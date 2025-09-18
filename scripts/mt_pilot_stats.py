#!/usr/bin/env python
"""Aggregate MT pilot stats; ready for case3_original_vs_mt.md."""
import argparse, statistics as st
from pathlib import Path

def load(p): return [l.rstrip("\n") for l in Path(p).read_text(encoding="utf-8").splitlines()]

def stats(lines):
    toks = [len(l.split()) for l in lines if l.strip()]
    return {
        "n": len(lines),
        "avg_tokens": sum(toks)/len(toks),
        "median_tokens": st.median(toks),
        "p95_tokens": sorted(toks)[int(0.95*len(toks))-1],
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--hyp", required=True)
    ap.add_argument("--out", default="reports/analysis/mt_pilot_stats.md")
    ap.add_argument("--label", default="kmr")
    args = ap.parse_args()
    src = load(args.src); hyp = load(args.hyp)
    assert len(src)==len(hyp), "satır sayısı tutmuyor"
    s_src = stats(src); s_hyp = stats(hyp)
    lines = [
        f"# MT Pilot Stats ({args.label})",
        "",
        f"Toplam satır: {s_src['n']}",
        "",
        "| Set | AvgTok | Median | P95 |",
        "|-----|--------|--------|-----|",
        f"| src | {s_src['avg_tokens']:.2f} | {s_src['median_tokens']:.1f} | {s_src['p95_tokens']} |",
        f"| hyp | {s_hyp['avg_tokens']:.2f} | {s_hyp['median_tokens']:.1f} | {s_hyp['p95_tokens']} |",
        "",
        "_Not: Referans yok; bu sadece uzunluk / dağılım kontrolü._"
    ]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"[mt-stats] -> {args.out}")

if __name__ == "__main__":
    main()