#!/usr/bin/env python
"""Generate Sprint-4 markdown report."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from mdke.utils.io import load_yaml

def fmt(x):
    return "NA" if x is None else str(x)

def fmt_pct(x):
    return "NA" if x is None else f"{x:.2f}%"

def run(cfg, summary_json: Path):
    data = json.loads(Path(summary_json).read_text(encoding="utf-8"))
    tag = data.get("tag_base", "normh")
    lines: list[str] = []
    lines.append(f"# Sprint 4 Summary ({tag})\n")

    for lang, d in data["langs"].items():
        lines.append(f"## {lang.upper()}")
        lines.append("")
        # Kaynak kırılımı
        if d.get("src_wiki") is not None or d.get("src_zazagorani") is not None:
            lines.append(f"- source wiki: {fmt(d.get('src_wiki'))}")
            lines.append(f"- source zazagorani: {fmt(d.get('src_zazagorani'))}")
            lines.append(f"- source total: {fmt(d.get('src_total'))}")
        # Birleşik korpus akışı
        lines.append(f"- paragraphs (normh): {fmt(d.get('n_normh'))}")
        lines.append(f"- post-filter clean: {fmt(d.get('n_clean'))} (drop={fmt(d.get('drop_postfilter'))}, retain={fmt_pct(d.get('retain_postfilter_pct'))})")
        lines.append(f"- section nonav: {fmt(d.get('n_nonav'))} (retain={fmt_pct(d.get('retain_nonav_pct'))})")
        lines.append(f"- dedup: {fmt(d.get('n_dedup'))} (drop={fmt(d.get('drop_dedup'))}, retain={fmt_pct(d.get('retain_dedup_pct'))})")
        lines.append(f"- sentences: {fmt(d.get('n_sentences'))}")
        lines.append(f"- overall retention: {fmt_pct(d.get('retain_overall_pct'))}")
        lines.append(f"- n-grams (uni): {fmt(d.get('ngrams_unigram'))}")
        lines.append(f"- n-grams (bi):  {fmt(d.get('ngrams_bigram'))}")
        lines.append("")

    out_md = Path("reports") / "sprint-4-summary.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"markdown -> {out_md}")
    return str(out_md)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--json", type=Path, default=Path("reports/sprint-4-summary.json"))
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    print(run(cfg, args.json))

if __name__ == "__main__":
    main()