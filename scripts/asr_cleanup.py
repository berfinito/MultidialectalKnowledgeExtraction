import argparse, json, pathlib, shutil
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASR_POST = ROOT / "data" / "interim" / "asr_post"
REPORTS = ROOT / "reports"

# Preferred variants to KEEP (exact matches; edit if you add new ones)
KEEP_VARIANTS = [
    "DEC-none_FL-auto_beam5_vad1_translit-strict",
    "DEC-none_FL-tr_beam5_vad1_translit-none",
    "DEC-none_FL-auto_beam1_vad0_translit-none",  # baseline
    "DEC-kmrBias_FL-auto_beam5_vad1_translit-strict",
    "DEC-zzaBias_FL-auto_beam5_vad1_translit-strict",
    "DEC-trBias_FL-auto_beam5_vad1_translit-strict",
    "DECODE-zzaBias",  # legacy cross-dialect decode runs
]

def load_index():
    idx_path = REPORTS / "asr_index.json"
    if not idx_path.exists():
        raise SystemExit("Run: python scripts/asr_inventory.py")
    return json.loads(idx_path.read_text(encoding="utf-8"))

def suffix_key(run):
    s = run.get("suffix") or ""
    try:
        return KEEP_VARIANTS.index(s)
    except ValueError:
        return len(KEEP_VARIANTS) + 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="Dry-run (default)")
    ap.add_argument("--apply", action="store_true", help="Apply moves to _trash")
    ap.add_argument("--keep-tests", action="store_true", help="Also keep test split")
    args = ap.parse_args()
    dry = not args.apply

    index = load_index()
    by_key = defaultdict(list)
    for it in index:
        if it["split"] != "validation" and not args.keep_tests:
            # Only validation by default; tests ignored for KEEP selection
            pass
        by_key[(it["lang"], it["split"])].append(it)

    to_keep = set()
    for key, runs in by_key.items():
        # Keep best-ranked variant(s) + any with missing report for debugging
        chosen = sorted(runs, key=suffix_key)
        seen_suffixes = set()
        for r in chosen:
            s = r.get("suffix") or ""
            if s in seen_suffixes:
                continue
            if s in KEEP_VARIANTS or not r.get("has_report"):
                to_keep.add(r["run_name"])
                seen_suffixes.add(s)

    trash_asr = ASR_POST / "_trash"
    trash_rep = REPORTS / "_trash"
    trash_asr.mkdir(exist_ok=True)
    trash_rep.mkdir(exist_ok=True)

    moves = []
    for it in index:
        rn = it["run_name"]
        jsonl = ROOT / it["jsonl_path"]
        rep = ROOT / (it["report_path"] or "")
        conf = ROOT / (it["confusion_path"] or "")
        if rn in to_keep:
            continue
        if jsonl.exists():
            moves.append((jsonl, trash_asr / jsonl.name))
        if rep and rep.exists():
            moves.append((rep, trash_rep / rep.name))
        if conf and conf.exists():
            moves.append((conf, trash_rep / conf.name))

    if dry:
        print(f"[DRY-RUN] Would move {len(moves)} files to _trash:")
        for src, dst in moves[:50]:
            print("-", src.relative_to(ROOT), "->", dst.relative_to(ROOT))
        if len(moves) > 50:
            print(f"... and {len(moves)-50} more")
        return

    for src, dst in moves:
        try:
            shutil.move(str(src), str(dst))
        except Exception as e:
            print("Move failed:", src, "->", dst, e)
    print(f"Moved {len(moves)} files to _trash")

if __name__ == "__main__":
    main()