
# -*- coding: utf-8 -*-
import re, json, zlib
from typing import Optional

HEX_RX = re.compile(r'^(?:[0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2})*)$')

def hex_to_bytes(hexstr: str) -> bytes:
    if not hexstr:
        return b""
    hs = hexstr.replace(":", "").replace(" ", "").strip()
    if len(hs) % 2 != 0:
        raise ValueError("odd length hex")
    return bytes.fromhex(hs)

def largest_json_in_text(s: str) -> Optional[str]:
    """Devuelve el objeto JSON balanceado más largo dentro de s."""
    if not s:
        return None
    best = None
    best_len = 0
    n = len(s)
    i = 0
    while i < n:
        start = s.find("{", i)
        if start < 0: break
        depth = 0; j = start
        while j < n:
            ch = s[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    ln = j - start + 1
                    if ln > best_len:
                        best_len = ln
                        best = s[start:start+ln]
                    j += 1
                    break
            j += 1
        i = max(j, start+1)
    return best

def maybe_inflate(raw: bytes) -> bytes:
    """Intenta descomprimir DEFLATE raw o zlib. Si falla, devuelve raw."""
    if not raw:
        return raw
    try:
        # zlib
        return zlib.decompress(raw)
    except:
        pass
    try:
        # raw DEFLATE necesita cabecera/cola zlib vacía
        return zlib.decompress(raw + b"\x00\x00\xff\xff", -zlib.MAX_WBITS)
    except:
        return raw
