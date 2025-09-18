"""
Export a weighted co-occurrence edge list (TSV) to a graph file (GEXF or GraphML).

Input TSV schema (header required):
    source<TAB>target<TAB>weight

Usage:
    python scripts/export_kg.py --tsv reports/analysis/tr_kg_full_pmi.tsv --out reports/analysis/exports/tr_kg_full_pmi.gexf

Notes:
- Undirected graph is used; edges are treated as symmetric.
- Weight is preserved on the edge attribute 'weight'.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from typing import Iterable, Tuple
import networkx as nx


def read_edges_tsv(path: Path) -> Iterable[Tuple[str, str, float]]:
    """
    Yield (source, target, weight) from a TSV file with a header row.
    Lines with parse errors are skipped.
    """
    with path.open("r", encoding="utf-8") as f:
        header = next(f, None)
        if not header or "source" not in header or "target" not in header or "weight" not in header:
            raise ValueError(f"Invalid TSV header in {path}. Expected: source\\ttarget\\tweight")
        for lineno, line in enumerate(f, start=2):
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                continue
            s, t, w = parts
            try:
                yield s, t, float(w)
            except ValueError:
                # skip malformed weight
                continue


def load_graph_from_tsv(path: Path) -> nx.Graph:
    """
    Create an undirected weighted graph from a TSV edge list.
    """
    G = nx.Graph()
    for s, t, w in read_edges_tsv(path):
        G.add_edge(s, t, weight=w)
    return G


def main() -> None:
    ap = argparse.ArgumentParser(description="Export KG TSV to GEXF/GraphML.")
    ap.add_argument("--tsv", type=Path, required=True, help="Input TSV with columns: source, target, weight")
    ap.add_argument("--out", type=Path, required=True, help="Output path (.gexf | .graphml)")
    args = ap.parse_args()

    if not args.tsv.exists():
        raise SystemExit(f"Input not found: {args.tsv}")

    G = load_graph_from_tsv(args.tsv)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    suffix = args.out.suffix.lower()
    if suffix == ".gexf":
        nx.write_gexf(G, args.out)
    elif suffix == ".graphml":
        nx.write_graphml(G, args.out)
    else:
        raise SystemExit("Unsupported format. Use .gexf or .graphml")

    print(f"[export-kg] nodes={G.number_of_nodes()} edges={G.number_of_edges()} -> {args.out}")


if __name__ == "__main__":
    main()