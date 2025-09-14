from __future__ import annotations
import argparse
from pathlib import Path
import json
from mdke.utils.io import Paths, ensure_dirs, load_yaml

LANGS = ["tr", "kmr", "zza"]

def run(cfg_path: Path, md_path: Path | None = None):
    cfg = load_yaml(cfg_path)
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)
    # Özet var mı? (okunmazsa hata verir; burada sadece varlık kontrolü gibi)
    _ = json.loads((paths.reports / "sprint-4-summary.json").read_text(encoding="utf-8"))

    md_file = md_path or (paths.reports / "sprint-4-summary.md")
    md_file.parent.mkdir(parents=True, exist_ok=True)
    existing = md_file.read_text(encoding="utf-8") if md_file.exists() else ""

    header = "## Final artefaktlar"
    if header in existing:
        print(f"Section already present -> {md_file}")
        return

    lines = []
    lines.append("\n## Final artefaktlar\n")
    for lang in LANGS:
        lines.append(f"### {lang.upper()}\n")
        lines.append(f"- Paragraflar (final): `data/processed/text_corpus_{lang}_final.parquet`")
        lines.append(f"- Cümleler (final): `data/processed/text_sentences_{lang}_final.parquet`")
        lines.append(f"- Düz metin export: `reports/exports/sentences_{lang}_final.txt`\n")

    with md_file.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Appended final artefacts -> {md_file}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--md", type=Path, default=None)
    args = ap.parse_args()
    run(args.config, args.md)