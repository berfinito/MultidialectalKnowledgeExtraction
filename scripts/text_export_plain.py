"""Export final sentences/documents into plain TXT for sampling/inspection.

Inputs:
- data/processed/text_corpus_{lang}_{tag}.parquet or .csv

Outputs:
- reports/exports/{lang}_{tag}.txt

Notes:
- Chooses the most specific available column in ['sentence', 'text_norm', 'text']
- Useful for manual reading, lexicon building, or external tools
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import pandas as pd
from mdke.utils.io import Paths, ensure_dirs, load_yaml

LANGS = ["tr", "kmr", "zza"]

def choose_col(df: pd.DataFrame) -> str:
    """Pick the best text column available in order of preference."""
    for c in ["sentence", "text_norm", "text"]:
        if c in df.columns:
            return c
    raise ValueError(f"Uygun kolon bulunamadı. Var olan kolonlar: {list(df.columns)}")

def run(cfg_path: Path, use_final: bool = True, tag_base: str = "normh_clean_nonav"):
    """Batch export TXT per language based on final tag pipeline."""
    cfg = load_yaml(cfg_path)
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)
    outdir = paths.reports / "exports"
    outdir.mkdir(parents=True, exist_ok=True)

    for lang in LANGS:
        if use_final:
            src = paths.processed / f"text_sentences_{lang}_final.parquet"
            label = "final"
            if not src.exists():
                src = paths.processed / f"text_sentences_{lang}_{tag_base}.parquet"
                label = tag_base
        else:
            src = paths.processed / f"text_sentences_{lang}_{tag_base}.parquet"
            label = tag_base

        if not src.exists():
            print(f"[skip] kaynak yok: {src}")
            continue

        df = pd.read_parquet(src)
        col = choose_col(df)
        s = df[col].astype(str).map(str.strip)
        s = s[s.str.len() > 0]

        s = s.str.replace(r"'{2,}", "", regex=True)

        s = s.str.replace(r"\s+([,;:.!?])", r"\1", regex=True)
        s = s.str.replace(r"\(\s+\)", "", regex=True)
        s = s.str.replace(r"\(\s+", "(", regex=True)
        s = s.str.replace(r"\s+\)", ")", regex=True)
        s = s.str.replace(r",\s*,", ", ", regex=True)
        s = s.str.replace(r"\s{2,}", " ", regex=True)
        s = s.str.replace(r",\s*\)", ")", regex=True)
        s = s.str.strip()

        out = outdir / f"sentences_{lang}_{label}.txt"
        out.write_text("\n".join(s.tolist()), encoding="utf-8")
        print(f"[export] {src.name} -> {out}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--no_final", action="store_true", help="final yerine tag_base kullan")
    ap.add_argument("--tag_base", type=str, default="normh_clean_nonav")
    args = ap.parse_args()
    run(args.config, use_final=not args.no_final, tag_base=args.tag_base)