from typing import Any, Dict, Iterable, List

def normalize_value_inputs(arr):
    """Keep only ValueInput keys; cast numbers to floats; omit None."""
    norm = []
    for v in arr or []:
        vi = {}
        if v.get("scenario") is not None:
            vi["scenario"] = v["scenario"]
        if v.get("series") is not None:
            vi["series"] = [float(x) for x in v["series"]]
        if v.get("constant") is not None:
            vi["constant"] = float(v["constant"])
        norm.append(vi)
    return norm

def prune_nones(x):
    if isinstance(x, dict):
        return {k: prune_nones(v) for k, v in x.items() if v is not None}
    if isinstance(x, list):
        return [prune_nones(v) for v in x]
    return x

def pick_keys(d, allowed):
    # strips unknown keys that would cause GraphQL errors
    return {k: d[k] for k in allowed if k in d}

def _to_float(v: Any) -> float:
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        return float(v.strip().replace(",", "."))
    raise TypeError(f"Cannot convert {v!r} to float")

def normalize_point(p: Any) -> Dict[str, float]:
    """
    Normalize a single point to {'x': float, 'y': float}.
    Accepts:
      - dict with x/y (case-insensitive): {'x': 1, 'y': 2} or {'X': '1,0', 'Y': '2'}
      - list/tuple pair: [1, 2] / (1, 2)
      - object with attributes .x and .y
    """
    # dict-like
    if isinstance(p, dict):
        # direct or case-insensitive access
        def get(d, key):
            if key in d:
                return d[key]
            for k in d:
                if isinstance(k, str) and k.lower() == key.lower():
                    return d[k]
            raise KeyError(key)

        x = get(p, "x")
        y = get(p, "y")
        return {"x": _to_float(x), "y": _to_float(y)}

    # sequence pair
    if isinstance(p, (list, tuple)) and len(p) == 2:
        x, y = p
        return {"x": _to_float(x), "y": _to_float(y)}

    # object with attributes
    if hasattr(p, "x") and hasattr(p, "y"):
        return {"x": _to_float(getattr(p, "x")), "y": _to_float(getattr(p, "y"))}

    raise ValueError(f"Point must be {{x,y}}, [x,y], or have attributes x/y; got: {p!r}")

def normalize_points(points: Iterable[Any] | None) -> List[Dict[str, float]]:
    """Normalize a list/iterable of points using normalize_point()."""
    if points is None:
        return []
    return [normalize_point(p) for p in points]