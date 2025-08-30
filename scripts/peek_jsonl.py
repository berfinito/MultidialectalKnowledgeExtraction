# scripts/peek_jsonl.py
# Örnek tahminleri kontrol et (kalite ve alfabetik düzgünlük). İlk 10 örneği görelim.

import json
from pathlib import Path
import sys

f = Path(sys.argv[1])
n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
with f.open("r", encoding="utf-8") as fh:
    for i, line in enumerate(fh):
        if i >= n: break
        row = json.loads(line)
        print("-", row["path"])
        print("GT:", row["gt_text"])
        print("HY:", row["pred_text"])
        print()
