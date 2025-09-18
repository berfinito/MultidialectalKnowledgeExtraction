"""
Compute character-level confusion matrices (ê→e, î→i, û→u etc.).

Input:
- Pred JSONL with 'ref' and 'pred_raw' (or similar) fields

Output:
- JSON dict: {'ê->e': count, ..., 'total': N}

Notes:
- Counts are naive char occurrences in aligned (ref, hyp) pairs
- Extend 'pairs' to cover additional characters as needed
"""
import json
import argparse
from collections import Counter

def load_jsonl(path):
    """Yield JSONL rows from file path."""
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def char_confusion(refs, hyps, pairs):
    """Count target replacements across aligned ref/hyp lists for given pairs."""
    stats = {p: 0 for p in pairs}
    total = 0
    for ref, hyp in zip(refs, hyps):
        for r, h in zip(ref, hyp):
            if r != h and (r, h) in pairs:
                stats[(r, h)] += 1
            total += 1
    return stats, total

def main():
    """CLI wrapper: parse args, load JSONL, compute and write matrix."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    data = load_jsonl(args.pred)
    refs = [d.get("ref", "") for d in data]
    hyps = [d.get("pred_raw", "") for d in data]

    pairs = [("ê", "e"), ("î", "i"), ("û", "u"), ("ş", "s"), ("ç", "c"), ("ö", "o"), ("ü", "u")]
    stats, total = char_confusion(refs, hyps, pairs)
    result = {f"{a}->{b}": stats[(a, b)] for (a, b) in pairs}
    result["total"] = total

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Confusion matrix saved to {args.out}")

if __name__ == "__main__":
    main()