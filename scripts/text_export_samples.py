"""Export random samples from corpora for qualitative checks.

Inputs:
- data/processed/text_corpus_{lang}{_tag}.{parquet|csv}

Output:
- reports/samples/{lang}{_tag}_sample_{N}.csv

Notes:
- Samples with fixed seed (42) for reproducibility
- Falls back to head(0) if table is empty
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from mdke.utils.io import Paths, ensure_dirs, load_yaml

def run(cfg, lang: str, n: int = 100, tag: str = "") -> str:
    """Read corpus, sample N rows, and write CSV; returns output path."""
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)
    sfx = f"_{tag}" if tag else ""
    in_pq = paths.processed / f"text_corpus_{lang}{sfx}.parquet"
    in_csv = paths.processed / f"text_corpus_{lang}{sfx}.csv"
    if in_pq.exists():
        df = pd.read_parquet(in_pq)
    elif in_csv.exists():
        df = pd.read_csv(in_csv)
    else:
        raise FileNotFoundError(f"Missing corpus for {lang}: {in_pq} / {in_csv}")
    sample = df.sample(min(n, len(df)), random_state=42) if len(df) else df.head(0)
    out = paths.reports / f"samples/{lang}{sfx}_sample_{len(sample)}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(out, index=False)
    return str(out)

def main():
    """CLI wrapper: choose language, sample size, and optional tag."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--lang", type=str, required=True, choices=["tr","kmr","zza"])
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--tag", type=str, default="")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    print(run(cfg, args.lang, args.n, args.tag))

if __name__ == "__main__":
    main() 