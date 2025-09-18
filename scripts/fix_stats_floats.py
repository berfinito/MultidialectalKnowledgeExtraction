#!/usr/bin/env python
"""Normalize min/avg/max ranges in KG stats JSONs for numeric stability."""
from pathlib import Path
import json
import math

BASE = Path("reports/analysis")
EPS = 1e-12
NDIG = 12

def r(x): 
    return float(round(float(x), NDIG))

fixed = 0
for sf in BASE.glob("*_kg_*_*_stats.json"):
    data = json.loads(sf.read_text(encoding="utf-8"))
    # beklenen alanlar varsa düzelt
    if all(k in data for k in ("min","avg","max")):
        mn, av, mx = float(data["min"]), float(data["avg"]), float(data["max"])
        # yuvarla
        mn, av, mx = r(mn), r(av), r(mx)
        # clamp
        if av < mn - EPS: av = mn
        if av > mx + EPS: av = mx
        data["min"], data["avg"], data["max"] = mn, av, mx
        sf.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        fixed += 1

print(f"[fix-stats] normalized files: {fixed}")
