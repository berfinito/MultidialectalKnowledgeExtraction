#!/usr/bin/env python
"""Summarize Sprint-4 results."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from mdke.utils.io import Paths, ensure_dirs, load_yaml

def count_rows(pq: Path) -> int | None:
    return int(pd.read_parquet(pq).shape[0]) if pq.exists() else None

def count_table(pq: Path, csv: Path) -> int | None:
    if pq.exists():
        return int(pd.read_parquet(pq).shape[0])
    if csv.exists():
        return int(pd.read_csv(csv).shape[0])
    return None

def run(cfg, tag_base: str = "normh"):
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)
    langs = ["tr", "kmr", "zza"]
    out = {"tag_base": tag_base, "langs": {}}

    for lang in langs:
        d: dict[str, object] = {}

        # Kaynak kırılımı (dataset-level)
        src_wiki = count_table(
            paths.processed / f"wiki_{lang}_{tag_base}.parquet",
            paths.processed / f"wiki_{lang}_{tag_base}.csv",
        )
        src_zaza = count_table(
            paths.processed / f"zazagorani_{lang}_{tag_base}.parquet",
            paths.processed / f"zazagorani_{lang}_{tag_base}.csv",
        )
        d["src_wiki"] = src_wiki
        d["src_zazagorani"] = src_zaza
        d["src_total"] = (src_wiki or 0) + (src_zaza or 0) if (src_wiki or src_zaza) is not None else None

        # Paragraf korpusları (birleşik akış)
        n_normh  = count_rows(paths.processed / f"text_corpus_{lang}_{tag_base}.parquet")
        n_clean  = count_rows(paths.processed / f"text_corpus_{lang}_{tag_base}_clean.parquet")
        n_nonav  = count_rows(paths.processed / f"text_corpus_{lang}_{tag_base}_clean_nonav.parquet")
        n_dedup  = count_rows(paths.processed / f"text_corpus_{lang}_{tag_base}_clean_nonav_dedup.parquet")
        d["n_normh"] = n_normh
        d["n_clean"] = n_clean
        d["n_nonav"] = n_nonav
        d["n_dedup"] = n_dedup

        # Cümle korpusu
        d["n_sentences"] = count_rows(paths.processed / f"text_sentences_{lang}_{tag_base}_clean_nonav.parquet")

        # Düşüşler
        def safe_diff(a, b):
            return (a - b) if (a is not None and b is not None) else None
        d["drop_postfilter"] = safe_diff(n_normh, n_clean)
        d["drop_dedup"]      = safe_diff(n_nonav, n_dedup)

        # Retention yüzdeleri
        def safe_pct(a, b):
            try:
                return round(100.0 * a / b, 2) if (a is not None and b is not None and b > 0) else None
            except Exception:
                return None
        d["retain_postfilter_pct"] = safe_pct(n_clean, n_normh)         # clean / normh
        d["retain_nonav_pct"]      = safe_pct(n_nonav, n_clean)         # nonav / clean
        d["retain_dedup_pct"]      = safe_pct(n_dedup, n_nonav)         # dedup / nonav
        # overall: dedup / src_total (varsa), yoksa dedup / normh
        overall_den = d["src_total"] if d["src_total"] else n_normh
        d["retain_overall_pct"]    = safe_pct(n_dedup, overall_den)

        # N-gram rapor yolları (öncelik dedup)
        rep = paths.reports / "ngrams"
        cand_uni = [
            rep / f"{lang}_{tag_base}_clean_nonav_dedup_unigram.txt",
            rep / f"{lang}_{tag_base}_clean_nonav_unigram.txt",
        ]
        d["ngrams_unigram"] = str(next((p for p in cand_uni if p.exists()), cand_uni[-1]))
        cand_bi = [
            rep / f"{lang}_{tag_base}_clean_nonav_dedup_bigram.txt",
            rep / f"{lang}_{tag_base}_clean_nonav_bigram.txt",
        ]
        d["ngrams_bigram"] = str(next((p for p in cand_bi if p.exists()), cand_bi[-1]))

        out["langs"][lang] = d

    out_dir = paths.reports
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "sprint-4-summary.json"
    out_json.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary -> {out_json}")
    return str(out_json)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--tag_base", type=str, default="normh")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    print(run(cfg, args.tag_base))

if __name__ == "__main__":
    main()