# 23.py — Config loader: parse INI-like lines and validate against schema
# Supports sections, key=value pairs, comments (# ...), and type validation
from typing import Dict, Any, List, Tuple, Optional

def parse_config(lines: List[str]) -> Dict[str, Dict[str, str]]:
    cfg: Dict[str, Dict[str, str]] = {}
    section = "DEFAULT"
    cfg[section] = {}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1].strip() or "DEFAULT"
            cfg.setdefault(section, {})
            continue
        if '=' in line:
            k, v = line.split('=', 1)
            cfg[section][k.strip()] = v.strip()
    return cfg

def _coerce(value: str, type_name: str) -> Any:
    if type_name == "int":
        return int(value)
    if type_name == "float":
        return float(value)
    if type_name == "bool":
        t = value.lower()
        if t in ("1", "true", "yes", "on"): return True
        if t in ("0", "false", "no", "off"): return False
        raise ValueError("invalid bool")
    return value

def validate_config(cfg: Dict[str, Dict[str, str]], schema: Dict[str, Dict[str, Tuple[str, bool]]]) -> Dict[str, Dict[str, Any]]:
    # schema: section -> key -> (type_name, required)
    out: Dict[str, Dict[str, Any]] = {}
    for sec, rules in schema.items():
        out[sec] = {}
        present = cfg.get(sec, {})
        for key, (typ, required) in rules.items():
            if key not in present:
                if required:
                    raise KeyError(f"missing required {sec}.{key}")
                else:
                    continue
            out[sec][key] = _coerce(present[key], typ)
    return out

def get(cfg: Dict[str, Dict[str, Any]], section: str, key: str, default: Optional[Any] = None) -> Any:
    return cfg.get(section, {}).get(key, default)
