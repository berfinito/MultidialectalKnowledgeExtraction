#!/usr/bin/env python
"""Lightweight viewer/inspector for topic outputs."""
from pathlib import Path
import json
import sys

lang = sys.argv[1] if len(sys.argv) > 1 else "tr"
p = Path("reports/topics") / f"{lang}_bertopic_topics.json"
info = json.loads(p.read_text(encoding="utf-8"))

topics = [t for t in info if t["topic_id"] != -1]
outlier = next((t for t in info if t["topic_id"] == -1), {"size": 0})
print(f"lang={lang} | n_topics={len(topics)} | outlier_size={outlier['size']}")
print("Top 10 topics:")
for t in sorted(topics, key=lambda x: x["size"], reverse=True)[:10]:
    terms = ", ".join(w["term"] for w in t["top_terms"][:5])
    print(f"- #{t['topic_id']:>4} size={t['size']:>6} | {terms}")