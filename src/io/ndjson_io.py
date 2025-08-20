
# -*- coding: utf-8 -*-
import json
from typing import List, Dict

def read_ndjson(path: str) -> list:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                items.append(json.loads(line))
            except Exception:
                items.append({"raw": line})
    return items

def write_ndjson(path: str, records: List[Dict]):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            # guardamos raw si lo hay; si no, kwargs
            if r.get("raw"):
                payload = r["raw"]
            else:
                payload = r.get("kwargs", {})
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
