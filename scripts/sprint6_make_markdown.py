#!/usr/bin/env python
"""
Generate Sprint-6 markdown report from sprint-6-summary.json.

Output:
- reports/sprint-6-summary.md
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

def run(summary_json: Path) -> str:
    data = json.loads(Path(summary_json).read_text(encoding="utf-8"))
    lines = ["# Sprint-6 Summary", ""]
    gen = data.get("_generated_at")
    if gen: lines += [f"_generated_at: {gen}_", ""]

    pm = data.get("project_map")
    lines += [f"- PROJECT_MAP.md: {'exists' if pm else 'MISSING'}"]
    env = data.get("env_snapshot", {})
    lines += [
        f"- env_snapshot.json: {'exists' if env.get('env_snapshot_json') else 'MISSING'}",
        f"- env_freeze.txt: {'exists' if env.get('env_freeze_txt') else 'MISSING'}",
        ""
    ]
    th = data.get("thesis_tables")
    lines += [f"- thesis_tables.md: {'exists' if th else 'MISSING'}", ""]

    ds = data.get("docstrings", {})
    lines += [
        "## Docstrings",
        f"- files total: {ds.get('total')}",
        f"- with docstring: {ds.get('with_doc')}",
        f"- missing: {ds.get('missing')}",
        ""
    ]
    missing_list = ds.get("missing_list") or []
    if missing_list:
        lines.append("### Missing Docstrings (first 20)")
        for p in missing_list[:20]:
            lines.append(f"- {p}")
        if len(missing_list) > 20:
            lines.append(f"... (+{len(missing_list)-20} more)")
        lines.append("")

    dep = data.get("deprecated_present") or []
    lines += ["## Deprecated Scripts Present" if dep else "## Deprecated Scripts Present",]
    if not dep:
        lines += ["- none", ""]
    else:
        lines += [*(f"- {p}" for p in dep), ""]

    out_md = Path("reports") / "sprint-6-summary.md"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")
    return str(out_md)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=Path("reports/sprint-6-summary.json"))
    args = ap.parse_args()
    print(run(args.json))

if __name__ == "__main__":
    main()