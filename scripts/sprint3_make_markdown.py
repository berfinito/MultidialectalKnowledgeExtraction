import json
from pathlib import Path

def head(lines, k=10):
    return [ln.strip() for ln in lines if ln.strip()][:k]

def read_top_lines(p: Path, k=10):
    if not p.exists():
        return []
    try:
        return head(p.read_text(encoding="utf-8").splitlines(), k)
    except UnicodeDecodeError:
        return head(p.read_text(encoding="utf-8", errors="ignore").splitlines(), k)

def main():
    root = Path(".").resolve()
    reports = root / "reports"
    in_json = reports / "sprint-3-summary.json"
    out_md = reports / "sprint-3-summary.md"

    if not in_json.exists():
        print("Sprint-3 summary JSON not found. Run scripts/sprint3_summarize.py first.")
        return

    data = json.loads(in_json.read_text(encoding="utf-8"))
    md = ["# Sprint-3 Summary", ""]
    gen = data.get("_generated_at")
    if gen:
        md.append(f"_generated_at: {gen}_")
        md.append("")

    for lang in ("tr", "kmr", "zza"):
        obj = data.get(lang, {})
        inp = obj.get("input")
        drp = obj.get("dropped")
        kep = obj.get("kept")
        has_clean = obj.get("has_clean")
        uni_path = obj.get("ngrams", {}).get("unigram")
        bi_path = obj.get("ngrams", {}).get("bigram")

        md.append(f"## {lang.upper()}")
        md.append(f"- input: {inp}  dropped: {drp}  kept: {kep}  clean: {has_clean}")
        if uni_path:
            uni_top = read_top_lines(root / uni_path, 10)
            if uni_top:
                md.append("")
                md.append("Top unigramlar:")
                md.extend([f"- {ln}" for ln in uni_top])
        if bi_path:
            bi_top = read_top_lines(root / bi_path, 10)
            if bi_top:
                md.append("")
                md.append("Top bigramlar:")
                md.extend([f"- {ln}" for ln in bi_top])
        md.append("")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"Sprint-3 markdown saved to {out_md}")

if __name__ == "__main__":
    main()