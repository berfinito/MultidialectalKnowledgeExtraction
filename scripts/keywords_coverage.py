import argparse, json, re
from pathlib import Path
from typing import List, Tuple, Dict

def load_docs(topics_dir: Path, lang: str, variant: str) -> List[str]:
    fp = topics_dir / f"{lang}_bertopic_docs_{variant}.txt"
    return [l.strip() for l in fp.read_text(encoding="utf-8").splitlines() if l.strip()]

def load_pairs(base: Path, lang: str, method: str, variant: str) -> List[Tuple[str, float]]:
    fp = base / f"{lang}_{method}_{variant}.json"
    data = json.loads(fp.read_text(encoding="utf-8"))
    return [(d[0], float(d[1])) for d in data]

def term_in_doc(term: str, doc: str) -> bool:
    # basit, küçük harf eşleşmesi; çok-sözcüklü terimler için substring
    return term in doc

def normalize(s: str) -> str:
    s = s.lower()
    s = "".join(ch if (ch.isalpha() or ch.isspace()) else " " for ch in s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def coverage_for_variant(topics_dir: Path, keywords_dir: Path, lang: str, method: str, variant: str):
    docs = [normalize(d) for d in load_docs(topics_dir, lang, variant)]
    pairs = load_pairs(keywords_dir, lang, method, variant)
    terms = [t for t,_ in pairs]
    terms_norm = [normalize(t) for t in terms]
    n_docs = len(docs)
    counts = []
    for t in terms_norm:
        c = sum(1 for d in docs if term_in_doc(t, d))
        counts.append(c)
    covered = sum(1 for c in counts if c > 0)
    avg_df = (sum(counts)/n_docs) if n_docs else 0.0
    return {
        "lang": lang, "method": method, "variant": variant,
        "topN": len(terms_norm), "covered_terms": covered, "covered_pct": covered/len(terms_norm) if terms_norm else 0.0,
        "avg_doc_coverage": avg_df
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topics_dir", type=Path, default=Path("reports/topics"))
    ap.add_argument("--keywords_dir", type=Path, default=Path("reports/keywords"))
    ap.add_argument("--langs", type=str, default="tr,kmr,zza")
    ap.add_argument("--methods", type=str, default="keybert,yake")
    ap.add_argument("--variants", type=str, default="text,cv,both")
    ap.add_argument("--out_md", type=Path, default=Path("reports/analysis/keyword_coverage.md"))
    args = ap.parse_args()
    args.out_md.parent.mkdir(parents=True, exist_ok=True)

    langs = [x for x in args.langs.split(",") if x]
    methods = [x for x in args.methods.split(",") if x]
    variants = [x for x in args.variants.split(",") if x]

    rows: List[Dict] = []
    for lang in langs:
        for method in methods:
            for v in variants:
                try:
                    rows.append(coverage_for_variant(args.topics_dir, args.keywords_dir, lang, method, v))
                except FileNotFoundError:
                    pass

    lines = ["# Keyword Coverage", ""]
    lines.append("| Lang | Method | Variant | topN | covered_terms | covered% | avg_doc_coverage |")
    lines.append("|------|--------|---------|------|---------------|----------|------------------|")
    for r in rows:
        lines.append(f"| {r['lang']} | {r['method']} | {r['variant']} | {r['topN']} | {r['covered_terms']} | {r['covered_pct']:.2%} | {r['avg_doc_coverage']:.3f} |")
    args.out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"[coverage] -> {args.out_md}")

if __name__ == "__main__":
    main()