#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import networkx as nx

def load_tsv(path: Path) -> nx.Graph:
    G = nx.Graph()
    with path.open("r", encoding="utf-8") as f:
        next(f, None)
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
    ap.add_argument("--tsv", type=Path, required=True, help="reports/analysis/... .tsv")
    ap.add_argument("--out", type=Path, required=True, help="Çıkış ( .gexf | .graphml )")
    args = ap.parse_args()

    G = load_tsv(args.tsv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.suffix.lower() == ".gexf":
        nx.write_gexf(G, args.out)
    elif args.out.suffix.lower() == ".graphml":
        nx.write_graphml(G, args.out)
    else:
        raise SystemExit("Desteklenmeyen format. .gexf veya .graphml kullanın.")
    print(f"[export-kg] saved -> {args.out}")

if __name__ == "__main__":
    main()