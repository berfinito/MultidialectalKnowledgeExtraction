# scripts/asr_bias_effect.py
import json, pathlib, sys

def load(p): return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))

if len(sys.argv)<3:
    print("Usage: python scripts/asr_bias_effect.py <report_off.json> <report_on.json>")
    sys.exit(1)

off, on = load(sys.argv[1]), load(sys.argv[2])

def pick(d): 
    return {k:d.get(k) for k in ("lang","n","wer","cer","rtf","latin_hawar_ratio")}

print("OFF:", pick(off))
print(" ON:", pick(on))
def delta(a,b): return {k: (b.get(k)-a.get(k) if isinstance(a.get(k),(int,float)) else None) 
                        for k in ("wer","cer","rtf","latin_hawar_ratio")}
print("Δ (ON - OFF):", delta(off,on))