import json, glob
from pathlib import Path
import argparse
from datetime import datetime

def collect(pattern: str):
    rows = []
    for p in glob.glob(pattern):
        with open(p, "r", encoding="utf-8") as f:
            rep = json.load(f)
        rows.append({
            "lang": rep.get("lang"),
            "split": rep.get("split"),
            "model": rep.get("model"),
            "wer": rep.get("wer"),
            "cer": rep.get("cer"),
            "rtf": rep.get("rtf"),
            "n": rep.get("n"),
            "path": p,
        })
    rows.sort(key=lambda r: (r["lang"], r["split"]))
    return rows

def to_markdown(rows):
    lines = []
    lines.append("| lang | split | model | n | WER | CER | RTF | report |")
    lines.append("|---|---|---|---:|---:|---:|---:|---|")
    for r in rows:
        lines.append(f"| {r['lang']} | {r['split']} | {r['model']} | {r['n']} | {r['wer']:.3f} | {r['cer']:.3f} | {r['rtf']:.3f} | {r['path']} |")
    return "\n".join(lines)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", default="reports/asr_whisper_*_*_medium.json")
    ap.add_argument("--out", default="reports/asr_summary_medium.md")
    args = ap.parse_args()

    rows = collect(args.pattern)
    md = to_markdown(rows)
    print(md)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = f"# ASR Summary (medium)\n\nGenerated: {datetime.now().isoformat(timespec='seconds')}\n\n"
    out_path.write_text(header + md + "\n", encoding="utf-8")
    print(f"\nSaved → {out_path}")