#!/usr/bin/env python
"""Generate Sprint-3 markdown report."""
import json
from pathlib import Path

def read_top(p: Path, k=10):
    if not p.exists():
        return []
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()][:k]

def main():
    root = Path(".").resolve()
    reports = root / "reports"
    data = json.loads((reports / "sprint-3-summary.json").read_text(encoding="utf-8"))
    md = ["# Sprint-3 Summary", ""]
    gen = data.get("_generated_at"); 
    if gen: md += [f"_generated_at: {gen}_", ""]

    for lang in ("tr","kmr","zza"):
        obj = data.get(lang, {})
        inp, drp, kep = obj.get("input"), obj.get("dropped"), obj.get("kept")
        md.append(f"## {lang.upper()}")
        md.append(f"- input: {inp}  dropped: {drp}  kept: {kep}  clean: {obj.get('has_clean')}")
        # Kaynak kırılımını yaz
        src = obj.get("sources") or {}
        if src:
            parts = [f"{k}: {v}" for k, v in src.items()]
            md.append(f"- sources: " + ", ".join(parts))
        # n-gram örnekleri
        uni_path = obj.get("ngrams", {}).get("unigram")
        bi_path = obj.get("ngrams", {}).get("bigram")
        if uni_path:
            topu = read_top(root / uni_path, 10)
            if topu: md += ["", "Top unigramlar:"] + [f"- {ln}" for ln in topu]
        if bi_path:
            topb = read_top(root / bi_path, 10)
            if topb: md += ["", "Top bigramlar:"] + [f"- {ln}" for ln in topb]
        md.append("")

    (reports / "sprint-3-summary.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Sprint-3 markdown saved to {reports / 'sprint-3-summary.md'}")

if __name__ == "__main__":
    main()