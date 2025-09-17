import argparse, json, math
from pathlib import Path
from typing import List, Dict

def read_jsonl(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if line:
                yield json.loads(line)

def load_items(patterns: List[str]) -> List[Dict]:
    out=[]
    for pat in patterns:
        for fp in Path(".").glob(pat):
            # JSONL beam format mı?
            if fp.suffix == ".jsonl":
                for rec in read_jsonl(fp):
                    hyp = rec.get("pred_text","")
                    ref = rec.get("gt_text","")
                    alt = rec.get("alt_hyps", [])
                    scores = rec.get("beam_scores", [])
                    out.append({
                        "file": str(fp),
                        "hyp": hyp,
                        "ref": ref,
                        "alt_hyps": alt,
                        "beam_scores": scores,
                        "logp_acoustic": rec.get("logp_acoustic"),
                    })
            else:
                # Tekil aggregate JSON (eski)
                data = json.loads(fp.read_text(encoding="utf-8"))
                hyp = data.get("hyp") or data.get("prediction") or ""
                ref = data.get("ref") or data.get("reference") or ""
                out.append({"file": str(fp), "hyp": hyp, "ref": ref, "alt_hyps": [], "beam_scores": [], "logp_acoustic": None})
    return out

def tokenize(s: str) -> List[str]:
    return s.strip().lower().split()

def dummy_lm_score(tokens: List[str]) -> float:
    return -0.3 * len(tokens)  # farklı katsayı

def wer(ref: List[str], hyp: List[str]) -> float:
    n,m=len(ref),len(hyp)
    dp=[[0]*(m+1) for _ in range(n+1)]
    for i in range(1,n+1): dp[i][0]=i
    for j in range(1,m+1): dp[0][j]=j
    for i in range(1,n+1):
        for j in range(1,m+1):
            cost=0 if ref[i-1]==hyp[j-1] else 1
            dp[i][j]=min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    return dp[n][m]/max(1,n)

def rescore(items, lambdas: List[float]):
    """
    Eğer alt_hyps varsa:
      candidates = [best] + alt_hyps
      candidate acoustic score (varsayım): beam_scores paralel (yoksa fallback len-based)
      fused = acoustic + λ * lm_score
      En yüksek fused seçilir → WER ölçülür.
    """
    table=[]
    for lam in lambdas:
        wers=[]
        for it in items:
            ref_tokens = tokenize(it["ref"])
            cands = [it["hyp"]] + list(it.get("alt_hyps", []))
            scores = it.get("beam_scores") or []
            # Acoustic skor yoksa heuristic:
            if not scores or len(scores)!=len(cands):
                scores = [-len(tokenize(c)) for c in cands]
            fused_best = None
            fused_text = cands[0]
            best_val = -1e9
            for cand_text, a_score in zip(cands, scores):
                lm = dummy_lm_score(tokenize(cand_text))
                fused = a_score + lam * lm
                if fused > best_val:
                    best_val = fused
                    fused_best = cand_text
            w = wer(ref_tokens, tokenize(fused_best))
            wers.append(w)
        avg = sum(wers)/len(wers) if wers else 0.0
        table.append({"lambda": lam, "avg_WER": avg})
    return table

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patterns", type=str, default="reports/interim/asr/whisper_*_validation*_beams.jsonl",
                    help="JSONL beam dosyaları veya eski JSON raporu pattern")
    ap.add_argument("--lambdas", type=str, default="0,0.2,0.4,0.6,0.8,1.0")
    ap.add_argument("--out", type=Path, default=Path("reports/analysis/fusion_pilot_results.md"))
    args = ap.parse_args()

    patterns = [p.strip() for p in args.patterns.split(",") if p.strip()]
    items = load_items(patterns)
    lam_list = [float(x) for x in args.lambdas.split(",")]
    table = rescore(items, lam_list)

    lines=["# Shallow Fusion Pilot (JSONL Beam)","","| λ | AvgWER |","|---|--------|"]
    for row in table:
        lines.append(f"| {row['lambda']} | {row['avg_WER']:.4f} |")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[fusion] -> {args.out}  (items={len(items)})")

if __name__ == "__main__":
    main()