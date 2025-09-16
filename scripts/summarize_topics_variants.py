from pathlib import Path
import json, sys

langs = sys.argv[1].split(",") if len(sys.argv) > 1 else ["tr","kmr","zza"]
variants = ["text", "cv", "both"]

def summarize(p: Path):
    info = json.loads(p.read_text(encoding="utf-8"))
    topics = [t for t in info if t["topic_id"] != -1]
    outlier = next((t for t in info if t["topic_id"] == -1), {"size": 0})
    total = outlier["size"] + sum(t["size"] for t in topics)
    return dict(
        n_topics=len(topics),
        outlier_size=outlier["size"],
        total=total,
        outlier_ratio=(outlier["size"]/total) if total else 0.0,
    )

base = Path("reports/topics")
for lang in langs:
    for variant in variants:
        p = base / f"{lang}_bertopic_topics_{variant}.json"
        if p.exists():
            s = summarize(p)
            print(f"{lang.upper()} {variant:<5} | topics={s['n_topics']:>4} | outliers={s['outlier_size']:>6} | ratio={s['outlier_ratio']:.2%}")
        else:
            print(f"{lang.upper()} {variant:<5} | MISSING")