import argparse, json
from pathlib import Path
import pandas as pd

def load_docs(topics_dir: Path, lang: str, variant: str):
    fp = topics_dir / f"{lang}_bertopic_docs_{variant}.txt"
    return [l.rstrip("\n") for l in fp.read_text(encoding="utf-8").splitlines()]

def load_map(topics_dir: Path, lang: str, variant: str) -> pd.DataFrame:
    fp = topics_dir / f"{lang}_bertopic_doc_topics_{variant}.parquet"
    df = pd.read_parquet(fp)
    # Probability opsiyonel; yoksa 1.0 verelim ki sıralayabilelim
    if "prob" not in df.columns or df["prob"].isna().all():
        df["prob"] = 1.0
    return df

def load_topics(topics_dir: Path, lang: str, variant: str):
    fp = topics_dir / f"{lang}_bertopic_topics_{variant}.json"
    return json.loads(fp.read_text(encoding="utf-8"))

def representatives(lang: str, variant: str, topics_dir: Path, out_md: Path, topk_docs: int = 2):
    docs = load_docs(topics_dir, lang, variant)
    df = load_map(topics_dir, lang, variant)
    topics = load_topics(topics_dir, lang, variant)
    out = []
    out.append(f"# Representatives - {lang}/{variant}")
    out.append("")
    for t in topics:
        tid = t["topic_id"]
        if tid == -1:  # outlier topic
            continue
        top_terms = ", ".join(tt["term"] for tt in t["top_terms"][:5])
        subset = df[df["topic"] == tid].sort_values("prob", ascending=False).head(topk_docs)
        examples = []
        for _, row in subset.iterrows():
            did = int(row["doc_id"])
            if 0 <= did < len(docs):
                examples.append(docs[did])
        out.append(f"## Topic {tid} | {top_terms}")
        for ex in examples:
            out.append(f"- {ex}")
        out.append("")
    out_md.write_text("\n".join(out), encoding="utf-8")
    print(f"[repr] -> {out_md}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topics_dir", type=Path, default=Path("reports/topics"))
    ap.add_argument("--lang", type=str, required=True)
    ap.add_argument("--variant", type=str, choices=["text","cv","both"], required=True)
    ap.add_argument("--topk_docs", type=int, default=2)
    ap.add_argument("--out_md", type=Path, default=None)
    args = ap.parse_args()
    out_md = args.out_md or Path(f"reports/analysis/representatives_{args.lang}_{args.variant}.md")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    representatives(args.lang, args.variant, args.topics_dir, out_md, args.topk_docs)

if __name__ == "__main__":
    main()