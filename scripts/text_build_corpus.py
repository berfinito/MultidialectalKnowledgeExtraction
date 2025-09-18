"""Ingest and build cleaned text corpora (wiki + Zazagorani) for a language.

Inputs:
- data/processed/wiki_{lang}{_tag}.{parquet|csv}
- data/processed/zazagorani_{lang}{_tag}.{parquet|csv} (if applicable)

Output:
- data/processed/text_corpus_{lang}{_tag}.{parquet|csv}

Notes:
- Merges sources, applies light normalization/column unification, and dedup earlier in pipeline
- Logging via mdke.utils.io.get_logger
"""
from __future__ import annotations
import argparse
from pathlib import Path

import pandas as pd

from mdke.utils.io import Paths, ensure_dirs, load_yaml, get_logger

def load_table_or_csv(path_parquet: Path, path_csv: Path) -> pd.DataFrame:
    """Load a table from parquet or CSV; return empty DataFrame if missing."""
    if path_parquet.exists():
        return pd.read_parquet(path_parquet)
    if path_csv.exists():
        return pd.read_csv(path_csv)
    return pd.DataFrame([])

def run(cfg, lang: str, tag: str = ""):
    """Build the combined corpus for a language and write to processed/."""
    logger = get_logger(f"text_build_{lang}")
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)

    tag_sfx = f"_{tag}" if tag else ""

    wiki_tbl = load_table_or_csv(
        paths.processed / f"wiki_{lang}{tag_sfx}.parquet",
        paths.processed / f"wiki_{lang}{tag_sfx}.csv"
    )
    zaza_tbl = pd.DataFrame([])
    if lang == "zza":
        zaza_tbl = load_table_or_csv(
            paths.processed / f"zazagorani_{lang}{tag_sfx}.parquet",
            paths.processed / f"zazagorani_{lang}{tag_sfx}.csv"
        )

    cols = ["doc_id","lang","source","text","text_norm","n_chars","n_tokens"]
    frames = []
    if not wiki_tbl.empty:
        keep = [c for c in cols if c in wiki_tbl.columns] + [c for c in ["page_id","title"] if c in wiki_tbl.columns]
        frames.append(wiki_tbl[keep])
    if not zaza_tbl.empty:
        keep = [c for c in cols if c in zaza_tbl.columns]
        frames.append(zaza_tbl[keep])

    if not frames:
        logger.warning("No inputs found for %s", lang)
        return {"n": 0, "out": None}

    corpus = pd.concat(frames, ignore_index=True)
    corpus["lang"] = lang
    corpus.drop_duplicates(subset=["text"], inplace=True)

    out_parquet = paths.processed / f"text_corpus_{lang}{tag_sfx}.parquet"
    out_csv = paths.processed / f"text_corpus_{lang}{tag_sfx}.csv"
    try:
        out_parquet.parent.mkdir(parents=True, exist_ok=True)
        corpus.to_parquet(out_parquet, index=False)
        written = str(out_parquet)
    except Exception:
        corpus.to_csv(out_csv, index=False)
        written = str(out_csv)

    n = len(corpus)
    n_tokens = int(corpus["n_tokens"].sum()) if "n_tokens" in corpus.columns else None
    logger.info("Built corpus %s: n=%d, tokens≈%s -> %s", lang, n, n_tokens, written)
    return {"n": n, "out": written}

def main():
    """CLI wrapper: choose language and optional tag, then build corpus."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--lang", type=str, required=True, choices=["tr","kmr","zza"])
    ap.add_argument("--tag", type=str, default="")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    res = run(cfg, args.lang, args.tag)
    print(res)

if __name__ == "__main__":
    main() 