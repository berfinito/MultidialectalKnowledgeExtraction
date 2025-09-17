import argparse, math, json, re
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

TOPIC_HEADER_RE = re.compile(r"^##\s+Topic\s+\d+\s+\|\s+(.+)$")

def parse_topics(md_file: Path, top_terms: int):
    topics = []
    for line in md_file.read_text(encoding="utf-8").splitlines():
        m = TOPIC_HEADER_RE.match(line.strip())
        if m:
            terms = [t.strip() for t in m.group(1).split(",") if t.strip()]
            topics.append(terms[:top_terms])
    return topics

def compute_stats(topic_terms, weighting: str):
    """
    weighting: 'pmi' veya 'tfidf'
    PMI:
      p(u) = freq(u)/T ; p(u,v) = cofreq(u,v)/T  (T = topic sayısı)
      PMI(u,v)=log( p(u,v) / (p(u)p(v)) )
    TF-IDF (burada edge weight):
      tf(u,v) = cofreq(u,v)
      idf(u,v) = log( T / df(u,v) ) ; df(u,v)=cofreq(u,v)  (topic-lık appearance)
      weight = tf * idf (basit)
    """
    T = len(topic_terms)
    term_freq = Counter()
    pair_freq = Counter()
    for terms in topic_terms:
        uniq = set(terms)
        for u in uniq:
            term_freq[u] += 1
        for a, b in combinations(sorted(uniq), 2):
            pair_freq[(a, b)] += 1

    edge_weights = {}
    for (a, b), cf in pair_freq.items():
        if weighting == "pmi":
            p_uv = cf / T
            p_u = term_freq[a] / T
            p_b = term_freq[b] / T
            if p_uv == 0 or p_u == 0 or p_b == 0:
                continue
            w = math.log(p_uv / (p_u * p_b), 2)  # log base 2
        else:  # tfidf
            tf = cf
            idf = math.log(T / cf) if cf > 0 else 0.0
            w = tf * idf
        edge_weights[(a, b)] = w
    return term_freq, edge_weights, T

def export_edge_list(edge_weights, out_path: Path, min_weight: float):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["source\ttarget\tweight"]
    for (a, b), w in edge_weights.items():
        if w >= min_weight:
            lines.append(f"{a}\t{b}\t{w:.6f}")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[kg-weight] edges>={min_weight} -> {out_path}")

def summarize(edge_weights):
    if not edge_weights:
        return {}
    weights = list(edge_weights.values())
    return {
        "edges": len(weights),
        "min": min(weights),
        "max": max(weights),
        "avg": sum(weights)/len(weights)
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps_md", type=Path, required=True, help="Representatives markdown (top15 veya full).")
    ap.add_argument("--top_terms", type=int, default=5)
    ap.add_argument("--weighting", choices=["pmi", "tfidf"], default="pmi")
    ap.add_argument("--min_weight", type=float, default=0.0, help="Edge filtresi (>=).")
    ap.add_argument("--out_edges", type=Path, default=Path("reports/analysis/kg_weighted_edges.tsv"))
    ap.add_argument("--out_stats", type=Path, default=Path("reports/analysis/kg_weighted_stats.json"))
    args = ap.parse_args()

    topics = parse_topics(args.reps_md, args.top_terms)
    _, edge_w, T = compute_stats(topics, args.weighting)
    export_edge_list(edge_w, args.out_edges, args.min_weight)
    stats = summarize(edge_w)
    stats["topics"] = T
    stats["weighting"] = args.weighting
    args.out_stats.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[kg-weight] stats -> {args.out_stats}")

if __name__ == "__main__":
    main()