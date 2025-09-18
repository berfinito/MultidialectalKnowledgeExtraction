#!/usr/bin/env python
"""
Generate Sprint-5 markdown report from sprint-5-summary.json.

Input:
- reports/sprint-5-summary.json (created by sprint5_summarize.py)

Output:
- reports/sprint-5-summary.md
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

def fmt_bool(b):
    return "yes" if b else "no"

def run(summary_json: Path) -> str:
    data = json.loads(Path(summary_json).read_text(encoding="utf-8"))
    lines = []
    lines.append(f"# Sprint-5 Summary\n")
    gen = data.get("_generated_at")
    if gen:
        lines.append(f"_generated_at: {gen}_\n")

    arts = data.get("artefacts", {})
    # Keyword overlap/coverage
    ov = arts.get("keyword_overlap_md", {})
    cvg = arts.get("keyword_coverage_md", {})
    lines += [
        "## Keyword Analizleri",
        f"- overlap.md exists: {fmt_bool(ov.get('exists'))}  lines: {ov.get('n_lines')}",
        f"- coverage.md exists: {fmt_bool(cvg.get('exists'))}  lines: {cvg.get('n_lines')}",
        "",
    ]
    # Centrality summary
    cen = arts.get("centrality_summary_md", {})
    lines += [
        "## KG Centrality",
        f"- centrality/summary.md exists: {fmt_bool(cen.get('exists'))}  lines: {cen.get('n_lines')}",
        "",
    ]
    # Cases
    cases = arts.get("cases", {})
    lines.append("## Case Studies")
    if not cases:
        lines.append("- none")
    else:
        for name, meta in cases.items():
            lines.append(f"- {name}  exists: {fmt_bool(meta.get('exists'))}  lines: {meta.get('n_lines')}")
    lines.append("")

    # Topics/Keywords inventory
    tk = arts.get("topics_keywords", {})
    lines.append("## Topics & Keywords")
    topics = tk.get("topics", {})
    if topics:
        lines.append("### Topics")
        for lang, meta in topics.items():
            lines.append(f"- {lang}:")
            for key, info in meta.items():
                lines.append(f"  - {key}: exists={fmt_bool(info.get('exists'))} size={info.get('size_bytes')}")
    keywords = tk.get("keywords", {})
    if keywords:
        lines.append("### Keywords")
        for lang, methods in keywords.items():
            lines.append(f"- {lang}:")
            for method, variants in methods.items():
                parts = ", ".join(f"{var}={meta.get('count')}" for var, meta in variants.items())
                lines.append(f"  - {method}: {parts}")
    lines.append("")

    # KG Exports
    exps = arts.get("kg_exports", {})
    lines.append("## KG Exports")
    if not exps:
        lines.append("- none")
    else:
        for name, meta in exps.items():
            lines.append(f"- {name}  exists: {fmt_bool(meta.get('exists'))}  size: {meta.get('size_bytes')}")
    lines.append("")

    out_md = Path("reports") / "sprint-5-summary.md"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")
    return str(out_md)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=Path("reports/sprint-5-summary.json"))
    args = ap.parse_args()
    print(run(args.json))

if __name__ == "__main__":
    main()