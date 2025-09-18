#!/usr/bin/env python
"""
Summarize Sprint-5 results.

This is a generic aggregator that scans reports/analysis and related folders
to build a JSON inventory + quick stats for key artefacts produced in Sprint-5
(e.g., cross-modal comparisons, KG exports, case studies).

Inputs (optional, discovered if present):
- reports/analysis/keyword_overlap.md
- reports/analysis/keyword_coverage.md
- reports/analysis/centrality/summary.md
- reports/analysis/case*.md
- reports/topics/* and reports/keywords/*
- reports/asr_* (index/summary) if any

Output:
- reports/sprint-5-summary.json
"""
from __future__ import annotations
import argparse, json, os
from datetime import datetime
from pathlib import Path

LANGS = ["tr", "kmr", "zza"]

def file_info(p: Path) -> dict:
    return {
        "exists": p.exists(),
        "size_bytes": p.stat().st_size if p.exists() else None,
        "path": str(p),
    }

def count_lines(p: Path) -> int | None:
    if not p.exists():
        return None
    try:
        return len(p.read_text(encoding="utf-8").splitlines())
    except Exception:
        return None

def scan_topics_keywords(reports_dir: Path) -> dict:
    td = reports_dir / "topics"
    kd = reports_dir / "keywords"
    res = {"topics": {}, "keywords": {}}
    if td.exists():
        for lang in LANGS:
            res["topics"][lang] = {
                "topics_json": file_info(td / f"{lang}_bertopic_topics.json"),
                "docs_txt": file_info(td / f"{lang}_bertopic_docs_text.txt"),
                "docs_cv_txt": file_info(td / f"{lang}_bertopic_docs_cv.txt"),
                "docs_both_txt": file_info(td / f"{lang}_bertopic_docs_both.txt"),
            }
    if kd.exists():
        for lang in LANGS:
            # variants and methods may vary by project; include common ones if present
            lang_items = {}
            for method in ["yake","keybert"]:
                m = {}
                for variant in ["text","cv","both"]:
                    p = kd / f"{lang}_{method}_{variant}.json"
                    if p.exists():
                        try:
                            data = json.loads(p.read_text(encoding="utf-8"))
                            m[variant] = {"count": len(data), **file_info(p)}
                        except Exception:
                            m[variant] = {"count": None, **file_info(p)}
                if m:
                    lang_items[method] = m
            if lang_items:
                res["keywords"][lang] = lang_items
    return res

def run(root: Path) -> dict:
    reports = root / "reports"
    analysis = reports / "analysis"

    out = {
        "_generated_at": datetime.utcnow().isoformat() + "Z",
        "artefacts": {},
    }
    # Key analysis artefacts
    out["artefacts"]["keyword_overlap_md"] = {
        **file_info(analysis / "keyword_overlap.md"),
        "n_lines": count_lines(analysis / "keyword_overlap.md"),
    }
    out["artefacts"]["keyword_coverage_md"] = {
        **file_info(analysis / "keyword_coverage.md"),
        "n_lines": count_lines(analysis / "keyword_coverage.md"),
    }
    out["artefacts"]["centrality_summary_md"] = {
        **file_info(analysis / "centrality" / "summary.md"),
        "n_lines": count_lines(analysis / "centrality" / "summary.md"),
    }
    # Case studies if any
    cases = {}
    for p in sorted((analysis).glob("case*.md")):
        cases[p.name] = {**file_info(p), "n_lines": count_lines(p)}
    out["artefacts"]["cases"] = cases
    # Topics/keywords inventory
    out["artefacts"]["topics_keywords"] = scan_topics_keywords(reports)

    # KG exports and plots if present
    kg_exports_dir = analysis / "exports"
    if kg_exports_dir.exists():
        exps = {}
        for p in sorted(kg_exports_dir.glob("*.gexf")) + sorted(kg_exports_dir.glob("*.graphml")):
            exps[p.name] = file_info(p)
        out["artefacts"]["kg_exports"] = exps

    # Save
    out_path = reports / "sprint-5-summary.json"
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