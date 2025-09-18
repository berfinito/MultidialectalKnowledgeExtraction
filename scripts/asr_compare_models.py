#!/usr/bin/env python
"""
Compare ASR model variants (e.g., medium vs large-v2) over existing JSON reports.

Inputs:
  - Glob patterns for reports/asr_whisper_*_{medium,large}.json
Outputs:
  - reports/asr_compare_medium_large.md  (detailed deltas)
  - reports/asr_best_medium_large.md     (short best-per-lang summary)

Notes:
- WER/CER/RTF pulled from per-run JSONs.
- Baseline can be chosen via CLI (default: medium).
"""
import argparse
import glob
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple


def infer_tag(rep: dict, path: str) -> str:
    # 1) Use explicit tag from report if present
    tag = rep.get("tag")
    if isinstance(tag, str) and tag.strip():
        return tag.strip().lower()

    # 2) Infer from model name
    model = (rep.get("model") or "").lower()
    if "whisper-small" in model:
        return "small"
    if "whisper-medium" in model:
        return "medium"
    if "whisper-large" in model:
        return "large"

    # 3) Fallback to file name
    p = path.lower()
    for t in ("small", "medium", "large"):
        if f"_{t}.json" in p or f"_{t}_" in p:
            return t

    return "unknown"


def load_reports(patterns: List[str]):
    items = []
    seen: Set[str] = set()
    for pattern in patterns:
        for p in sorted(glob.glob(pattern)):
            if p in seen:
                continue
            seen.add(p)
            with open(p, "r", encoding="utf-8") as f:
                rep = json.load(f)
            lang = rep.get("lang")
            split = rep.get("split")
            tag = infer_tag(rep, p)
            items.append(((lang, split, tag), rep, p))
    return items


def fmt(x) -> str:
    try:
        return f"{float(x):.3f}"
    except Exception:
        return "-"


def order_tags(baseline: str, tags: Set[str]) -> List[str]:
    baseline = (baseline or "").lower().strip()
    canonical = ["small", "medium", "large"]
    rest = [t for t in canonical if t in tags and t != baseline]
    # Add any non-canonical tags (e.g., custom) at the end alphabetically
    others = sorted(t for t in tags if t not in set([baseline] + canonical))
    ordered = []
    # Baseline'i her zaman ilk sütun yap; mevcut değilse de sütun olarak göster
    ordered.append(baseline if baseline else "baseline")
    ordered.extend(rest)
    ordered.extend(others)
    # Tekrarlı olmasın
    seen = set()
    deduped = []
    for t in ordered:
        if t not in seen:
            deduped.append(t)
            seen.add(t)
    return deduped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--patterns",
        nargs="+",
        required=True,
        help="Birden çok pattern ver: reports/asr_whisper_*_*_small.json reports/asr_whisper_*_*_medium.json ...",
    )
    ap.add_argument(
        "--baseline",
        default="medium",
        help="Karşılaştırma tabanı (tag): small|medium|large|<custom>",
    )
    ap.add_argument("--out", default="reports/asr_compare_small_medium_large.md")
    ap.add_argument(
        "--best-out",
        default=None,
        help="Opsiyonel: En iyi (WER, sonra CER, sonra RTF) tag'i seçen kompakt tabloyu bu dosyaya da yaz.",
    )
    args = ap.parse_args()

    rows = load_reports(args.patterns)
    if not rows:
        print("No reports matched given patterns.")
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text("No data.\n", encoding="utf-8")
        print(f"\nSaved → {args.out}")
        return

    # (lang, split, tag) -> rep
    by_key: Dict[Tuple[str, str, str], dict] = {k: rep for (k, rep, _p) in rows}

    # (lang, split) -> set(tags)
    ls_tags: Dict[Tuple[str, str], Set[str]] = {}
    for (lang, split, tag), _rep, _p in rows:
        ls_tags.setdefault((lang, split), set()).add(tag)

    # Gather all tags and put baseline first for column order
    found_tags = {tag for (_lang, _split, tag), _rep, _p in rows}
    all_tags = order_tags(args.baseline, found_tags)

    # Wide table
    lines: List[str] = []
    header = ["lang", "split", "n"]
    for tag_name in all_tags:
        header += [f"WER_{tag_name}", f"CER_{tag_name}", f"RTF_{tag_name}"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")

    for (lang, split), tags in sorted(ls_tags.items(), key=lambda x: (str(x[0][0]), str(x[0][1]))):
        # Pick n from baseline if exists, else any available tag for that (lang, split)
        n_val = "-"
        base_rep = by_key.get((lang, split, args.baseline))
        if base_rep:
            n_val = base_rep.get("n", "-")
        else:
            for tag_name in all_tags:
                r = by_key.get((lang, split, tag_name))
                if r:
                    n_val = r.get("n", "-")
                    break

        row = [str(lang), str(split), str(n_val)]
        for tag_name in all_tags:
            rep = by_key.get((lang, split, tag_name))
            if rep:
                row += [fmt(rep.get("wer")), fmt(rep.get("cer")), fmt(rep.get("rtf"))]
            else:
                row += ["-", "-", "-"]
        lines.append("| " + " | ".join(row) + " |")

    # Delta table vs baseline
    lines.append("\n\n")
    lines.append(f"### Deltas (baseline={args.baseline})")
    lines.append("| lang | split | compare | ΔWER | ΔWER% | ΔCER | ΔCER% | ΔRTF | ΔRTF% |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|")

    for (lang, split), tags in sorted(ls_tags.items(), key=lambda x: (str(x[0][0]), str(x[0][1]))):
        base = by_key.get((lang, split, args.baseline))
        if not base:
            continue
        bw, bc, br = base.get("wer"), base.get("cer"), base.get("rtf")
        try:
            bwf, bcf, brf = float(bw), float(bc), float(br)
        except Exception:
            continue

        for tag_name in [t for t in all_tags if t != args.baseline]:
            if tag_name not in tags:
                continue
            rep = by_key.get((lang, split, tag_name))
            if not rep:
                continue
            try:
                lwf, lcf, lrf = float(rep.get("wer")), float(rep.get("cer")), float(rep.get("rtf"))
            except Exception:
                continue
            dwer = lwf - bwf
            dwer_rel = (dwer / bwf) * 100.0 if bwf else float("nan")
            dcer = lcf - bcf
            dcer_rel = (dcer / bcf) * 100.0 if bcf else float("nan")
            drtf = lrf - brf
            drtf_rel = (drtf / brf) * 100.0 if brf else float("nan")
            lines.append(
                f"| {lang} | {split} | {tag_name} | {dwer:.3f} | {dwer_rel:.1f}% | {dcer:.3f} | {dcer_rel:.1f}% | {drtf:.3f} | {drtf_rel:.1f}% |"
            )

    out = "\n".join(lines) + "\n"
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(out, encoding="utf-8")
    print(out)
    print(f"\nSaved → {args.out}")

    # Compact best-per-(lang, split) table
    if args.best_out:
        best_lines: List[str] = []
        best_lines.append("| lang | split | best | WER | CER | RTF | baseline | ΔWER | ΔWER% | ΔCER | ΔCER% | ΔRTF | ΔRTF% |")
        best_lines.append("|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|")

        for (lang, split), tags in sorted(ls_tags.items(), key=lambda x: (str(x[0][0]), str(x[0][1]))):
            # pick best by (WER, CER, RTF) tuple
            best_tag = None
            best_tuple = None  # (wer, cer, rtf)
            for tag_name in tags:
                rep = by_key.get((lang, split, tag_name))
                if not rep:
                    continue
                try:
                    tup = (float(rep.get("wer")), float(rep.get("cer")), float(rep.get("rtf")))
                except Exception:
                    continue
                if best_tuple is None or tup < best_tuple:
                    best_tuple = tup
                    best_tag = tag_name

            if best_tag is None:
                continue

            rep_best = by_key[(lang, split, best_tag)]
            bw, bc, br = rep_best.get("wer"), rep_best.get("cer"), rep_best.get("rtf")

            # deltas vs baseline
            base_rep = by_key.get((lang, split, args.baseline))
            if base_rep:
                try:
                    bwf, bcf, brf = float(base_rep.get("wer")), float(base_rep.get("cer")), float(base_rep.get("rtf"))
                    lwf, lcf, lrf = float(bw), float(bc), float(br)
                    dwer = lwf - bwf
                    dwer_rel = (dwer / bwf) * 100.0 if bwf else float("nan")
                    dcer = lcf - bcf
                    dcer_rel = (dcer / bcf) * 100.0 if bcf else float("nan")
                    drtf = lrf - brf
                    drtf_rel = (drtf / brf) * 100.0 if brf else float("nan")
                    delta_cells = [
                        f"{dwer:.3f}",
                        f"{dwer_rel:.1f}%",
                        f"{dcer:.3f}",
                        f"{dcer_rel:.1f}%",
                        f"{drtf:.3f}",
                        f"{drtf_rel:.1f}%",
                    ]
                    base_name = args.baseline
                except Exception:
                    delta_cells = ["-", "-", "-", "-", "-", "-"]
                    base_name = args.baseline
            else:
                delta_cells = ["-", "-", "-", "-", "-", "-"]
                base_name = "-"

            best_lines.append(
                "| "
                + " | ".join(
                    [
                        str(lang),
                        str(split),
                        best_tag,
                        fmt(bw),
                        fmt(bc),
                        fmt(br),
                        base_name,
                        *delta_cells,
                    ]
                )
                + " |"
            )

        best_out = "\n".join(best_lines) + "\n"
        Path(args.best_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.best_out).write_text(best_out, encoding="utf-8")
        print("\n" + best_out)
        print(f"Saved → {args.best_out}")


if __name__ == "__main__":
    main()