"""
Sentence segmentation (regex-based) and paragraph splitting.

Uses a simple regex on [.?!…] boundaries and trims whitespace.
Optionally normalizes text before splitting if upstream hasn't done so.

Outputs:
- text_sentences_{lang}{_tag}.parquet with one sentence per row
"""
from __future__ import annotations
import re, argparse
from pathlib import Path
import pandas as pd
from mdke.utils.io import Paths, ensure_dirs, load_yaml
from mdke.utils.textnorm import normalize_text

SPLIT_RE = re.compile(r"(?<=[\.\?\!…])\s+")

def sent_tokenize(txt: str) -> list[str]:
    """Split by punctuation regex and clean artifacts; returns list of sentences."""
    parts = SPLIT_RE.split(txt or "")
    out = []
    for p in parts:
        s = (p or "").strip()
        if len(s) < 3:
            continue
        if len(re.findall(r"\w+", s, flags=re.UNICODE)) < 2:
            continue
        out.append(s)
    return out

def run(cfg, lang: str, tag: str):
    """Read corpus, segment into sentences, and write sentence parquet."""
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
    sents = []
    for t in series:
        t = normalize_text(t, lang)
        sents.extend(sent_tokenize(t))
    out_df = pd.DataFrame({"text": sents})
    out_pq = paths.processed / f"text_sentences_{lang}{sfx}.parquet"
    out_df.to_parquet(out_pq, index=False)
    print(f"[{lang}] sentences: in_paragraphs={len(df)} out_sentences={len(out_df)} -> {out_pq}")
    return str(out_pq)

def main():
    """CLI wrapper to segment sentences for specified language/tag."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--lang", required=True, choices=["tr","kmr","zza"])
    ap.add_argument("--tag", default="clean_nonav", help="Kaynak sonek (default: clean_nonav)")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    print(run(cfg, args.lang, args.tag))

if __name__ == "__main__":
    main()