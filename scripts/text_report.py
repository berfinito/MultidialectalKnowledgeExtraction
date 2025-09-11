from __future__ import annotations
import argparse
from pathlib import Path

import pandas as pd
import numpy as np

from mdke.utils.io import Paths, ensure_dirs, load_yaml, get_logger
from mdke.utils.metrics import latin_hawar_ratio

def load_table(paths: Paths, lang: str, tag: str = "") -> pd.DataFrame:
    sfx = f"_{tag}" if tag else ""
    p_parquet = paths.processed / f"text_corpus_{lang}{sfx}.parquet"
    p_csv = paths.processed / f"text_corpus_{lang}{sfx}.csv"
    if p_parquet.exists():
        return pd.read_parquet(p_parquet)
    if p_csv.exists():
        return pd.read_csv(p_csv)
    return pd.DataFrame([])

def tf_idf_top(df: pd.DataFrame, top_n: int = 50) -> list[tuple[str, float]]:
    from collections import Counter, defaultdict
    docs = (df["text_norm"].fillna("") + "").tolist()
    if not any(docs):
        docs = (df["text"].fillna("") + "").tolist()
    import re
    word_re = re.compile(r"\w+", flags=re.UNICODE)
    doc_tokens = [set(w.lower() for w in word_re.findall(doc)) for doc in docs]
    dfreq = Counter()
    tf = defaultdict(int)
    for toks in doc_tokens:
        for t in toks:
            dfreq[t] += 1
    for doc in docs:
        for t in word_re.findall(doc):
            tf[t.lower()] += 1
    N = max(1, len(docs))
    scores = {}
    for t, f in tf.items():
        d = dfreq.get(t, 1)
        idf = np.log((N + 1) / (d + 1)) + 1.0
        scores[t] = f * idf
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return top

def write_md_stats(out_path: Path, lang: str, df: pd.DataFrame, top_terms: list[tuple[str,float]], lh_ratio: float):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = len(df)
    n_tok = int(df["n_tokens"].sum()) if "n_tokens" in df.columns else None
    lens = df["n_tokens"].fillna(0)
    pct_short = float((lens < 5).mean()) if len(lens) else 0.0
    pct_medium = float(((lens >= 5) & (lens < 30)).mean()) if len(lens) else 0.0
    pct_long = float((lens >= 30).mean()) if len(lens) else 0.0

    lines = []
    lines.append(f"# Text report — {lang}")
    lines.append("")
    lines.append(f"- docs: {n}")
    lines.append(f"- tokens≈: {n_tok}")
    lines.append(f"- latin_hawar_ratio: {lh_ratio:.3f}")
    lines.append(f"- length buckets (<5 / 5–29 / ≥30): {pct_short:.2%} / {pct_medium:.2%} / {pct_long:.2%}")
    lines.append("")
    lines.append("## Top terms (TF‑IDF)")
    for t, s in top_terms:
        lines.append(f"- {t}\t{s:.2f}")
    out_path.write_text("\n".join(lines), encoding="utf-8")

def run(cfg, lang: str, tag: str = "", top_n: int = 50):
    logger = get_logger(f"text_report_{lang}")
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)
    df = load_table(paths, lang, tag)
    if df.empty:
        logger.warning("No corpus for %s", lang)
        return None
    top = tf_idf_top(df, top_n=top_n)
    lh = float(latin_hawar_ratio(df["text"].astype(str).tolist()))
    out_md = paths.reports / f"text_stats/{lang}{('_'+tag) if tag else ''}.md"
    write_md_stats(out_md, lang, df, top, lh)
    logger.info("Report -> %s", out_md)
    return str(out_md)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--lang", type=str, required=True, choices=["tr","kmr","zza"])
    ap.add_argument("--tag", type=str, default="")
    ap.add_argument("--top_n", type=int, default=50)
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    res = run(cfg, args.lang, args.tag, args.top_n)
    print(res)

if __name__ == "__main__":
    main() 