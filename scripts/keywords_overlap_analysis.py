"""
Compute Jaccard overlap between keyword sets across variants (text vs cv vs both).

Output:
  - reports/analysis/keyword_overlap.md

Details:
- Reads JSON arrays of [term, score] from reports/keywords/{lang}_{method}_{variant}.json
- Reports per-language, per-method overlaps and basic descriptive stats
- Multi-word ratio and average term length included for qualitative comparison
"""
import argparse, json
from pathlib import Path
from typing import Dict, List, Tuple, Set

VARIANTS = ["text","cv","both"]

def load_pairs(fp: Path) -> List[Tuple[str, float]]:
    """Load [term, score] pairs from a JSON file and return as list of tuples."""
    data = json.loads(fp.read_text(encoding="utf-8"))
    # data format: list of [term, score] or [[term, score], ...] or list of lists?
    # Current format is list of [term, score] pairs (JSON dumps of list of tuples)
    return [(d[0], d[1]) for d in data]

def avg_len(terms: List[str]) -> float:
    """Average character length of terms; 0.0 if list is empty."""
    return sum(len(t) for t in terms) / max(1, len(terms))

def multi_word_ratio(terms: List[str]) -> float:
    """Ratio of terms containing two or more whitespace-separated tokens."""
    return sum(1 for t in terms if len(t.split()) >= 2) / max(1, len(terms))

def jaccard(a: Set[str], b: Set[str]) -> float:
    """Jaccard overlap between two sets; returns 1.0 if both empty."""
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)

def analyze_lang(base: Path, lang: str, method: str):
    """Compute overlaps and term stats for a single language and method."""
    sets: Dict[str, Set[str]] = {}
    stats = {}
    for v in VARIANTS:
        fp = base / f"{lang}_{method}_{v}.json"
        if not fp.exists():
            continue
        pairs = load_pairs(fp)
        terms = [p[0] for p in pairs]
        sets[v] = set(terms)
        stats[v] = {
            "count": len(terms),
            "avg_len": avg_len(terms),
            "multi_word_ratio": multi_word_ratio(terms),
        }
    if not sets:
        return None
    # overlaps
    text = sets.get("text", set())
    cv = sets.get("cv", set())
    both = sets.get("both", set())
    union_base = text | cv
    new_in_both = both - union_base
    out = {
        "lang": lang,
        "method": method,
        "variants": stats,
        "j_text_cv": jaccard(text, cv),
        "j_text_both": jaccard(text, both),
        "j_cv_both": jaccard(cv, both),
        "only_text": len(text - cv),
        "only_cv": len(cv - text),
        "new_in_both": len(new_in_both),
        "both_total": len(both),
        "new_in_both_pct": (len(new_in_both)/len(both)) if both else 0.0
    }
    return out

def main():
    """Entry point: iterate langs/methods, write markdown report."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--keywords_dir", type=Path, default=Path("reports/keywords"))
    ap.add_argument("--langs", type=str, default="tr,kmr,zza")
    ap.add_argument("--methods", type=str, default="keybert,yake")
    ap.add_argument("--out_md", type=Path, default=Path("reports/analysis/keyword_overlap.md"))
    args = ap.parse_args()
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    langs = [l.strip() for l in args.langs.split(",") if l.strip()]
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]

    rows = []
    for lang in langs:
        for method in methods:
            res = analyze_lang(args.keywords_dir, lang, method)
            if res:
                rows.append(res)

    lines = ["# Keyword Overlap & Novelty", ""]
    for res in rows:
        lines.append(f"## {res['lang']} - {res['method']}")
        vstats = res["variants"]
        header = "| Variant | Count | AvgLen | MultiWord |"
        sep = "|---------|-------|--------|-----------|"
        lines.append(header); lines.append(sep)
        for v, st in vstats.items():
            lines.append(f"| {v} | {st['count']} | {st['avg_len']:.1f} | {st['multi_word_ratio']:.3f} |")
        lines.append("")
        lines.append("| J(text,cv) | J(text,both) | J(cv,both) | only_text | only_cv | both_total | new_in_both | new_in_both% |")
        lines.append("|-----------|--------------|-----------|-----------|---------|------------|-------------|--------------|")
        lines.append(f"| {res['j_text_cv']:.3f} | {res['j_text_both']:.3f} | {res['j_cv_both']:.3f} | "
                     f"{res['only_text']} | {res['only_cv']} | {res['both_total']} | {res['new_in_both']} | {res['new_in_both_pct']:.2%} |")
        lines.append("")
    args.out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"[overlap] -> {args.out_md}")

if __name__ == "__main__":
    main()