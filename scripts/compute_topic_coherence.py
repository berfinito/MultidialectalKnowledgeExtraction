import argparse, json, math, random, re
from pathlib import Path
from typing import List
from statistics import median

try:
    from gensim.corpora import Dictionary
    from gensim.models.coherencemodel import CoherenceModel
except Exception:
    Dictionary = None
    CoherenceModel = None

VARIANTS = ["text","cv","both"]

def simple_tokenize(s: str) -> List[str]:
    s = s.lower()
    s = "".join(ch if (ch.isalpha() or ch.isspace()) else " " for ch in s)
    s = re.sub(r"\s+", " ", s).strip()
    return [t for t in s.split(" ") if t]

def _uniq_preserve_order(tokens: List[str]) -> List[str]:
    seen = set()
    out = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out

def load_docs(base: Path, lang: str, variant: str, sample: int | None) -> List[List[str]]:
    fp = base / f"{lang}_bertopic_docs_{variant}.txt"
    if not fp.exists():
        raise FileNotFoundError(f"Docs file yok: {fp} (topics script patch sonrası yeniden çalıştır)")
    lines = [l.strip() for l in fp.read_text(encoding="utf-8").splitlines() if l.strip()]
    if sample and len(lines) > sample:
        random.shuffle(lines)
        lines = lines[:sample]
    return [simple_tokenize(l) for l in lines]

def load_topics_tokens(base: Path, lang: str, variant: str) -> List[List[str]]:
    fp = base / f"{lang}_bertopic_topics_{variant}.json"
    with fp.open(encoding="utf-8") as f:
        data = json.load(f)
    topics_tokens: List[List[str]] = []
    for t in data:
        if t.get("topic_id", -1) == -1:
            continue
        raw_terms = [tw["term"] for tw in t.get("top_terms", [])]
        tokens_flat: List[str] = []
        for term in raw_terms:
            tokens_flat.extend(simple_tokenize(term))
        tokens_flat = _uniq_preserve_order(tokens_flat)
        if tokens_flat:
            topics_tokens.append(tokens_flat)
    return topics_tokens

def load_doc_map(base: Path, lang: str, variant: str):
    import pandas as pd
    fp = base / f"{lang}_bertopic_doc_topics_{variant}.parquet"
    return pd.read_parquet(fp)

def filter_topics_to_dictionary(topics_tokens: List[List[str]], dictionary: Dictionary, topn_tokens: int) -> List[List[str]]:
    keep = []
    vocab = dictionary.token2id if dictionary is not None else {}
    for toks in topics_tokens:
        toks2 = [t for t in toks if t in vocab]
        toks2 = _uniq_preserve_order(toks2)[:topn_tokens]
        if len(toks2) >= 2:  # coherence için min. 2 token mantıklı
            keep.append(toks2)
    return keep

def coherence_for_lang(base: Path, lang: str, variants, topn_tokens: int, sample: int | None, coherence: str):
    rows = []
    for v in variants:
        try:
            texts = load_docs(base, lang, v, sample)
            if not texts:
                print(f"[WARN] Boş corpus: {lang}/{v}")
                continue
            topics_tokens = load_topics_tokens(base, lang, v)
            if not topics_tokens:
                print(f"[WARN] Topic yok: {lang}/{v}")
                continue

            if Dictionary is None:
                # gensim yoksa sadece istatistikleri yaz
                doc_map = load_doc_map(base, lang, v)
                outliers = (doc_map["topic"] == -1).sum()
                total = len(doc_map)
                outlier_ratio = outliers / total if total else math.nan
                rows.append({
                    "lang": lang, "variant": v, "n_topics": len(topics_tokens),
                    "outlier_ratio": outlier_ratio, "coherence": None,
                    "coh_median": None, "coh_min": None, "coh_max": None,
                })
                continue

            dictionary = Dictionary(texts)
            dictionary.filter_extremes(no_below=2, no_above=0.5, keep_n=50000)
            topics = filter_topics_to_dictionary(topics_tokens, dictionary, topn_tokens)
            if not topics:
                print(f"[WARN] Sözlüğe uyan topic tokenı kalmadı: {lang}/{v}")
                continue

            cm = CoherenceModel(
                topics=topics,
                texts=texts,
                dictionary=dictionary,
                coherence=coherence
            )
            coh = cm.get_coherence()
            per_topic = cm.get_coherence_per_topic()

            doc_map = load_doc_map(base, lang, v)
            outliers = (doc_map["topic"] == -1).sum()
            total = len(doc_map)
            outlier_ratio = outliers / total if total else math.nan

            rows.append({
                "lang": lang,
                "variant": v,
                "n_topics": len(topics),
                "outlier_ratio": outlier_ratio,
                "coherence": coh,
                "coh_median": median(per_topic) if per_topic else None,
                "coh_min": min(per_topic) if per_topic else None,
                "coh_max": max(per_topic) if per_topic else None,
            })
        except FileNotFoundError as e:
            print(f"[WARN] {e}")
    return rows

def _fmt4(x):
    if x is None:
        return "NA"
    try:
        return f"{x:.4f}"
    except Exception:
        return str(x)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topics_dir", type=Path, default=Path("reports/topics"))
    ap.add_argument("--langs", type=str, default="tr,kmr,zza")
    ap.add_argument("--variants", type=str, default="text,cv,both")
    ap.add_argument("--topn", type=int, default=10, help="Her topic için maksimum token sayısı (dictionary'e uyan)")
    ap.add_argument("--sample_docs", type=int, default=20000, help="Coherence için doc sample (<=0 tümü)")
    ap.add_argument("--coherence", type=str, default="c_npmi", choices=["c_npmi","u_mass","c_v"])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out_md", type=Path, default=Path("reports/analysis/topic_coherence.md"))
    args = ap.parse_args()

    random.seed(args.seed)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    langs = [l.strip() for l in args.langs.split(",") if l.strip()]
    variants = [v.strip() for v in args.variants.split(",") if v.strip()]
    sample = None if args.sample_docs <= 0 else args.sample_docs

    all_rows = []
    for lang in langs:
        all_rows.extend(coherence_for_lang(args.topics_dir, lang, variants, args.topn, sample, args.coherence))

    lines = [
        "# Topic Coherence",
        "",
        "| Lang | Variant | #Topics | Outlier% | Coherence | Median | Min | Max |",
        "|------|---------|---------|----------|-----------|--------|-----|-----|"
    ]
    for r in all_rows:
        lines.append(
            f"| {r['lang']} | {r['variant']} | {r['n_topics']} | {r['outlier_ratio']:.2%} | "
            f"{_fmt4(r['coherence'])} | {_fmt4(r['coh_median'])} | {_fmt4(r['coh_min'])} | {_fmt4(r['coh_max'])} |"
        )
    args.out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"[coherence] -> {args.out_md}")

if __name__ == "__main__":
    main()