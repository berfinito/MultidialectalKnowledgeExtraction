#!/usr/bin/env python
"""
Summarize Sprint-6 (documentation & packaging).

Focus:
- Docstring coverage across scripts and src/mdke
- Deprecated scripts presence
- PROJECT_MAP existence
- Env snapshot presence
- Thesis tables presence

Output:
- reports/sprint-6-summary.json
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from datetime import datetime

ROOTS = ["scripts", "src/mdke"]
DEPRECATED_HINTS = {"ct2_smoketest.py", "kg_centrality.py", "trim_reps.py"}

def has_module_docstring(path: Path) -> bool:
    try:
        txt = path.read_text(encoding="utf-8")
    except Exception:
        return False
    m = re.match(r'\s*(?:#.*\n)*\s*(?P<q>["\']{3})', txt)
    return bool(m)

def summarize_docstrings(root: Path) -> dict:
    files = []
    for base in ROOTS:
        for p in (root / base).rglob("*.py"):
            if p.name == "__init__.py":  # allow empty docstring
                continue
            files.append(p)
    covered = [str(p) for p in files if has_module_docstring(p)]
    missing = [str(p) for p in files if not has_module_docstring(p)]
    return {"total": len(files), "with_doc": len(covered), "missing": len(missing), "missing_list": missing}

def run(root: Path) -> dict:
    reports = root / "reports"
    out = {"_generated_at": datetime.utcnow().isoformat() + "Z"}
    out["project_map"] = (reports / "docs" / "PROJECT_MAP.md").exists()
    out["env_snapshot"] = {
        "env_snapshot_json": (reports / "env_snapshot.json").exists(),
        "env_freeze_txt": (reports / "env_freeze.txt").exists(),
    }
    out["thesis_tables"] = (reports / "analysis" / "thesis_tables.md").exists()
    out["docstrings"] = summarize_docstrings(root)
    deprecated = []
    for name in DEPRECATED_HINTS:
        p = (root / "scripts" / name)
        if p.exists():
            deprecated.append(str(p))
    out["deprecated_present"] = deprecated
    out_path = reports / "sprint-6-summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"out_json": str(out_path)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    args = ap.parse_args()
    res = run(args.root.resolve())
    print(f"Summary JSON written to: {res['out_json']}")

if __name__ == "__main__":
    main()