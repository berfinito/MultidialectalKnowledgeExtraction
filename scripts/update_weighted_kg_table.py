#!/usr/bin/env python
"""
Update the Weighted KG (PMI vs TF-IDF) summary table inside
`reports/analysis/thesis_tables.md` from the authoritative stats JSON files.

Usage:
  python scripts/update_weighted_kg_table.py --thesis reports/analysis/thesis_tables.md

It reads:
  reports/analysis/{lang}_kg_{set}_{weight}_stats.json
"""
from __future__ import annotations
import argparse
import re
import json
from pathlib import Path
from dataclasses import dataclass

LANGS = ["tr", "kmr", "zza"]
SETS = ["top15", "full"]
WEIGHTS = ["pmi", "tfidf"]

TABLE_HEADER = (
    "| Lang | Set    | Topics | RawPairs (T*10) | UniqueEdges | DupLoss% | "
    "TF-IDF Weight Range | PMI Avg |"
)

@dataclass
class Row:
    lang: str
    set: str
    topics: int
    raw_pairs: int
    unique_edges: int
    dup_loss: float
    tfidf_range: str
    pmi_avg: float

def read_stats(lang: str, set_: str, weight: str, base: Path) -> dict:
    p = base / f"{lang}_kg_{set_}_{weight}_stats.json"
    return json.loads(p.read_text(encoding="utf-8"))

def build_rows(stats_dir: Path) -> list[Row]:
    rows: list[Row] = []
    cache = {(l, s, w): read_stats(l, s, w, stats_dir) for l in LANGS for s in SETS for w in WEIGHTS}
    for lang in LANGS:
        for set_ in SETS:
            sp = cache[(lang, set_, "pmi")]
            st = cache[(lang, set_, "tfidf")]
            topics = sp["topics"]
            raw_pairs = topics * 10
            unique_edges = sp["edges"]
            dup_loss = 1 - (unique_edges / raw_pairs)
            tf_min, tf_max = st["min"], st["max"]
            tfidf_range = f"{tf_min:.2f}–{tf_max:.2f}" if abs(tf_min - tf_max) > 1e-9 else f"{tf_min:.3f}–{tf_max:.3f}"
            rows.append(Row(lang, set_, topics, raw_pairs, unique_edges, dup_loss, tfidf_range, sp["avg"]))
    return rows

def format_table(rows: list[Row]) -> str:
    lines = [TABLE_HEADER,
             "|------|--------|--------|-----------------|-------------|---------|---------------------|--------|"]
    for r in rows:
        lines.append(
            f"| {r.lang:<4} | {r.set:<6} | {r.topics:<6} | {r.raw_pairs:<15} | {r.unique_edges:<11} | "
            f"{r.dup_loss*100:4.1f}% | {r.tfidf_range:<19} | {r.pmi_avg:.2f}   |"
        )
    return "\n".join(lines)

def replace_section(md_path: Path, new_table: str) -> None:
    text = md_path.read_text(encoding="utf-8")
    anchor = "### Weighted KG (PMI vs TF-IDF) Kısa Özet"
    if anchor not in text:
        raise SystemExit("Anchor not found in thesis_tables.md")

    pattern = re.compile(
        r"(### Weighted KG \(PMI vs TF-IDF\) Kısa Özet\s*\n\n\| Lang .*?)(\n\n## |$)",
        re.DOTALL
    )

    def repl(match):
        before = match.group(1)
        # 'Notlar:' bloğunu bul
        notes_pattern = re.compile(r"Notlar:.*", re.DOTALL)
        notes_match = notes_pattern.search(before)
        notes_text = notes_match.group(0) if notes_match else ""
        header_line = "### Weighted KG (PMI vs TF-IDF) Kısa Özet"
        return f"{header_line}\n\n{new_table}\n\n{notes_text}\n\n## "

    new_text, n = pattern.subn(repl, text, count=1)
    if n == 0:
        raise SystemExit("Failed to substitute table block.")
    backup = md_path.with_suffix(".md.bak")
    backup.write_text(text, encoding="utf-8")
    md_path.write_text(new_text, encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--thesis", required=True, help="Path to thesis_tables.md")
    ap.add_argument("--stats-dir", default="reports/analysis", help="Directory with *_stats.json")
    args = ap.parse_args()
    rows = build_rows(Path(args.stats_dir))
    table_md = format_table(rows)
    replace_section(Path(args.thesis), table_md)
    print("Updated table with current stats.")

if __name__ == "__main__":
    main()