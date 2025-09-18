"""
Select representative terms and sample sentences per topic and variant.

Inputs:
- reports/topics/{lang}_bertopic_topics.json
- reports/topics/{lang}_bertopic_doc_topics_{variant}.parquet
- reports/topics/{lang}_bertopic_docs_{variant}.txt

Outputs:
- reports/analysis/representatives_{lang}_{variant}.md
- Optionally limits to top-k docs per topic for readability.

Notes:
- The selection ties topic top terms with sample sentences assigned to the topic.
"""
import argparse, json, random
from pathlib import Path
import pandas as pd

def load_docs(topics_dir: Path, lang: str, variant: str):
    """Read per-variant raw docs for sampling sentences."""
    fp = topics_dir / f"{lang}_bertopic_docs_{variant}.txt"
    return [l.rstrip("\n") for l in fp.read_text(encoding="utf-8").splitlines()]

def load_map(topics_dir: Path, lang: str, variant: str) -> pd.DataFrame:
    """Load doc→topic mapping (parquet) and ensure expected columns exist."""
    fp = topics_dir / f"{lang}_bertopic_doc_topics_{variant}.parquet"
    df = pd.read_parquet(fp)
    if "prob" not in df.columns or df["prob"].isna().all():
        df["prob"] = 1.0
    return df

def load_topics(topics_dir: Path, lang: str, variant: str):
    """Load topics JSON; returns list/dict depending on upstream exporter."""
    fp = topics_dir / f"{lang}_bertopic_topics_{variant}.json"
    return json.loads(fp.read_text(encoding="utf-8"))

def representatives(lang: str,
                    variant: str,
                    topics_dir: Path,
                    out_md: Path,
                    topk_docs: int = 2,
                    seed: int | None = None,
                    include_header: bool = True):
    """Render representatives as markdown for a given language/variant."""
    if seed is not None:
        random.seed(seed)
    docs = load_docs(topics_dir, lang, variant)
    df = load_map(topics_dir, lang, variant)
    topics = load_topics(topics_dir, lang, variant)

    out = []
    if include_header:
        out.append(f"# Representatives - {lang}/{variant}")
        out.append("")
    # Topic list explicitly sorted by id for deterministic order
    topics_sorted = sorted([t for t in topics if t["topic_id"] != -1],
                           key=lambda x: x["topic_id"])
    for t in topics_sorted:
        tid = t["topic_id"]
        top_terms = ", ".join(tt["term"] for tt in t["top_terms"][:5])
        subset = df[df["topic"] == tid].copy()

        # Deterministik: prob DESC, doc_id ASC
        subset = subset.sort_values(["prob", "doc_id"], ascending=[False, True])

        # Eğer tüm prob'lar aynıysa ve seed verildiyse hafif shuffle yapıp tekrar sırala (ikincil deterministik)
        if seed is not None:
            if subset["prob"].nunique() == 1:
                # shuffle doc_id order in a controlled way
                shuf = list(subset["doc_id"])
                random.shuffle(shuf)
                order_map = {d: i for i, d in enumerate(shuf)}
                subset["tie_order"] = subset["doc_id"].map(order_map)
                subset = subset.sort_values(["prob", "tie_order"], ascending=[False, True])

        examples = []
        for _, row in subset.head(topk_docs).iterrows():
            did = int(row["doc_id"])
            if 0 <= did < len(docs):
                examples.append(docs[did])

        out.append(f"## Topic {tid} | {top_terms}")
        for ex in examples:
            out.append(f"- {ex}")
        out.append("")

    out_md.write_text("\n".join(out), encoding="utf-8")
    print(f"[repr] -> {out_md} (topics={len(topics_sorted)} seed={seed})")

def main():
    """CLI wrapper to render representatives for requested languages/variants."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--topics_dir", type=Path, default=Path("reports/topics"))
    ap.add_argument("--lang", type=str, required=True)
    ap.add_argument("--variant", type=str, choices=["text","cv","both"], required=True)
    ap.add_argument("--topk_docs", type=int, default=2)
    ap.add_argument("--out_md", type=Path, default=None)
    ap.add_argument("--seed", type=int, default=None,
                    help="Deterministik temsilci seçimi için seed (prob eşitliklerinde).")
    ap.add_argument("--no_header", action="store_true",
                    help="Birleştirme için üst başlığı yazma.")
    args = ap.parse_args()
    out_md = args.out_md or Path(f"reports/analysis/representatives_{args.lang}_{args.variant}.md")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    representatives(args.lang, args.variant, args.topics_dir, out_md,
                    args.topk_docs, args.seed, include_header=not args.no_header)

if __name__ == "__main__":
    main()