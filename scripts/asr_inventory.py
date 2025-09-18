#!/usr/bin/env python
"""
Inventory and sanity checks for ASR runs.

- Enumerates data/interim/asr/*.jsonl and reports/asr_whisper_*.json
- Optionally prints summary tables and missing runs
- Serves as an entrypoint for cleanup/export helpers
"""

import json
import pathlib
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASR_POST_DIR = ROOT / "data" / "interim" / "asr_post"
REPORTS_DIR = ROOT / "reports"

def load_jsonl(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue

def summarize_jsonl(path: pathlib.Path):
    n = 0
    lang_counter = Counter()
    prob_sum = 0.0
    for row in load_jsonl(path):
        n += 1
        lang = row.get("detected_language")
        if lang:
            lang_counter[lang] += 1
        prob = row.get("detected_lang_prob")
        if isinstance(prob, (int, float)):
            prob_sum += prob
    avg_prob = (prob_sum / n) if n > 0 else None
    return {
        "n_items": n,
        "detected_language_dist": dict(lang_counter.most_common()),
        "detected_language_avg_prob": avg_prob,
    }

def parse_variant_from_jsonl_name(name: str):
    # Examples:
    # whisperct2_kmr_validation.jsonl
    # whisperct2_kmr_validation_DEC-none_FL-tr_beam5_vad1_translit-none.jsonl
    base = name.replace(".jsonl", "")
    parts = base.split("_")
    # whisperct2, {lang}, {split}, [suffix...]
    lang = parts[1] if len(parts) > 1 else "unk"
    split = parts[2] if len(parts) > 2 else "unk"
    suffix = "_".join(parts[3:]) if len(parts) > 3 else ""
    return lang, split, suffix

def expected_report_for_jsonl(jsonl: pathlib.Path):
    # reports/asr_ + jsonl.stem + .json
    return REPORTS_DIR / f"asr_{jsonl.stem}.json"

def expected_confusion_for_jsonl(jsonl: pathlib.Path):
    lang, _split, suffix = parse_variant_from_jsonl_name(jsonl.name)
    if suffix:
        name = f"confusion_{lang}_{suffix}.json"
    else:
        # fallback if no decorated suffix; keep it explicit by split
        # e.g., whisperct2_kmr_validation.jsonl -> confusion_kmr_validation.json
        parts = jsonl.stem.split("_")
        split = parts[2] if len(parts) > 2 else "unk"
        name = f"confusion_{lang}_{split}.json"
    return REPORTS_DIR / name

def load_json(path: pathlib.Path):
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def main():
    ASR_POST_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    jsonls = sorted(ASR_POST_DIR.glob("whisperct2_*.jsonl"))
    index = []
    missing_confusion_cmds = []

    for j in jsonls:
        lang, split, suffix = parse_variant_from_jsonl_name(j.name)
        rep = expected_report_for_jsonl(j)
        conf = expected_confusion_for_jsonl(j)

        # JSONL stats
        jl_stats = summarize_jsonl(j)

        # Report metrics (if any)
        rep_data = load_json(rep)
        metrics = {}
        if isinstance(rep_data, dict):
            # pick commonly used keys if present
            for k in [
                "n", "wer_raw", "cer_raw", "wer_translit", "cer_translit",
                "latin_hawar_ratio_raw", "latin_hawar_ratio_translit",
                "rtf", "force_lang_effective"
            ]:
                if k in rep_data:
                    metrics[k] = rep_data[k]

        has_confusion = conf.exists()
        if not has_confusion:
            # prepare a command to fill it
            cmd = (
                f"python scripts/make_char_confusion.py "
                f"--pred {j.as_posix()} "
                f"--out {conf.as_posix()}"
            )
            missing_confusion_cmds.append(cmd)

        index.append({
            "run_name": j.stem,
            "lang": lang,
            "split": split,
            "suffix": suffix,
            "jsonl_path": str(j.relative_to(ROOT)),
            "report_path": (str(rep.relative_to(ROOT)) if rep.exists() else None),
            "confusion_path": (str(conf.relative_to(ROOT)) if conf.exists() else None),
            "has_report": rep.exists(),
            "has_confusion": conf.exists(),
            "jsonl_stats": jl_stats,
            "report_metrics": metrics,
        })

    out_json = REPORTS_DIR / "asr_index.json"
    out_json.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    # Minimal markdown view
    lines = ["# ASR Run Index", ""]
    for item in index:
        lines.append(f"## {item['run_name']}")
        lines.append(f"- lang/split: {item['lang']}/{item['split']}")
        lines.append(f"- report: {item['report_path'] or 'MISSING'}")
        lines.append(f"- confusion: {item['confusion_path'] or 'MISSING'}")
        jl = item["jsonl_stats"]
        dl = jl.get("detected_language_dist", {})
        lines.append(f"- n_items: {jl.get('n_items')}, avg_prob: {jl.get('detected_language_avg_prob')}")
        if dl:
            top = ', '.join([f"{k}:{v}" for k, v in list(dl.items())[:5]])
            lines.append(f"- detected_language (top): {top}")
        mets = item["report_metrics"]
        if mets:
            wer = mets.get("wer_raw")
            cer = mets.get("cer_raw")
            cer_t = mets.get("cer_translit")
            rtf = mets.get("rtf")
            lines.append(f"- metrics: WER={wer} CER={cer} CER_t={cer_t} RTF={rtf}")
        lines.append("")
    out_md = REPORTS_DIR / "asr_index.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")

    # Print missing confusion commands for convenience
    if missing_confusion_cmds:
        print("Missing confusions. Run these to fill them:")
        for c in missing_confusion_cmds:
            print(c)
    else:
        print("All confusions present.")

    print(f"Wrote {out_json} and {out_md}")

if __name__ == "__main__":
    main()