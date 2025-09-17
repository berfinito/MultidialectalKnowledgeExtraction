"""
MT Pilot Quality Evaluator

Beklenen input:
  --src refs.txt (her satırda orijinal lehçe cümle)
  --hyp mt_tr.txt (aynı sıra ile TR pivot çeviriler)
Ölçümler:
  - ChrF (sacrebleu varsa)
  - BLEU (sacrebleu varsa)
  - Ortalama cümle uzunluğu (ref/hyp)
"""
import argparse
from pathlib import Path

def load_lines(p: Path):
    return [l.rstrip("\n") for l in p.read_text(encoding="utf-8").splitlines()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", type=Path, required=True)
    ap.add_argument("--hyp", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("reports/analysis/mt_pilot_quality.md"))
    args = ap.parse_args()

    refs = load_lines(args.ref)
    hyps = load_lines(args.hyp)
    assert len(refs) == len(hyps), "Ref/Hyp satır sayısı eşleşmiyor"

    try:
        import sacrebleu
        bleu = sacrebleu.corpus_bleu(hyps, [refs])
        chrf = sacrebleu.corpus_chrf(hyps, [refs])
        bleu_score = bleu.score
        chrf_score = chrf.score
    except Exception:
        bleu_score = None
        chrf_score = None

    avg_ref_len = sum(len(r.split()) for r in refs)/len(refs)
    avg_hyp_len = sum(len(h.split()) for h in hyps)/len(hyps)

    lines = [
        "# MT Pilot Quality",
        "",
        f"Toplam cümle: {len(refs)}",
        f"Avg ref len: {avg_ref_len:.2f}",
        f"Avg hyp len: {avg_hyp_len:.2f}",
        f"BLEU: {bleu_score:.2f}" if bleu_score is not None else "BLEU: (sacrebleu yok)",
        f"ChrF: {chrf_score:.2f}" if chrf_score is not None else "ChrF: (sacrebleu yok)",
        "",
        "Eşik Önerisi: ChrF > 40 sağlanırsa full drift deneyine geç."
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[mt-pilot] -> {args.out}")

if __name__ == "__main__":
    main()