"""Fix mojibake / Unicode inconsistencies in source corpora or samples.

Heuristics:
- Detect common mojibake patterns (e.g., 'ÅŸ'→'ş', 'Ã¶'→'ö', etc.)
- Prefer preserving valid TR/KMR/ZZA diacritics listed in GOOD set
- Apply pair-mapped replacements first, then a light cleanup pass

Usage:
  python scripts/fix_mojibake.py IN.txt > OUT.txt
"""
from pathlib import Path
import unicodedata as u
import sys, re

_BAD_RE = re.compile(r"[ÃÅÂ¤Ÿ�]")
_GOOD = set("şŞçÇğĞıİöÖüÜâÂêÊîÎûÛ’ʻʼ`´ʿ’")

_PAIR_MAP = {
    "ÅŸ": "ş", "Å": "Ş",
    "Ã§": "ç", "Ã": "Ç",
    "ÄŸ": "ğ", "Ä": "Ğ",
    "Ä±": "ı", "I\u0307": "İ",
    "Ã¶": "ö", "Ã": "Ö",
    "Ã¼": "ü", "Ã": "Ü",
    "Ã¢": "â", "Ã": "Â",
    "Ãª": "ê", "Ã": "Ê",
    "Ã®": "î", "Ã": "Î",
    "Ã»": "û", "Ã": "Û",
    "Â·": "·", "Â": "",
}

def _pair_cleanup(s: str) -> str:
    """Apply pair replacements once; do not loop to avoid overfixing."""
    for k, v in _PAIR_MAP.items():
        s = s.replace(k, v)
    return s

def _score(s: str) -> float:
    """Score a string by 'good' vs 'bad' character presence; higher is better."""
    bad = len(_BAD_RE.findall(s))
    good = sum(ch in _GOOD for ch in s)
    return good - 2.0 * bad

def _once(s: str):
    """Single pass: try pair cleanup and pick the better scoring variant."""
    cands = [("orig", s)]
    for enc, dec in [("cp1252","utf-8"), ("latin1","utf-8"),
                     ("utf-8","cp1252"), ("utf-8","latin1")]:
        try:
            t = s.encode(enc, errors="strict").decode(dec, errors="strict")
            cands.append((f"{enc}->{dec}", t))
        except Exception:
            pass
    best = s; best_sc = float("-inf")
    for _, t in cands:
        t = u.normalize("NFC", t)
        sc = _score(t)
        if sc > best_sc:
            best, best_sc = t, sc
    return best

def fix_line(s: str) -> str:
    """Fix mojibake in one line; idempotent by design."""
    prev = s
    for _ in range(4):
        cur = _once(prev)
        if cur == prev:
            break
        prev = cur
    cur2 = _pair_cleanup(prev)
    return u.normalize("NFC", cur2)

def fix_file(inp: Path, outp: Path):
    """Process a file line-by-line and write the fixed output."""
    lines = inp.read_text(encoding="utf-8", errors="replace").splitlines()
    fixed = [fix_line(s) for s in lines]
    outp.write_text("\n".join(fixed), encoding="utf-8")

if __name__ == "__main__":
    in_path = Path(sys.argv[1]); out_path = Path(sys.argv[2])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fix_file(in_path, out_path)
    print(f"[fix] {in_path} -> {out_path}")
