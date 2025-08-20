
# -*- coding: utf-8 -*-
import os, subprocess, tempfile, re, json
from typing import List, Dict, Optional
from .utils import hex_to_bytes, maybe_inflate, largest_json_in_text
from .wamp_parser import parse_wamp_array

TSHARK = os.environ.get("TSHARK", "tshark")

class Filters:
    def __init__(self, src_ip="", dst_ip="", src_port="", dst_port="", mode="AUTO"):
        self.src_ip = src_ip.strip()
        self.dst_ip = dst_ip.strip()
        self.src_port = src_port.strip()
        self.dst_port = dst_port.strip()
        self.mode = mode.upper()  # AUTO | WAMP | TCPJSON

    def to_display(self):
        return f"src={self.src_ip or '*'} dst={self.dst_ip or '*'} sport={self.src_port or '*'} dport={self.dst_port or '*'} mode={self.mode}"

def _ip_ok(ip: str, want: str) -> bool:
    return (not want) or ip == want

def _port_ok(port: str, want: str) -> bool:
    return (not want) or port == want

def run_tshark_fields(pcap: str, fields: List[str], display_filter: str) -> List[str]:
    cmd = [
        TSHARK, "-r", pcap,
        "-o", "tcp.desegment_tcp_streams:true",
        "-T", "fields", "-E", "separator=\t", "-E", "header=n"
    ]
    for f in fields:
        cmd += ["-e", f]
    if display_filter:
        cmd += ["-Y", display_filter]
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return out.decode("utf-8", errors="ignore").splitlines()

def extract_websocket_messages(pcap: str, flt: Filters) -> List[Dict]:
    # Extraemos frames WS text/continuations
    fields = [
        "frame.time_epoch","ip.src","ip.dst","tcp.stream",
        "websocket.opcode","websocket.fin","websocket.mask","websocket.masking_key",
        "websocket.payload"
    ]
    df = "websocket && (websocket.opcode==1 || websocket.opcode==0)"
    rows = run_tshark_fields(pcap, fields, df)
    # Reensamblado por stream/opcode+fin
    buffers = {}
    messages = []

    for line in rows:
        cols = line.split("\t")
        if len(cols) < len(fields):
            continue
        epoch, src, dst, stream, opcode, fin, mask, mkey, payload_hex = cols
        if not _ip_ok(src, flt.src_ip) or not _ip_ok(dst, flt.dst_ip):
            continue
        # convert payload
        payload = b""
        try:
            payload = hex_to_bytes(payload_hex)
        except Exception:
            payload = b""
        # mask
        if mask == "1" and mkey:
            k = bytes.fromhex(mkey.replace(":",""))
            payload = bytes(b ^ k[i % 4] for i, b in enumerate(payload))
        # acumula
        buf = buffers.setdefault(stream, bytearray())
        if opcode == "1":
            buf.clear()
        if opcode in ("1","0"):
            buf.extend(payload)
        if fin == "1" and (opcode in ("1","0")):
            data = bytes(buf)
            data = maybe_inflate(data)
            text = data.decode("utf-8", errors="ignore")
            # puede ser array WAMP o JSON directo
            json_text = text.strip()
            try:
                msg_type, topic, args, kwargs = parse_wamp_array(json_text)
            except Exception:
                # intentar mayor JSON
                j = largest_json_in_text(text)
                msg_type, topic, args, kwargs = ("WAMP", "", [], {})
                if j:
                    try:
                        kwargs = json.loads(j)
                    except Exception:
                        kwargs = {"raw_text": j}
            messages.append({
                "time": "", "ms": "", "epoch": float(epoch),
                "stream": stream, "src": src, "dst": dst,
                "opcode": msg_type, "topic": topic, "type": _root_key(kwargs),
                "args": args, "kwargs": kwargs, "raw": json_text
            })
            buf.clear()
    return messages

def _root_key(d: Dict) -> str:
    if isinstance(d, dict) and d:
        return next(iter(d.keys()))
    return ""

def extract_tcpjson_messages(pcap: str, flt: Filters) -> List[Dict]:
    # Campos TCP (usamos payload para reensamblar nosotros por stream)
    fields = [
        "frame.time_epoch","ip.src","ip.dst","tcp.stream","tcp.payload"
    ]
    rows = run_tshark_fields(pcap, fields, "tcp")
    buffers: Dict[str, bytearray] = {}
    times: Dict[str, float] = {}
    msgs: List[Dict] = []

    for line in rows:
        cols = line.split("\t")
        if len(cols) < 5: 
            continue
        epoch, src, dst, stream, payload_hex = cols
        if not (_ip_ok(src, flt.src_ip) and _ip_ok(dst, flt.dst_ip)):
            continue
        try:
            data = hex_to_bytes(payload_hex)
        except Exception:
            data = b""
        if not data:
            continue
        buf = buffers.setdefault(stream, bytearray())
        buf.extend(data)
        if stream not in times:
            times[stream] = float(epoch)

        # Buscar JSON en el buffer
        text = buf.decode("utf-8", errors="ignore")
        while True:
            j = largest_json_in_text(text)
            if not j:
                break
            # Emitir y recortar desde el final del JSON
            end_idx = text.find(j) + len(j)
            remaining = text[end_idx:]
            # actualizar buffer con lo no consumido
            buf[:] = remaining.encode("utf-8", errors="ignore")
            # construir record
            kwargs = {}
            try:
                kwargs = json.loads(j)
            except Exception:
                kwargs = {"raw_text": j}
            epoch0 = times.get(stream, float(epoch))
            msgs.append({
                "time": "", "ms": "", "epoch": epoch0,
                "stream": stream, "src": src, "dst": dst,
                "opcode": "TCPJSON", "topic": "", "type": _root_key(kwargs),
                "args": [], "kwargs": kwargs, "raw": j
            })
            text = remaining
    return msgs

def extract_messages(pcap: str, flt: Filters) -> List[Dict]:
    mode = flt.mode
    msgs: List[Dict] = []
    if mode in ("AUTO","WAMP"):
        msgs.extend(extract_websocket_messages(pcap, flt))
    if mode in ("AUTO","TCPJSON"):
        msgs.extend(extract_tcpjson_messages(pcap, flt))

    # Ordena por epoch y agrega time/ms formateados
    msgs.sort(key=lambda r: r.get("epoch", 0.0))
    for m in msgs:
        import datetime as _dt
        t = _dt.datetime.utcfromtimestamp(float(m["epoch"]))
        m["time"] = t.strftime("%H:%M:%S")
        m["ms"] = f"{t.microsecond:06d}"
        # normaliza type si viene algo como MsgEP ya detectado en opcode
        if not m.get("type") and isinstance(m.get("kwargs"), dict):
            m["type"] = _root_key(m["kwargs"])
    return msgs
