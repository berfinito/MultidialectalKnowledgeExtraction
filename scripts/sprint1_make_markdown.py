#!/usr/bin/env python
"""Generate Sprint-1 markdown report from produced artefacts."""

import json
import pathlib

def main():
    summary_path = pathlib.Path("reports/sprint-1-summary.json")
    if not summary_path.exists():
        print("Sprint-1 summary JSON not found.")
        return

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    md = ["# Sprint-1 Summary", ""]

    for run_name, entry in summary.items():
        if run_name.startswith("_"):
            continue
        md.append(f"## {run_name}")
        md.append(f"- variant: {entry.get('variant_suffix','default')}")
        md.append(f"- jsonl: {entry.get('jsonl')}")
        md.append(f"- report: {entry.get('report') or 'MISSING'}")
        det = entry.get("detected_language", {})
        md.append(f"- items: {det.get('n_items')}, avg_prob: {det.get('detected_language_avg_prob')}")
        dist = det.get("detected_language_dist", {})
        if dist:
            top = ', '.join([f"{k}:{v}" for k, v in list(dist.items())[:8]])
            md.append(f"- detected_language (top): {top}")
        mets = entry.get("metrics", {})
        if isinstance(mets, dict):
            wer = mets.get("wer_raw"); cer = mets.get("cer_raw"); rtf = mets.get("rtf")
            md.append(f"- metrics: WER={wer} CER={cer} RTF={rtf}")
        md.append("")

    best = summary.get("_best_baseline")
    if isinstance(best, dict):
        md.append("## Best baseline")
        md.append(f"- run: {best.get('run')}")
        md.append(f"- score: {best.get('score')}")
        md.append("")

    out_path = pathlib.Path("reports/sprint-1-summary.md")
    out_path.write_text("\n".join(md), encoding="utf-8")
    print(f"Sprint-1 markdown saved to {out_path}")

if __name__ == "__main__":
    main()