
# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Union

def flatten_dict(obj: Any, prefix: str = "") -> Dict[str, Any]:
    """
    Aplana dict/list anidados a claves tipo 'kw.EP.common.campo1' o 'args[0]'
    """
    out: Dict[str, Any] = {}

    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            out.update(flatten_dict(v, p))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            p = f"{prefix}[{i}]"
            out.update(flatten_dict(v, p))
    else:
        out[prefix] = obj
    return out
