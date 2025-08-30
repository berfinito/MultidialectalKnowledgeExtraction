# scripts/sprint1_make_markdown.py
# Sprint raporuna görsel bir tablo eklemek çok iyi olur. Aşağıdaki script JSON’ları okuyup Markdown tablo üretir.

import json
from pathlib import Path

summary_path = Path("reports/sprint-1-summary.json")
if not summary_path.exists():
    raise FileNotFoundError("Run sprint1_summarize.py first!")

data = json.loads(summary_path.read_text(encoding="utf-8"))

rows = []
header = "| Lang | Split | Model | N | WER | CER | RTF | Latin/Hawar | TR-bias |\n"
header += "|---|---|---|---:|---:|---:|---:|---:|---:|\n"

for key, v in data.items():
    rows.append(
        f"| {v['lang']} | {v['split']} | {v['model']} | {v['n']} | "
        f"{v['wer']:.3f} | {v['cer']:.3f} | {v['rtf']:.3f} | "
        f"{(v.get('latin_hawar_ratio') or 0):.3f} | {(v.get('tr_token_bias') or 0):.3f} |"
    )

md = header + "\n".join(rows) + "\n"
out_md = Path("reports/sprint-1-summary.md")
out_md.write_text(md, encoding="utf-8")
print(f"Saved Markdown summary → {out_md}")
