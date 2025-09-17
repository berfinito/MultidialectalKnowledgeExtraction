#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import json

import networkx as nx

def load_tsv(path: Path) -> nx.Graph:
    G = nx.Graph()
    with path.open("r", encoding="utf-8") as f:
        next(f, None)  # header
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) != 3: 
                continue
            s, t, w = p
            try:
                wt = float(w)
            except:
                continue
            G.add_edge(s, t, weight=wt)
    return G

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", type=Path, required=True, help="reports/analysis/..._kg_... .tsv")
    ap.add_argument("--top_edges", type=int, default=200, help="Ağırlığa göre en yüksek N kenar (filtre)")
    ap.add_argument("--out", type=Path, required=True, help="PNG çıkış yolu")
    args = ap.parse_args()

    try:
        import matplotlib
        matplotlib.use("Agg")  # headless
        import matplotlib.pyplot as plt
    except Exception as e:
        print(f"[plot-kg] matplotlib eksik: {e}")
        print("[plot-kg] pip install matplotlib")
        return

    Gfull = load_tsv(args.tsv)
    # En ağır kenarları al
    edges_sorted = sorted(Gfull.edges(data=True), key=lambda e: e[2].get("weight", 1.0), reverse=True)
    keep = edges_sorted[:args.top_edges] if args.top_edges > 0 else edges_sorted
    G = nx.Graph()
    for u, v, d in keep:
        G.add_edge(u, v, **d)

    if G.number_of_nodes() == 0:
        print("[plot-kg] Graph empty after filtering.")
        return

    # En büyük bileşen (daha okunur)
    comps = sorted(nx.connected_components(G), key=len, reverse=True)
    Gc = G.subgraph(comps[0]).copy()

    # Node size = weighted degree; edge width = normalized weight
    wdeg = {n: sum(d.get("weight",1.0) for _,_,d in Gc.edges(n, data=True)) for n in Gc.nodes()}
    wmin = min(d.get("weight",1.0) for _,_,d in Gc.edges(data=True))
    wmax = max(d.get("weight",1.0) for _,_,d in Gc.edges(data=True))
    def norm(w): 
        return 0.5 + 3.5 * ((w - wmin) / (wmax - wmin + 1e-9))

    pos = nx.spring_layout(Gc, seed=42, k=1.0/(len(Gc.nodes())**0.5 + 1e-9), iterations=200, weight="weight")
    plt.figure(figsize=(12, 9), dpi=150)
    nx.draw_networkx_edges(Gc, pos, width=[norm(Gc[u][v].get("weight",1.0)) for u,v in Gc.edges()])
    nx.draw_networkx_nodes(Gc, pos, node_size=[8 + 2.0*wdeg[n] for n in Gc.nodes()], node_color="#1f77b4", alpha=0.85)
    nx.draw_networkx_labels(Gc, pos, font_size=8)

    plt.axis("off")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(args.out, bbox_inches="tight")
    print(f"[plot-kg] saved -> {args.out}")

if __name__ == "__main__":
    main()