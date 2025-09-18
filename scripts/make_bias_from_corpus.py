#!/usr/bin/env python
"""Build bias prompt from corpus snippets (KMR/ZZA) if needed."""
import pandas as pd
from collections import Counter
import re, argparse, pathlib
from itertools import islice

def tokenize(s: str):
    s = s.lower()
    s = re.sub(r"[^a-zçğıîêşûöüâêîû’wqx\s]", " ", s)
    return [t for t in s.split() if len(t) > 1]

def ngrams(tokens, n):
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--mode", choices=["light","strong"], default="strong")
    ap.add_argument("--top_k", type=int, default=2000)
    ap.add_argument("--ngrams", type=int, default=1, help="Unigram=1, Bigram=2, Trigram=3")
    ap.add_argument("--in_parquet", default=None)
    ap.add_argument("--out_txt", default=None)
    ap.add_argument("--add_examples", action="store_true", help="Add sample sentences at the end")
    args = ap.parse_args()

    in_path = args.in_parquet or f"data/processed/cv_{args.lang}_train.parquet"
    out_path = args.out_txt or f"configs/prompts/{args.lang}_bias.txt"

    df = pd.read_parquet(in_path)
    items = []
    for t in df["text"].astype(str):
        toks = tokenize(t)
        if args.ngrams == 1:
            items.extend(toks)
        else:
            items.extend(ngrams(toks, args.ngrams))

    cnt = Counter(items).most_common(args.top_k)
    words = [w for w,_ in cnt]

    p = pathlib.Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write("# mode: "+args.mode+"\n")
        f.write("# Hawar alphabet: a b c ç d e ê f g h i î j k l m n o p q r s ş t u û v w x y z\n\n")
        f.write("# Top {}-gram list\n".format(args.ngrams))
        f.write(" ".join(words)+"\n\n")
        if args.add_examples:
            f.write("# Sample sentences from corpus\n")
            for ex in islice(df["text"], 10):
                f.write(ex.strip()+"\n")

if __name__ == "__main__":
    main()