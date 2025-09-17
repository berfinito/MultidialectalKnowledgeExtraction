#!/usr/bin/env python
"""
Minimal KG centrality summary.
Input pattern: reports/analysis/*_kg_{top15,full}_{pmi,tfidf}.tsv
Metrics:
- node count, edge count
- degree mean/max
- weighted degree mean/max
- connected component count
Output:
  reports/analysis/kg_centrality_summary.md
"""
import argparse, glob
from pathlib import Path
import networkx as nx

def load_graph(path: str):
    G = nx.Graph()
    with open(path, "r", encoding="utf-8") as f:
        next(f)
        for line in f:
            parts=line.strip().split("\t")
            if len(parts)==3:
                s,t,w=parts
                G.add_edge(s,t,weight=float(w))
    return G

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patterns", nargs="+",
                    default=["reports/analysis/*_kg_*_pmi.tsv","reports/analysis/*_kg_*_tfidf.tsv"])
    ap.add_argument("--out", type=Path, default=Path("reports/analysis/kg_centrality_summary.md"))
    args = ap.parse_args()
    rows=[]
    for pat in args.patterns:
        for path in glob.glob(pat):
            if path.endswith("_stats.json"):
                continue
            G=load_graph(path)
            deg=[d for _,d in G.degree()]
            wdeg=[sum(d.get("weight",1.0) for _,_,d in G.edges(n,data=True)) for n in G.nodes()]
            cc = nx.number_connected_components(G)
            stem=Path(path).stem  # e.g. tr_kg_full_pmi
            rows.append((stem, G.number_of_nodes(), G.number_of_edges(),
                         sum(deg)/len(deg) if deg else 0,
                         max(deg) if deg else 0,
                         sum(wdeg)/len(wdeg) if wdeg else 0,
                         max(wdeg) if wdeg else 0,
                         cc))
    lines=["# KG Centrality (Minimal)","","| Graph | Nodes | Edges | DegMean | DegMax | WDegMean | WDegMax | #CC |",
           "|-------|------|-------|--------|--------|----------|---------|-----|"]
    for r in rows:
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]:.2f} | {r[4]} | {r[5]:.2f} | {r[6]:.2f} | {r[7]} |")
    args.out.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"[centrality] -> {args.out}")

if __name__ == "__main__":
    main()