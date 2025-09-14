from __future__ import annotations
import argparse, re
from pathlib import Path
import pandas as pd
from mdke.utils.io import Paths, ensure_dirs, load_yaml
from mdke.utils.textnorm import normalize_text

HEADINGS = {
    "tr": [
        "dış bağlantılar", "ayrıca bakınız", "kaynakça", "notlar",
        "bibliyografya", "galeri", "ilgili sayfalar"
    ],
    "kmr": [
        "çavkanî", "çavkanîyan", "girêdanên derve", "girêdanên derveyî",
        "lîste", "lîsteyê", "binihêrin", "biguherîne"
    ],
    "zza": [
        "kaynak", "kaynakê", "cı geyrê", "cı geyri", "seba zêde",
        "lıste", "liste", "galeri"
    ],
}

def build_pattern(lang: str):
    items = [re.escape(h) for h in HEADINGS.get(lang, [])]
    if not items:
        return None
    # Başlık satırı: tek başına/başında/sonunda iki nokta opsiyonel
    pat = r"^(?:\s*(?:%s)\s*:?\s*)$" % ("|".join(items))
    return re.compile(pat, flags=re.IGNORECASE)

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
    series = df[col].fillna("")
    pat = build_pattern(lang)
    series_n = series.map(lambda x: normalize_text(x, lang))
    mask = series_n.str.match(pat) if pat is not None else pd.Series(False, index=df.index)
    out = df.loc[~mask].reset_index(drop=True)
    out_pq = paths.processed / f"text_corpus_{lang}{sfx}_nonav.parquet"
    out.to_parquet(out_pq, index=False)
    print(f"[{lang}] section-filter: input={len(df)} dropped={int(mask.sum())} kept={len(out)} -> {out_pq}")
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