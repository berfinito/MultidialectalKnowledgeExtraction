# scripts/kg_weighting.py
from __future__ import annotations

import argparse, json, math, re
from pathlib import Path
from collections import Counter
from itertools import combinations
from typing import Dict, List, Tuple

__all__ = ["compute_stats", "parse_topics", "export_edge_list", "summarize"]

TOPIC_HEADER_RE = re.compile(r"^##\s+Topic\s+\d+\s+\|\s+(.+)$")

def parse_topics(md_file: Path, top_terms: int) -> List[List[str]]:
    """
    representatives.md tarzı bir dosyadan, her topic başlığındaki terimleri çekip
    ilk top_terms kadarını döndürür.
    """
    topics: List[List[str]] = []
    for line in md_file.read_text(encoding="utf-8").splitlines():
        m = TOPIC_HEADER_RE.match(line.strip())
        if m:
            terms = [t.strip() for t in m.group(1).split(",") if t.strip()]
            topics.append(terms[:top_terms])
    return topics


def compute_stats(topic_terms: List[List[str]], weighting: str):
    """
    Testlerde de kullanılan basit istatistik hesaplayıcı.

    weighting:
      - 'pmi':  PMI(u,v) = log( p(u,v) / (p(u) * p(v)) ), p(x) = freq(x)/T
                (log tabanı doğal log; işaret ve 0 değerleri tabandan bağımsızdır)
      - 'tfidf': tf-idf benzeri kenar ağırlığı (tf = birlikte görünme sayısı,
                 idf = log(T/df) ve burada df(u,v) = birlikte görünme sayısı)

    Dönüş:
      term_freq  : Dict[token, int]
      edge_weights: Dict[(u,v), float]   # u < v sıralı
      T          : int                   # topic sayısı
    """
    if weighting not in {"pmi", "tfidf"}:
        raise ValueError(f"Unsupported weighting: {weighting}")

    T = len(topic_terms)
    term_freq: Counter[str] = Counter()
    pair_freq: Counter[Tuple[str, str]] = Counter()

    # Her topic'i set'e çevirerek tekil sayım (topic frekansı mantığı)
    for terms in topic_terms:
        uniq = set(terms)
        term_freq.update(uniq)
        for a, b in combinations(sorted(uniq), 2):
            pair_freq[(a, b)] += 1

    edge_weights: Dict[Tuple[str, str], float] = {}
    for (a, b), cf in pair_freq.items():
        if weighting == "pmi":
            p_uv = cf / T
            p_u = term_freq[a] / T
            p_v = term_freq[b] / T
            if p_uv == 0 or p_u == 0 or p_v == 0:
                continue
            # doğal log (base e) — testlerin işaret/0 beklentisiyle uyumlu
            w = math.log(p_uv / (p_u * p_v))
        else:
            # tf * idf (df(u,v) = cofreq)
            tf = cf
            idf = math.log(T / cf) if cf > 0 else 0.0
            w = tf * idf
        edge_weights[(a, b)] = float(w)

    return term_freq, edge_weights, T


def export_edge_list(edge_weights: Dict[Tuple[str, str], float], out_path: Path, min_weight: float):
    """
    Edge listesini TSV'ye yazar (source, target, weight).
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["source\ttarget\tweight"]
    for (a, b), w in edge_weights.items():
        if w >= min_weight:
            lines.append(f"{a}\t{b}\t{w:.6f}")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[kg-weight] edges>={min_weight} -> {out_path}")


def summarize(edge_weights: Dict[Tuple[str, str], float]) -> Dict[str, float]:
    """
    min/avg/max özetini döndürür. IEEE yuvarlama farklarından doğan sınır
    ihlallerini önlemek için avg değerini min/max içine çok küçük bir epsilon ile
    kısıtlarız.
    """
    if not edge_weights:
        return {"edges": 0, "min": 0.0, "max": 0.0, "avg": 0.0}
    vals = list(edge_weights.values())
    e = len(vals)
    vmin = float(min(vals))
    vmax = float(max(vals))
    vavg = float(sum(vals) / e)
    # numerik stabilizasyon (testlerde min <= avg <= max gereksinimi var)
    eps = 1e-12
    if vavg < vmin - eps:
        vavg = vmin
    if vavg > vmax + eps:
        vavg = vmax
    return {
        "edges": e,
        "min": vmin,
        "max": vmax,
        "avg": vavg,
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
