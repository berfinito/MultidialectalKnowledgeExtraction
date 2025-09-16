import argparse, subprocess, sys
from pathlib import Path

def extract_body(markdown: str) -> str:
    # En üstteki başlık satır(lar)ını düşür (ör. "# Topic Coherence")
    lines = markdown.splitlines()
    i = 0
    # Başlangıçtaki boş satırları atla
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    # Üstte ardışık başlık satırları varsa (# veya ## ile başlayan), atla
    while i < len(lines) and lines[i].lstrip().startswith("#"):
        i += 1
    # Bir sonraki tek boş satırı da atla (varsa)
    if i < len(lines) and lines[i].strip() == "":
        i += 1
    return "\n".join(lines[i:])

def append_if_exists(lines, path: Path, title: str):
    if path.exists():
        # Kendi başlığımızı tek sefer ekleyelim
        lines.append(f"## {title}")
        lines.append("")
        body = extract_body(path.read_text(encoding="utf-8"))
        lines.extend(body.splitlines())
        lines.append("")
    else:
        lines.append(f"<!-- Missing: {path} -->")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis_dir", type=Path, default=Path("reports/analysis"))
    ap.add_argument("--out", type=Path, default=Path("reports/analysis/thesis_tables.md"))
    # İsterseniz coverage'ı varsayılanlara dahil edin:
    ap.add_argument("--include", type=str, default="topic_coherence.md,keyword_overlap.md,keyword_coverage.md")
    args = ap.parse_args()
    args.analysis_dir.mkdir(parents=True, exist_ok=True)
    files = [f.strip() for f in args.include.split(",") if f.strip()]
    lines = ["# Tez Tabloları", ""]
    for f in files:
        # Görsel başlık: dosya adından türet
        title = f.replace(".md","").replace("_"," ").title()
        append_if_exists(lines, args.analysis_dir / f, title)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[thesis] -> {args.out}")

if __name__ == "__main__":
    main()