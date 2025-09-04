import json
import pathlib
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASR_POST_DIR = ROOT / "data" / "interim" / "asr_post"
REPORTS_DIR = ROOT / "reports"

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

def score(metrics: dict):
    # Lower is better. Prefer wer_translit > wer_raw > wer (HF)
    if not isinstance(metrics, dict):
        return float("inf")
    for k in ("wer_translit", "wer_raw", "wer"):
        v = metrics.get(k)
        if isinstance(v, (int, float)):
            return v
    return float("inf")

def parse_lang_from_run(run_name: str) -> str:
    parts = run_name.split("_")
    return parts[1] if len(parts) > 1 else "unk"

def add_runs_from_glob(summary: dict, pattern: str):
    for jsonl in sorted(ASR_POST_DIR.glob(pattern)):
        report = REPORTS_DIR / f"asr_{jsonl.stem}.json"
        entry = {
            "jsonl": str(jsonl.relative_to(ROOT)),
            "report": str(report.relative_to(ROOT)) if report.exists() else None,
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

def main():
    summary = {}

    # CT2 runs (all splits)
    add_runs_from_glob(summary, "whisperct2_*.jsonl")

    # Best combo across all runs by WER
    best = None
    for run_name, entry in summary.items():
        sc = score(entry.get("metrics", {}))
        if sc != float("inf"):
            if best is None or sc < best[1]:
                best = (run_name, sc)
    if best:
        summary["_best_combo"] = {"run": best[0], "score": best[1]}

    # Best per language
    best_per_lang = {}
    for run_name, entry in summary.items():
        lang = parse_lang_from_run(run_name)
        sc = score(entry.get("metrics", {}))
        if sc == float("inf"):
            continue
        cur = best_per_lang.get(lang)
        if cur is None or sc < cur["score"]:
            best_per_lang[lang] = {"run": run_name, "score": sc}
    if best_per_lang:
        summary["_best_per_lang"] = best_per_lang

    out_path = REPORTS_DIR / "sprint-2-summary.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Sprint-2 summary saved to {out_path}")

if __name__ == "__main__":
    main()