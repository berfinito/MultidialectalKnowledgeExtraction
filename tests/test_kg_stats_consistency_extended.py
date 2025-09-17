import json
from pathlib import Path

def mean_of_tsv_weights(tsv_path: Path):
    weights=[]
    with tsv_path.open("r", encoding="utf-8") as f:
        next(f, None)
        for line in f:
            parts=line.strip().split("\t")
            if len(parts)==3:
                weights.append(float(parts[2]))
    return sum(weights)/len(weights) if weights else 0.0

def test_pmi_tfidf_means_match_stats():
    base = Path("reports/analysis")
    stats_files = list(base.glob("*_kg_*_*_stats.json"))
    assert stats_files, "No stats JSON files found."
    tol = 0.03  # TSV yuvarlama farkı
    for sf in stats_files:
        data = json.loads(sf.read_text(encoding="utf-8"))
        tsv = base / (sf.stem.replace("_stats","") + ".tsv")
        if not tsv.exists():
            continue
        mean_w = mean_of_tsv_weights(tsv)
        assert abs(mean_w - data["avg"]) <= tol, f"{sf.name}: mean {mean_w} vs json {data['avg']}"

def test_stats_schema_and_ranges():
    base = Path("reports/analysis")
    for sf in base.glob("*_kg_*_*_stats.json"):
        data = json.loads(sf.read_text(encoding="utf-8"))
        for k in ("edges","min","max","avg","topics","weighting"):
            assert k in data
        assert data["min"] <= data["avg"] <= data["max"]
        assert data["edges"] > 0
        assert data["topics"] > 0