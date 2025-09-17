# scripts/fix_mojibake.py
from pathlib import Path
import unicodedata as u
import sys, re

_BAD_RE = re.compile(r"[ÃÅÂ¤Ÿ�]")  # tipik mojibake izleri
_GOOD = set("şŞçÇğĞıİöÖüÜâÂêÊîÎûÛ’ʻʼ`´ʿ’")  # TR+KMR+ZZA’daki diakritikler

# Son-çare düzeltme haritası (sık rastlanan ikililer)
_PAIR_MAP = {
    "ÅŸ": "ş", "Å": "Ş",
    "Ã§": "ç", "Ã": "Ç",
    "ÄŸ": "ğ", "Ä": "Ğ",
    "Ä±": "ı", "I\u0307": "İ",  # noktalı I birleşimi
    "Ã¶": "ö", "Ã": "Ö",
    "Ã¼": "ü", "Ã": "Ü",
    "Ã¢": "â", "Ã": "Â",
    "Ãª": "ê", "Ã": "Ê",
    "Ã®": "î", "Ã": "Î",
    "Ã»": "û", "Ã": "Û",
    "Â·": "·", "Â": "",  # yalın 'Â' zayiatı
}

def _pair_cleanup(s: str) -> str:
    for k, v in _PAIR_MAP.items():
        s = s.replace(k, v)
    return s

def _score(s: str) -> float:
    # iyi harf çok, kötü iz az → yüksek skor
    bad = len(_BAD_RE.findall(s))
    good = sum(ch in _GOOD for ch in s)
    return good - 2.0 * bad

def _once(s: str):
    cands = [("orig", s)]
    for enc, dec in [("cp1252","utf-8"), ("latin1","utf-8"),
                     ("utf-8","cp1252"), ("utf-8","latin1")]:
        try:
            t = s.encode(enc, errors="strict").decode(dec, errors="strict")
            cands.append((f"{enc}->{dec}", t))
        except Exception:
            pass
    # en iyi adayı seç
    best = s; best_sc = float("-inf")
    for _, t in cands:
        t = u.normalize("NFC", t)
        sc = _score(t)
        if sc > best_sc:
            best, best_sc = t, sc
    return best

def fix_line(s: str) -> str:
    # 1) birden çok tur dene (karışık satırlar için)
    prev = s
    for _ in range(4):           # 4 tur genelde yeter
        cur = _once(prev)
        if cur == prev:
            break
        prev = cur
    # 2) son-çare ikili harita temizlik
    cur2 = _pair_cleanup(prev)
    return u.normalize("NFC", cur2)

def fix_file(inp: Path, outp: Path):
    lines = inp.read_text(encoding="utf-8", errors="replace").splitlines()
    fixed = [fix_line(s) for s in lines]
    outp.write_text("\n".join(fixed), encoding="utf-8")

if __name__ == "__main__":
    in_path = Path(sys.argv[1]); out_path = Path(sys.argv[2])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fix_file(in_path, out_path)
    print(f"[fix] {in_path} -> {out_path}")
