"""
Compute centrality & clustering stats for KG TSVs.

Inputs (glob):
  reports/analysis/{lang}_kg_{set}_{weight}.tsv

Outputs:
  reports/analysis/centrality/{stem}_centrality.json
  reports/analysis/centrality/summary.md

Metrics:
- degree, weighted_degree
- betweenness (k-sampling if nodes>300)
- eigenvector (numpy-based; fallback empty if fails)
- clustering (unweighted)
- connected components (count + size stats)

Notes:
- TSV schema is: source<TAB>target<TAB>weight with a header row.
- Graph is undirected; weights aggregated where multiple edges occur.
"""
from __future__ import annotations
import argparse
import glob
import json
from pathlib import Path
import math
import statistics
import networkx as nx
from typing import List, Dict, Any

def load_graph(path: str):
    """Load an undirected weighted graph from a TSV edge list with header."""
    G = nx.Graph()
    with open(path, "r", encoding="utf-8") as f:
        next(f)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                continue
            s, t, w = parts
            try:
                wt = float(w)
            except Exception:
                continue
            G.add_edge(s, t, weight=wt)
    return G

def safe_eigenvector(G: nx.Graph):
    """Compute eigenvector centrality with a safe fallback if it fails."""
    try:
        return nx.eigenvector_centrality_numpy(G, weight="weight")
    except Exception:
        return {}

def maybe_betweenness(G: nx.Graph):
    """Compute betweenness centrality; sample k nodes if graph is large."""
    n = G.number_of_nodes()
    if n <= 300:
        return nx.betweenness_centrality(G, weight="weight", normalized=True)
    # sample k nodes
    k = min(128, max(16, int(math.sqrt(n))))
    return nx.betweenness_centrality(G, weight="weight", normalized=True, k=k, seed=42)

def percentile(vals: List[float], p: float):
    """Return p-th percentile (0-100) for a list of floats; empty=>None."""
    if not vals:
        return None
    vals_sorted = sorted(vals)
    k = (len(vals_sorted) - 1) * (p / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(vals_sorted[int(k)])
    d0 = vals_sorted[f] * (c - k)
    d1 = vals_sorted[c] * (k - f)
    return float(d0 + d1)

def summarize(vals: List[float]) -> Dict[str, Any]:
    """Summarize a numeric list with min/max/avg/std and selected percentiles."""
    if not vals:
        return {}
    mn = float(min(vals))
    mx = float(max(vals))
    mean = float(statistics.fmean(vals))
    med = float(statistics.median(vals))
    p90 = percentile(vals, 90)
    return {"min": mn, "max": mx, "mean": mean, "median": med, "p90": (None if p90 is None else float(p90))}

def main():
    """Drive the analysis across input patterns and write JSON + summary.md."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--patterns", nargs="+", required=False,
                    default=["reports/analysis/*_kg_full_*.tsv","reports/analysis/*_kg_top15_*.tsv"])
    ap.add_argument("--out-dir", default="reports/analysis/centrality")
    args = ap.parse_args()
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)

    summary_rows = []

    for pat in args.patterns:
        for path in glob.glob(pat):
            if path.endswith("_stats.json"):
                continue
            G = load_graph(path)
            deg = dict(G.degree())
            wdeg = {n: sum(data.get("weight", 1.0) for _, _, data in G.edges(n, data=True)) for n in G.nodes()}
            ev = safe_eigenvector(G)
            btw = maybe_betweenness(G)
            clust = nx.clustering(G)
            comps = [len(c) for c in nx.connected_components(G)]

            stats = {
                "file": path,
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges(),
                "degree": summarize(list(deg.values())),
                "weighted_degree": summarize(list(wdeg.values())),
                "eigenvector": summarize(list(ev.values())),
                "betweenness": summarize(list(btw.values())),
                "clustering": summarize(list(clust.values())),
                "components": {
                    "count": len(comps),
                    "sizes": summarize(comps),
                }
            }
            out_json = Path(args.out_dir) / (Path(path).stem + "_centrality.json")
            out_json.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

            stem = Path(path).stem  # e.g. tr_kg_full_pmi
            parts = stem.split("_kg_")
            if len(parts) != 2 or "_" not in parts[1]:
                # beklenmeyen adlandırma — summary’ye ekleme ama json’ı yine yaz
                continue
            lang = parts[0]
            tail = parts[1]           # full_pmi
            set_, weight = tail.split("_", 1)

            summary_rows.append({
                "lang": lang,
                "set": set_,
                "weight": weight,
                "nodes": stats["nodes"],
                "edges": stats["edges"],
                "deg_mean": stats["degree"].get("mean", 0.0) if stats["degree"] else 0.0,
                "deg_max": stats["degree"].get("max", 0.0) if stats["degree"] else 0.0,
                "wdeg_mean": stats["weighted_degree"].get("mean", 0.0) if stats["weighted_degree"] else 0.0,
                "wdeg_max": stats["weighted_degree"].get("max", 0.0) if stats["weighted_degree"] else 0.0,
                "ev_max": (stats["eigenvector"] or {}).get("max", 0.0) or 0.0,
                "btw_p90": (stats["betweenness"] or {}).get("p90", 0.0) or 0.0,
                "components": stats["components"]["count"],
            })

    # Markdown summary
    if summary_rows:
        lines = [
            "# KG Centrality Summary",
            "",
            "| Lang | Set | W | Nodes | Edges | DegMean | DegMax | WDegMean | WDegMax | EVmax | BtwP90 | #Comp |",
            "|------|-----|---|-------|-------|--------:|-------:|---------:|--------:|------:|-------:|------:|",
        ]
        for r in summary_rows:
            lines.append(
                f"| {r['lang']} | {r['set']} | {r['weight']} | {r['nodes']} | {r['edges']} | "
                f"{r['deg_mean']:.2f} | {r['deg_max']:.0f} | {r['wdeg_mean']:.2f} | {r['wdeg_max']:.0f} | "
                f"{r['ev_max']:.3f} | {r['btw_p90']:.3f} | {r['components']} |"
            )
        (Path(args.out_dir) / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
