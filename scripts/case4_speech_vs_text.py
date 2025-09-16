import re
from pathlib import Path

AN_DIR = Path("reports/analysis")
OUT = AN_DIR / "case4_speech_vs_text.md"

def read(p): return Path(p).read_text(encoding="utf-8").splitlines()

def parse_overlap(lines):
    res, cur_lang, cur_method = {}, None, None
    for i,l in enumerate(lines):
        m = re.match(r"##\s+(\w+)\s+-\s+(keybert|yake)", l.strip(), flags=re.I)
        if m:
            cur_lang = m.group(1).lower(); cur_method = m.group(2).lower()
            res.setdefault(cur_lang, {}).setdefault(cur_method, {})
        if l.strip().startswith("| 0.") or l.strip().startswith("| 1.") or l.strip().startswith("| 0"):
            vals = [v.strip() for v in lines[i].split("|") if v.strip()]
            if cur_lang and cur_method and len(vals)>=1:
                try:
                    res[cur_lang][cur_method]["J_text_cv"] = float(vals[0])
                except:
                    pass
    return res

def parse_coverage(lines):
    res = {}
    header = None
    for l in lines:
        if l.strip().startswith("| Lang |"):
            header = [h.strip().lower() for h in l.strip().split("|") if h.strip()]
            continue
        if header and l.strip().startswith("|"):
            cells = [c.strip() for c in l.strip().split("|") if c.strip()]
            if len(cells) != len(header): continue
            row = dict(zip(header, cells))
            lang = row["lang"].lower()
            method = row["method"].lower()
            var = row["variant"].lower()
            cov = row["covered%"].replace("%","").strip()
            try:
                covf = float(cov)
            except:
                continue
            res.setdefault(lang, {}).setdefault(method, {})[var] = covf
    return res

def main():
    ol = parse_overlap(read(AN_DIR/"keyword_overlap.md"))
    cvg = parse_coverage(read(AN_DIR/"keyword_coverage.md"))
    lines = ["# Case Study 4 — Speech (CV) vs Text", ""]
    for lang in ["tr","kmr","zza"]:
        lines += [f"## {lang.upper()}", ""]
        j = ol.get(lang,{}).get("keybert",{}).get("J_text_cv", None)
        t_cov = cvg.get(lang,{}).get("keybert",{}).get("text", None)
        cv_cov = cvg.get(lang,{}).get("keybert",{}).get("cv", None)
        both_cov = cvg.get(lang,{}).get("keybert",{}).get("both", None)
        lines += [
            "- KeyBERT:",
            f"  - J(text,cv): {j if j is not None else 'NA'}",
            f"  - Coverage% → text: {t_cov if t_cov is not None else 'NA'} | cv: {cv_cov if cv_cov is not None else 'NA'} | both: {both_cov if both_cov is not None else 'NA'}",
            "  - Yorum: text–cv kesişimi çok düşük; cv/both kapsamı yüksek (konuşma verisinde terimler geçiyor).",
            "",
            "- YAKE:",
        ]
        j_y = ol.get(lang,{}).get("yake",{}).get("J_text_cv", None)
        t_cov_y = cvg.get(lang,{}).get("yake",{}).get("text", None)
        cv_cov_y = cvg.get(lang,{}).get("yake",{}).get("cv", None)
        both_cov_y = cvg.get(lang,{}).get("yake",{}).get("both", None)
        lines += [
            f"  - J(text,cv): {j_y if j_y is not None else 'NA'}",
            f"  - Coverage% → text: {t_cov_y if t_cov_y is not None else 'NA'} | cv: {cv_cov_y if cv_cov_y is not None else 'NA'} | both: {both_cov_y if both_cov_y is not None else 'NA'}",
            "  - Yorum: Unigram doğası gereği daha stabil; tamamlayıcılığı KeyBERT daha iyi yansıtıyor.",
            "",
        ]
    lines += [
        "Kaynaklar:",
        "- [reports/analysis/keyword_overlap.md](reports/analysis/keyword_overlap.md)",
        "- [reports/analysis/keyword_coverage.md](reports/analysis/keyword_coverage.md)",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[case4] -> {OUT}")

if __name__ == "__main__":
    main()