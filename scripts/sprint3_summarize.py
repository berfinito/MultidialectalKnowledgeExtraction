from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
import pandas as pd  # row sayısı fallback için

LANGS = ["tr", "kmr", "zza"]

def parse_residual_report(path: Path):
    if not path.exists():
        return None
    data = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip()
    try:
        return {
            "input": int(data.get("input", "0")),
            "dropped": int(data.get("dropped", "0")),
            "kept": int(data.get("kept", "0")),
            "source": data.get("source"),
            "out": data.get("out"),
        }
    except Exception:
        return None

def parquet_len(p: Path) -> int | None:
    if not p.exists():
        return None
    try:
        return len(pd.read_parquet(p))
    except Exception:
        return None

def main():
    root = Path(".").resolve()
    reports_dir = root / "reports"
    processed = root / "data" / "processed"
    out_json = reports_dir / "sprint-3-summary.json"

    summary = {"_generated_at": datetime.utcnow().isoformat() + "Z"}

    for lang in LANGS:
        res_file = reports_dir / "text_stats" / f"residual_media_{lang}.txt"
        res = parse_residual_report(res_file)

        base = processed / f"text_corpus_{lang}.parquet"
        clean = processed / f"text_corpus_{lang}_clean.parquet"

        input_n = res["input"] if res else parquet_len(base)
        kept_n = res["kept"] if res else parquet_len(clean)
        dropped_n = res["dropped"] if res else (input_n - kept_n if (input_n is not None and kept_n is not None) else None)

        uni_clean = reports_dir / "ngrams" / f"{lang}_clean_unigram.txt"
        bi_clean = reports_dir / "ngrams" / f"{lang}_clean_bigram.txt"
        uni = uni_clean if uni_clean.exists() else (reports_dir / "ngrams" / f"{lang}_unigram.txt")
        bi = bi_clean if bi_clean.exists() else (reports_dir / "ngrams" / f"{lang}_bigram.txt")

        summary[lang] = {
            "input": input_n,
            "dropped": dropped_n,
            "kept": kept_n,
            "has_clean": clean.exists(),
            "ngrams": {
                "unigram": str(uni.relative_to(root)) if uni.exists() else None,
                "bigram": str(bi.relative_to(root)) if bi.exists() else None,
            },
            "residual_report": str(res_file.relative_to(root)) if res_file.exists() else None,
        }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Sprint-3 summary saved to {out_json}")

if __name__ == "__main__":
    main()