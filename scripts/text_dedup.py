from __future__ import annotations
import argparse, hashlib
from pathlib import Path
import pandas as pd
from mdke.utils.io import Paths, ensure_dirs, load_yaml
from mdke.utils.textnorm import normalize_text

def normhash(s: str, lang: str) -> str:
    t = normalize_text(s or "", lang)
    t = " ".join(t.split())
    return hashlib.sha1(t.encode("utf-8")).hexdigest()

def run(cfg, lang: str, tag: str):
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)
    sfx = f"_{tag}" if tag else ""
    in_pq = paths.processed / f"text_corpus_{lang}{sfx}.parquet"
    if not in_pq.exists():
        raise FileNotFoundError(in_pq)
    df = pd.read_parquet(in_pq)
    col = "text_norm" if "text_norm" in df.columns else "text"
    h = df[col].fillna("").map(lambda x: normhash(x, lang))
    kept = df.loc[~h.duplicated()].reset_index(drop=True)
    out_pq = paths.processed / f"text_corpus_{lang}{sfx}_dedup.parquet"
    kept.to_parquet(out_pq, index=False)
    print(f"[{lang}] dedup: input={len(df)} dropped={len(df)-len(kept)} kept={len(kept)} -> {out_pq}")
    return str(out_pq)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--lang", required=True, choices=["tr","kmr","zza"])
    ap.add_argument("--tag", default="clean", help="Kaynak sonek (default: clean)")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    print(run(cfg, args.lang, args.tag))

if __name__ == "__main__":
    main()