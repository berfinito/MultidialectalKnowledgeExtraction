#!/usr/bin/env python
"""
Aggregate runtime metrics (RTF, wall time, item counts) from ASR reports.

Input:
  - reports/asr_whisper_*_*.json
Output:
  - reports/asr_runtime_summary_validation.csv (or similar)
"""
import json, glob, pandas as pd, pathlib

def load_reports(patterns):
    rows=[]
    for pat in patterns:
        for p in glob.glob(pat):
            rep=json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
            rows.append({
                "report_file": p,
                "backend": "ct2" if "whisperct2" in p else "hf",
                "model": rep.get("model"),
                "lang": rep.get("lang"),
                "split": rep.get("split"),
                "n": rep.get("n"),
                "wer": rep.get("wer"),
                "cer": rep.get("cer"),
                "rtf": rep.get("rtf"),
                "latin_hawar_ratio": rep.get("latin_hawar_ratio"),
                "total_audio_s": rep.get("total_audio_s"),
                "wall_s": rep.get("wall_s"),
            })
    return pd.DataFrame(rows)

df = load_reports([
    "reports/asr_whisper_*_validation.json",
    "reports/asr_whisperct2_*_validation.json",
])
df = df.sort_values(["lang","backend"]).reset_index(drop=True)
out_csv = "reports/asr_runtime_summary_validation.csv"
pathlib.Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out_csv, index=False, encoding="utf-8")
print(df)
print(f"\nSaved → {out_csv}")