
# -*- coding: utf-8 -*-
import json
from typing import Dict, Any, List, Tuple

def parse_wamp_array(text: str) -> Tuple[str, Dict[str, Any], List[Any], Dict[str, Any]]:
    """
    text es el payload de texto del frame WebSocket (un array JSON WAMP).
    Devuelve (topic_or_proc, args, kwargs) + 'msg_type'.
    Acepta formatos: [type, ... ,'MsgEP', [ {..} ] ] o similar.
    """
    arr = json.loads(text)
    msg_type = None
    topic = ""
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}

    # Heurística: buscar cadena tipo 'MsgEP' en posiciones típicas
    if isinstance(arr, list):
        for v in arr:
            if isinstance(v, str) and v.startswith("Msg"):
                msg_type = v
                break
        # args/kwargs posibles:
        for v in arr:
            if isinstance(v, list) and not args:
                args = v
            elif isinstance(v, dict) and not kwargs:
                kwargs = v

    if not msg_type:
        msg_type = "WAMP"

    # Si args es lista con un único dict, tratarlo como kwargs 'payload'
    if not kwargs and len(args) == 1 and isinstance(args[0], dict):
        kwargs = args[0]

    return msg_type, topic, args, kwargs
