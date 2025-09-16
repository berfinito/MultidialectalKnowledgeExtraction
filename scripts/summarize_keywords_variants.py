from pathlib import Path
import json, re, unicodedata, sys

langs = sys.argv[1].split(",") if len(sys.argv)>1 else ["tr","kmr","zza"]
variants = ["text","cv","both"]

def tr_lower(s: str) -> str:
    return s.replace("I","ı").replace("İ","i").lower()

def norm(t: str) -> str:
    t = unicodedata.normalize("NFKC", t)
    t = tr_lower(t.strip(" \"'‘’“”.,;:!?()[]{}<>~`|/\\"))
    t = re.sub(r"\s+", " ", t).strip()
    return t

def load_pairs(path: Path):
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [(norm(k), float(v)) for k,v in data if norm(k)]

def jaccard(a: set, b: set) -> float:
    if not a and not b: return 1.0
    return len(a & b) / max(1, len(a | b))

base = Path("reports/keywords")
for lang in langs:
    for var in variants:
        kb = load_pairs(base / f"{lang}_keybert_{var}.json")
        yk = load_pairs(base / f"{lang}_yake_{var}.json")
        kb_terms, yk_terms = {k for k,_ in kb}, {k for k,_ in yk}
        jac = jaccard(kb_terms, yk_terms)
        avg_len_kb = sum(len(k) for k,_ in kb)/max(1,len(kb)) if kb else 0
        avg_len_yk = sum(len(k) for k,_ in yk)/max(1,len(yk)) if yk else 0
        print(f"{lang.upper()} {var:<5} | KB {len(kb_terms):>3} (avg={avg_len_kb:.1f}) | "
              f"YAKE {len(yk_terms):>3} (avg={avg_len_yk:.1f}) | Jaccard={jac:.3f}")