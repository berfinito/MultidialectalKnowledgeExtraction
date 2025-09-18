#!/usr/bin/env python
"""Summarize Sprint-1 results as JSON and MD."""
import json
import pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASR_POST_DIR = ROOT / "data" / "interim" / "asr_post"
REPORTS_DIR = ROOT / "reports"

ALLOWED_BASELINE_SUFFIXES = {
    "",  # truly suffixless
    "DEC-none_FL-auto_beam1_vad0_translit-none",  # baseline-like
}

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue

def detected_lang_stats(jsonl_path: pathlib.Path):
    n = 0
    ctr = Counter()
    prob_sum = 0.0
    for row in load_jsonl(jsonl_path):
        n += 1
        lang = row.get("detected_language")
        if lang:
            ctr[lang] += 1
        p = row.get("detected_lang_prob")
        if isinstance(p, (int, float)):
            prob_sum += p
    return {
        "n_items": n,
        "detected_language_dist": dict(ctr.most_common()),
        "detected_language_avg_prob": (prob_sum / n) if n else None,
    }

def parse_variant(name: str):
    stem = name.replace(".jsonl", "")
    parts = stem.split("_")
    lang = parts[1] if len(parts) > 1 else "unk"
    split = parts[2] if len(parts) > 2 else "unk"
    suffix = "_".join(parts[3:]) if len(parts) > 3 else ""
    return stem, lang, split, suffix

def score(metrics: dict):
    if not isinstance(metrics, dict):
        return float("inf")
    wr = metrics.get("wer_raw")
    return wr if isinstance(wr, (int, float)) else float("inf")

def main():
    summary = {}

    for jsonl in sorted(ASR_POST_DIR.glob("whisperct2_*.jsonl")):
        stem, lang, split, suffix = parse_variant(jsonl.name)
        if suffix not in ALLOWED_BASELINE_SUFFIXES:
            continue
        report = REPORTS_DIR / f"asr_{jsonl.stem}.json"
        entry = {
            "jsonl": str(jsonl.relative_to(ROOT)),
            "report": str(report.relative_to(ROOT)) if report.exists() else None,
            "variant_suffix": suffix or "default",
        }
        if report.exists():
            try:
                entry["metrics"] = load_json(report)
            except Exception:
                entry["metrics"] = {"error": "failed to load report"}
        else:
            entry["metrics"] = {"status": "report missing"}
        entry["detected_language"] = detected_lang_stats(jsonl)
        summary[jsonl.stem] = entry

    best = None
    for run_name, entry in summary.items():
        sc = score(entry.get("metrics", {}))
        if sc != float("inf"):
            if best is None or sc < best[1]:
                best = (run_name, sc)
    if best:
        summary["_best_baseline"] = {"run": best[0], "score": best[1]}

    out_path = REPORTS_DIR / "sprint-1-summary.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Sprint-1 summary saved to {out_path}")

if __name__ == "__main__":
    main()