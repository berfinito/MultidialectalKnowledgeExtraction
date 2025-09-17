from pathlib import Path
import json

def test_representatives_topic_count():
    p = Path("reports/analysis/representatives_tr_both_top15.md")
    assert p.exists()
    lines = p.read_text(encoding="utf-8").splitlines()
    topics = [l for l in lines if l.startswith("## Topic ")]
    assert len(topics) == 15

def test_kg_weighting_stats_exist():
    stats_files = list(Path("reports/analysis").glob("*_kg_full_pmi_stats.json"))
    assert stats_files, "No full PMI stats JSON files found."
    for sf in stats_files:
        data = json.loads(sf.read_text(encoding="utf-8"))
        for k in ("edges","min","max","avg","topics","weighting"):
            assert k in data