import re, itertools, json, argparse, statistics
from pathlib import Path

def parse_terms(md_path, top_terms_per_topic=5):
    lines = Path(md_path).read_text(encoding="utf-8").splitlines()
    topics = []
    for l in lines:
        m = re.match(r"##\s+Topic\s+\d+\s+\|\s+(.+)", l.strip())
        if m:
            all_terms = [t.strip() for t in m.group(1).split(",") if t.strip()]
            topics.append(all_terms[:top_terms_per_topic])
    return topics

def build_graph(topics):
    edge_w = {}
    nodes = set()
    for terms in topics:
        uniq = sorted(set(terms))
        nodes.update(uniq)
        for a,b in itertools.combinations(uniq, 2):
            edge_w[(a,b)] = edge_w.get((a,b), 0) + 1
    return sorted(nodes), edge_w

def graph_stats(nodes, edges):
    if not nodes:
        return {}
    deg_w = {n:0 for n in nodes}
    for (a,b),w in edges.items():
        deg_w[a]+=w; deg_w[b]+=w
    weighted_edges_sum = sum(edges.values())
    avg_weighted_degree = sum(deg_w.values())/len(nodes)
    density = (2*len(edges))/(len(nodes)*(len(nodes)-1)) if len(nodes) > 1 else 0.0
    avg_edge_weight = weighted_edges_sum/len(edges) if edges else 0.0
    deg_values = list(deg_w.values())
    return {
        "nodes": len(nodes),
        "edges": len(edges),
        "weighted_edges_sum": weighted_edges_sum,
        "avg_weighted_degree": avg_weighted_degree,
        "density": density,
        "avg_edge_weight": avg_edge_weight,
        "median_weighted_degree": statistics.median(deg_values),
        "max_weighted_degree": max(deg_values),
        "min_weighted_degree": min(deg_values)
    }

def to_graphml(nodes, edges, out_path: Path):
    idx = {n:i for i,n in enumerate(nodes)}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n')
        f.write('<key id="label" for="node" attr.name="label" attr.type="string"/>\n')
        f.write('<key id="weight" for="edge" attr.name="weight" attr.type="double"/>\n')
        f.write('<graph edgedefault="undirected">\n')
        for n,i in idx.items():
            f.write(f'<node id="n{i}"><data key="label">{n}</data></node>\n')
        for (a,b),w in edges.items():
            f.write(f'<edge source="n{idx[a]}" target="n{idx[b]}"><data key="weight">{w}</data></edge>\n')
        f.write('</graph>\n</graphml>\n')

def process_lang(lang, reps_dir, out_dir, top_terms):
    reps_file = reps_dir / f"representatives_{lang}_both_top15.md"
    if not reps_file.exists():
        print(f"[WARN] {reps_file} yok; atlanıyor.")
        return None
    topics = parse_terms(reps_file, top_terms_per_topic=top_terms)
    nodes, edges = build_graph(topics)
    stats = graph_stats(nodes, edges)
    graphml = out_dir / f"{lang}_both_top15_terms.graphml"
    stats_json = out_dir / f"{lang}_both_top15_terms_stats.json"
    to_graphml(nodes, edges, graphml)
    stats_json.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[kg] {lang}: {graphml}  stats={stats}")
    stats["lang"] = lang
    return stats

def write_summary_md(stats_list, out_md: Path):
    lines = ["# KG Examples — Both Top15 (TR/KMR/ZZA)", ""]
    lines.append("| Lang | Nodes | Edges | WeightedSum | AvgWeightedDeg | Density | AvgEdgeW | MedDeg | MaxDeg | MinDeg |")
    lines.append("|------|-------|-------|-------------|----------------|---------|----------|--------|--------|--------|")
    for s in stats_list:
        lines.append(
            f"| {s['lang']} | {s['nodes']} | {s['edges']} | {s['weighted_edges_sum']} | "
            f"{s['avg_weighted_degree']:.2f} | {s['density']:.3f} | {s['avg_edge_weight']:.2f} | "
            f"{s['median_weighted_degree']} | {s['max_weighted_degree']} | {s['min_weighted_degree']} |"
        )
    lines += ["","Açıklama:",
              "- Nodes: Terim çeşitliliği.",
              "- Edges: Birlikte görünen terim çiftleri.",
              "- WeightedSum: Kenar ağırlık toplamı (konu sayısı üzerinden).",
              "- AvgWeightedDeg: Ortalama ağırlıklı derece (bağlantı gövdesi).",
              "- Density: Terimler arası olası bağlantıların hangi oranı kullanılmış.",
              "- AvgEdgeW: Kenar başına ortalama tekrar sayısı (topic’ler arası yeniden birliktelik)."]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"[kg-summary] -> {out_md}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", type=str, default="tr,kmr,zza")
    ap.add_argument("--reps_dir", type=Path, default=Path("reports/analysis"))
    ap.add_argument("--out_dir", type=Path, default=Path("reports/kg"))
    ap.add_argument("--top_terms", type=int, default=5, help="Topic başlığından alınacak ilk terim sayısı")
    ap.add_argument("--summary_md", type=Path, default=Path("reports/analysis/kg_examples_all.md"))
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stats_all = []
    for lang in [l.strip() for l in args.langs.split(",") if l.strip()]:
        st = process_lang(lang, args.reps_dir, args.out_dir, args.top_terms)
        if st: stats_all.append(st)
    if stats_all:
        write_summary_md(stats_all, args.summary_md)

if __name__ == "__main__":
    main()