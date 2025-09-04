import json
import pathlib

def main():
    summary_path = pathlib.Path("reports/sprint-2-summary.json")
    if not summary_path.exists():
        print("Sprint-2 summary JSON not found.")
        return

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    md = ["# Sprint-2 Summary", ""]

    for run_name, entry in summary.items():
        if run_name.startswith("_"):
            continue
        md.append(f"## {run_name}")
        # Variant suffix (DEC/FL/beam/vad/translit for CT2)
        parts = run_name.split("_")
        suffix = "_".join(parts[3:]) if len(parts) > 3 else ""
        md.append(f"- variant: {suffix or 'default'}")
        md.append(f"- jsonl: {entry.get('jsonl')}")
        md.append(f"- report: {entry.get('report') or 'MISSING'}")
        det = entry.get("detected_language", {})
        n = det.get("n_items"); avgp = det.get("detected_language_avg_prob")
        dist = det.get("detected_language_dist", {})
        md.append(f"- items: {n}, avg_prob: {avgp}")
        if dist:
            top = ', '.join([f"{k}:{v}" for k, v in list(dist.items())[:8]])
            md.append(f"- detected_language (top): {top}")
        mets = entry.get("metrics", {})
        if isinstance(mets, dict):
            wer = mets.get("wer_raw") if mets.get("wer_raw") is not None else mets.get("wer")
            cer = mets.get("cer_raw") if mets.get("cer_raw") is not None else mets.get("cer")
            cer_t = mets.get("cer_translit"); rtf = mets.get("rtf")
            md.append(f"- metrics: WER={wer} CER={cer} CER_t={cer_t} RTF={rtf}")
        md.append("")

    best = summary.get("_best_combo")
    if isinstance(best, dict):
        md.append("## Best combo (global)")
        md.append(f"- run: {best.get('run')}")
        md.append(f"- score: {best.get('score')}")
        md.append("")

    bpl = summary.get("_best_per_lang")
    if isinstance(bpl, dict) and bpl:
        md.append("## Best per language")
        for lang, obj in bpl.items():
            md.append(f"- {lang}: {obj.get('run')} (score={obj.get('score')})")
        md.append("")

    out_path = pathlib.Path("reports/sprint-2-summary.md")
    out_path.write_text("\n".join(md), encoding="utf-8")
    print(f"Sprint-2 markdown saved to {out_path}")

if __name__ == "__main__":
    main()