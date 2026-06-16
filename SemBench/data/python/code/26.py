# 26.py — CSV parsing and group-by aggregation without external libs
from typing import List, Dict, Tuple, Callable, Any, Iterable

def parse_csv(text: str, sep: str = ',') -> List[List[str]]:
    # very simple parser: handles quoted fields and escaped quotes
    rows: List[List[str]] = []
    field = ''
    row: List[str] = []
    in_quotes = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_quotes:
            if ch == '"':
                if i + 1 < len(text) and text[i+1] == '"':
                    field += '"'
                    i += 1
                else:
                    in_quotes = False
            else:
                field += ch
        else:
            if ch == '"':
                in_quotes = True
            elif ch == sep:
                row.append(field); field = ''
            elif ch == '\n':
                row.append(field); field = ''
                rows.append(row); row = []
            else:
                field += ch
        i += 1
    # flush pending
    if field or row:
        row.append(field); rows.append(row)
    return rows

def groupby_agg(rows: List[List[str]], key_idx: int, val_idx: int, agg: Callable[[Iterable[float]], float]) -> Dict[str, float]:
    groups: Dict[str, List[float]] = {}
    for r in rows:
        if len(r) <= max(key_idx, val_idx):
            continue
        key = r[key_idx]
        try:
            v = float(r[val_idx])
        except ValueError:
            continue
        groups.setdefault(key, []).append(v)
    return {k: agg(vs) for k, vs in groups.items()}

def mean(xs: Iterable[float]) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0
