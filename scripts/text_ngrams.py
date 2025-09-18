"""Compute and export uni/bi-gram frequency lists for QC.

Inputs:
- data/processed/text_corpus_{lang}{_tag}.{parquet|csv}

Outputs:
- reports/ngrams/{lang}{_tag}_uni.csv
- reports/ngrams/{lang}{_tag}_bi.csv

Notes:
- Applies stopword filtering per language
- Can drop numeric-only tokens; optionally keep years (e.g., '1995')
"""
from __future__ import annotations
import argparse, re
from pathlib import Path
from collections import Counter
import pandas as pd
from mdke.utils.io import Paths, ensure_dirs, load_yaml

def load_stopwords(lang: str) -> set[str]:
    """Load stopwords from configs/stopwords/{lang}.txt; return empty set if missing."""
    p = Path(f"configs/stopwords/{lang}.txt")
    if not p.exists():
        return set()
    return {
        w.strip().lower()
        for w in p.read_text(encoding="utf-8").splitlines()
        if w.strip() and not w.startswith("#")
    }

def tokenize(txt: str) -> list[str]:
    """Simple whitespace tokenizer; assumes upstream normalization."""
    return re.findall(r"\w+", (txt or "").lower(), flags=re.UNICODE)

def is_numeric_token(t: str) -> bool:
    """Return True if token is purely numeric or punctuation-like numeric."""
    return bool(re.fullmatch(r"\d+", t))

def looks_like_year(t: str) -> bool:
    """Heuristic for four-digit years between 1800 and 2100."""
    if not re.fullmatch(r"\d{3,4}", t):
        return False
    v = int(t)
    return 800 <= v <= 2099

def top_ngrams(df: pd.DataFrame, sw: set[str], n: int = 100,
               drop_numeric: bool = True,
               keep_years: bool = False,
               min_freq: int = 1):
    """Compute top-N unigrams and bigrams after stopword/numeric filtering."""
    uni = Counter()
    bi = Counter()
    series = df["text_norm"] if "text_norm" in df.columns else df["text"]
    for s in series.fillna(""):
        raw = tokenize(s)
        toks = []
        for t in raw:
            if t in sw:
                continue
            if drop_numeric and is_numeric_token(t):
                if keep_years and looks_like_year(t):
                    pass
                else:
                    continue
            toks.append(t)
        for t in toks:
            uni[t] += 1
        for a, b in zip(toks, toks[1:]):
            bi[(a, b)] += 1
    if min_freq > 1:
        uni = Counter({w: c for w, c in uni.items() if c >= min_freq})
        bi = Counter({k: c for k, c in bi.items() if c >= min_freq})
    return uni.most_common(n), bi.most_common(n)

def run(cfg, lang: str, tag: str, top_n: int,
        drop_numeric: bool,
        keep_years: bool,
        min_freq: int):
    """Load corpus and write ngram frequency CSVs into reports/ngrams/."""
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
        raise FileNotFoundError(f"Missing corpus for {lang}")
    sw = load_stopwords(lang)
    uni, bi = top_ngrams(
        df, sw, top_n,
        drop_numeric=drop_numeric,
        keep_years=keep_years,
        min_freq=min_freq
    )
    out_dir = paths.reports / "ngrams"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{lang}{sfx}_unigram.txt").write_text(
        "\n".join(f"{w}\t{c}" for w, c in uni), encoding="utf-8"
    )
    (out_dir / f"{lang}{sfx}_bigram.txt").write_text(
        "\n".join(f"{a} {b}\t{c}" for (a, b), c in bi), encoding="utf-8"
    )
    return str(out_dir)

def main():
    """CLI wrapper with options for N, numeric filtering, and year handling."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--lang", type=str, required=True, choices=["tr","kmr","zza"])
    ap.add_argument("--tag", type=str, default="")
    ap.add_argument("--top_n", type=int, default=100)
    ap.add_argument("--no_drop_numeric", action="store_true",
                    help="Saf numerik tokenları atmayı kapat.")
    ap.add_argument("--keep_years", action="store_true",
                    help="Numerikler atılırken 3–4 haneli yıl benzeri (800–2099) kalsın.")
    ap.add_argument("--min_freq", type=int, default=1,
                    help="Bu frekansın altındaki n-gramları at (default=1).")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    drop_numeric = not args.no_drop_numeric
    print(run(cfg, args.lang, args.tag, args.top_n,
              drop_numeric=drop_numeric,
              keep_years=args.keep_years,
              min_freq=args.min_freq))

if __name__ == "__main__":
    main() 