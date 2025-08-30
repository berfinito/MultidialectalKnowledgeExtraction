# scripts/sprint1_summarize.py
import json
from pathlib import Path

REPORTS = [
    "reports/asr_whisper_tr_validation.json",
    "reports/asr_whisper_tr_test.json",
    "reports/asr_whisperct2_kmr_validation.json",
    "reports/asr_whisperct2_kmr_test.json",
    "reports/asr_whisperct2_zza_validation.json",
    "reports/asr_whisperct2_zza_test.json",
]

out = {}
for rp in REPORTS:
    p = Path(rp)
    if not p.exists():
        print(f"[WARN] Missing: {rp}")
        continue
    data = json.loads(p.read_text(encoding="utf-8"))
    key = f"{data['lang']}_{data['split']}"
    out[key] = data

out_path = Path("reports/sprint-1-summary.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Saved Sprint-1 summary → {out_path}")
