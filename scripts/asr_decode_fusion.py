"""
Shallow Fusion Pilot Skeleton.

Not: KenLM entegrasyonu için 'pip install kenlm' gerekir.
Bu iskelet:
1. Var olan ASR JSON sonuçlarını okur (hyp + ref + token olmasa bile text).
2. Opsiyonel LM skorlayıcı (dummy) ile log P_LM tahmini yapar (yer tutucu).
3. Lambda grid üzerinden yeniden skorlar.
4. WER/CER fark tablosu üretir.

Geliştirme:
- KenLM modelini load_kenlm(path) ile entegre edip sequence skorlayıcı ekleyin.
- Şu an dummy_lm_score = -len(tokens)*0.5 gibi basit yer tutucu.
"""
import argparse, json, math
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

def load_hyp_refs(patterns: List[str]) -> List[Dict]:
    out = []
    for pat in patterns:
        for fp in Path(".").glob(pat):
            data = json.loads(fp.read_text(encoding="utf-8"))
            # Beklenen alanlar varsayım: {"hyp": "...", "ref": "..."} (gerekirse uyarlayın)
            hyp = data.get("hyp") or data.get("prediction") or ""
            ref = data.get("ref") or data.get("reference") or ""
            out.append({"file": str(fp), "hyp": hyp, "ref": ref})
    return out

def tokenize(s: str) -> List[str]:
    return s.strip().lower().split()

def dummy_lm_score(tokens: List[str]) -> float:
    # Gerçek LM yerine basit fonksiyon (uzun sekansa daha negatif skor)
    return -0.5 * len(tokens)

def wer(ref: List[str], hyp: List[str]) -> float:
    # Basic dynamic programming
    n, m = len(ref), len(hyp)
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(1, n+1): dp[i][0] = i
    for j in range(1, m+1): dp[0][j] = j
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = 0 if ref[i-1] == hyp[j-1] else 1
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    return dp[n][m] / max(1, n)

def rescore(items, lambdas: List[float]):
    """
    Varsayım:
    Acoustic log P (dummy) = -len(hyp_tokens)
    Fusion: logP = logP_acoustic + λ*logP_LM
    Sadece karşılaştırma amacıyla WER yeniden hesaplanır.
    (Gerçek kullanımda beam candidates gerekir; burada iskelet.)
    """
    table = []
    for lam in lambdas:
        wers = []
        for it in items:
            hyp_tokens = tokenize(it["hyp"])
            ref_tokens = tokenize(it["ref"])
            logP_acoustic = -len(hyp_tokens)  # placeholder
            logP_lm = dummy_lm_score(hyp_tokens)
            fused = logP_acoustic + lam * logP_lm  # skor kullanılmıyor; pipeline gösterimi
            # Burada fused skora göre alternatif hip seçilseydi değişiklik olacaktı.
            w = wer(ref_tokens, hyp_tokens)
            wers.append(w)
        avg = sum(wers)/len(wers) if wers else 0.0
        table.append({"lambda": lam, "avg_WER": avg})
    return table

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json_patterns", type=str, default="reports/asr_whisper_*_validation_medium.json")
    ap.add_argument("--lambdas", type=str, default="0.2,0.4,0.6,0.8,1.0")
    ap.add_argument("--out", type=Path, default=Path("reports/analysis/fusion_pilot_results.md"))
    args = ap.parse_args()

    patterns = [p.strip() for p in args.json_patterns.split(",")]
    items = load_hyp_refs(patterns)
    lam_list = [float(x) for x in args.lambdas.split(",") if x.strip()]
    table = rescore(items, lam_list)

    lines = ["# Shallow Fusion Pilot (Skeleton)", "", "| λ | AvgWER |", "|---|--------|"]
    for row in table:
        lines.append(f"| {row['lambda']} | {row['avg_WER']:.4f} |")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[fusion] -> {args.out}")

if __name__ == "__main__":
    main()