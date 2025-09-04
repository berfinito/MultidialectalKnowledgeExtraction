import argparse
import json
import pathlib
from typing import Dict, Any, Iterable

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASR_POST_DIR = ROOT / "data" / "interim" / "asr_post"
REPORTS_DIR = ROOT / "reports"
OUT_DIR_DEFAULT = ROOT / "data" / "processed" / "asr_texts"

def load_index() -> Iterable[Dict[str, Any]]:
    idx_path = REPORTS_DIR / "asr_index.json"
    if not idx_path.exists():
        raise SystemExit("Run: python scripts/asr_inventory.py")
    return json.loads(idx_path.read_text(encoding="utf-8"))

def load_jsonl(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue

def choose_text(row: Dict[str, Any], prefer_translit: bool) -> (str, str):
    """Return (text, field_name_used)."""
    if prefer_translit:
        t = row.get("pred_translit")
        if isinstance(t, str) and t.strip():
            return t, "pred_translit"
    t = row.get("pred_raw") or ""
    return t, "pred_raw"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", default="tr,kmr,zza", help="Comma-separated langs")
    ap.add_argument("--splits", default="validation", help="Comma-separated splits")
    ap.add_argument("--prefer-translit", action="store_true", help="Prefer pred_translit over pred_raw")
    ap.add_argument("--out-dir", default=str(OUT_DIR_DEFAULT), help="Output directory")
    # Optional: limit to variants (suffix exact matches, comma-separated). If omitted, include all.
    ap.add_argument("--suffixes", default="", help="Comma-separated exact suffix filters (optional)")
    args = ap.parse_args()

    langs = {s.strip() for s in args.langs.split(",") if s.strip()}
    splits = {s.strip() for s in args.splits.split(",") if s.strip()}
    suffix_filters = {s.strip() for s in args.suffixes.split(",") if s.strip()}

    out_dir = pathlib.Path(args.out_dir)
    per_run_dir = out_dir / "per_run"
    combined_dir = out_dir / "combined"
    per_run_dir.mkdir(parents=True, exist_ok=True)
    combined_dir.mkdir(parents=True, exist_ok=True)

    index = load_index()

    # Prepare combined writers per (lang, split)
    combined_paths = {}
    combined_handles = {}

    def get_combined_handle(lang: str, split: str):
        key = (lang, split)
        if key not in combined_handles:
            p = combined_dir / f"{lang}_{split}.jsonl"
            h = p.open("w", encoding="utf-8")
            combined_paths[key] = p
            combined_handles[key] = h
        return combined_handles[key]

    selected = []
    for it in index:
        if it.get("jsonl_path") is None:
            continue
        lang = it.get("lang")
        split = it.get("split")
        suffix = it.get("suffix") or ""
        if lang not in langs or split not in splits:
            continue
        if suffix_filters and suffix not in suffix_filters:
            continue
        jsonl_path = ROOT / it["jsonl_path"]
        if not jsonl_path.exists():
            continue
        selected.append(it)

    for it in selected:
        lang = it["lang"]
        split = it["split"]
        suffix = it.get("suffix") or "default"
        run_name = it["run_name"]
        jsonl_path = ROOT / it["jsonl_path"]

        # per-run export
        out_run = per_run_dir / f"{run_name}.jsonl"
        n_written = 0
        with out_run.open("w", encoding="utf-8") as out_f:
            for i, row in enumerate(load_jsonl(jsonl_path)):
                text, used_field = choose_text(row, args.prefer_translit)
                rec = {
                    "id": i,
                    "lang": lang,
                    "split": split,
                    "run_name": run_name,
                    "variant_suffix": suffix,
                    "text": text,
                    "text_field": used_field,
                    "ref": row.get("ref"),
                    "detected_language": row.get("detected_language"),
                    "detected_lang_prob": row.get("detected_lang_prob"),
                    "audio": row.get("audio"),
                }
                out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                # combined export
                ch = get_combined_handle(lang, split)
                ch.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_written += 1

        print(f"Wrote {n_written} lines to {out_run.relative_to(ROOT)}")

    # Close combined handles
    for h in combined_handles.values():
        h.close()
    if combined_paths:
        for (lang, split), p in combined_paths.items():
            print(f"Combined -> {p.relative_to(ROOT)}")

if __name__ == "__main__":
    main()