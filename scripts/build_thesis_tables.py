"""
Consolidate project results into thesis-ready tables (topics, keywords, KG, case studies).

Inputs:
- reports/analysis/* (case studies, centrality, coverage/overlap)
- reports/topics/*
- reports/keywords/*

Output:
- reports/analysis/thesis_tables.md

Notes:
- This script stitches together selected sections with normalized heading levels.
- It also annotates with the current git commit hash when available.
"""
import argparse
import datetime
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Set

def git_commit_hash() -> str:
    """Return short git commit hash if available, else 'unknown'."""
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"

def expand_items(analysis_dir: Path, include_raw: List[str]) -> List[Path]:
    """Resolve a mixed list of file names and glob patterns into Path list."""
    out: List[Path] = []
    seen: Set[Path] = set()
    for item in include_raw:
        if any(ch in item for ch in ["*", "?", "["]):
            for p in sorted(analysis_dir.glob(item)):
                if p.is_file() and p not in seen:
                    out.append(p)
                    seen.add(p)
        else:
            p = analysis_dir / item
            if p.is_file() and p not in seen:
                out.append(p)
                seen.add(p)
            else:
                # Yine de listede göstermek için placeholder
                if p not in seen:
                    out.append(p)
                    seen.add(p)
    return out

def derive_title(path: Path) -> str:
    """Derive a title from filename for markdown section anchors."""
    name = path.name.replace(".md", "")
    return name.replace("_", " ").title()

def parse_file(path: Path) -> Tuple[str, List[str]]:
    """Read a file and split into title + body lines."""
    if not path.exists():
        return f"Missing: {path.name}", [f"<!-- Missing file: {path.name} -->"]
    lines = path.read_text(encoding="utf-8").splitlines()
    title = None
    body_start = 0
    # Skip initial empties
    while body_start < len(lines) and lines[body_start].strip() == "":
        body_start += 1
    if body_start < len(lines) and lines[body_start].lstrip().startswith("#"):
        raw = lines[body_start].lstrip()
        # Normalize to level 2 heading later
        title = raw.lstrip("# ").strip()
        body_start += 1
        # Skip one blank line after heading
        if body_start < len(lines) and lines[body_start].strip() == "":
            body_start += 1
    if title is None:
        title = derive_title(path)
    body = lines[body_start:]
    return title, body

def normalize_heading_levels(body: List[str], base_level: int = 3) -> List[str]:
    """Shift heading levels so stitched doc remains consistent (### by default)."""
    norm: List[str] = []
    for line in body:
        if line.lstrip().startswith("#"):
            hashes = 0
            for c in line:
                if c == "#":
                    hashes += 1
                else:
                    break
            # Replace with desired level (min 1)
            line = "#" * base_level + " " + line.lstrip("# ").strip()
        norm.append(line)
    return norm

def make_toc(sections: List[Tuple[str, str]]) -> List[str]:
    """Build a small Table of Contents list of bullet links."""
    lines = ["## İçindekiler", ""]
    for anchor, title in sections:
        lines.append(f"- [{title}](#{anchor})")
    lines.append("")
    return lines

def anchor_slug(title: str) -> str:
    """Create a markdown anchor slug from a title string."""
    return (
        title.lower()
        .replace(" ", "-")
        .replace("/", "-")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
        .replace(".", "")
        .replace("?", "")
        .replace(":", "")
        .replace("á", "a")
        .replace("î", "i")
    )

def main():
    """Build and write the consolidated thesis_tables.md."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis_dir", type=Path, default=Path("reports/analysis"))
    ap.add_argument("--out", type=Path, default=Path("reports/analysis/thesis_tables.md"))
    ap.add_argument("--include", type=str,
                    default="topic_coherence.md,keyword_overlap.md,keyword_coverage.md,representatives_tr_both_top15.md,representatives_kmr_both_top15.md,representatives_zza_both_top15.md,case1_*,case2_*,case3_*,case4_*,kg_examples_*.md,kg_interpretation.md,project_execution_summary.md")
    ap.add_argument("--toc", action="store_true", help="İçindekiler tablosu ekle")
    ap.add_argument("--no_metadata", action="store_true", help="Üst metadata bloğunu yazma")
    ap.add_argument("--drop_duplicates", action="store_true", help="Aynı başlık ikinci kez gelirse atla")
    ap.add_argument("--normalize_level", type=int, default=3, help="İç gövde alt başlıkları bu seviyeye çek")
    args = ap.parse_args()

    args.analysis_dir.mkdir(parents=True, exist_ok=True)

    include_items = [x.strip() for x in args.include.split(",") if x.strip()]
    files = expand_items(args.analysis_dir, include_items)

    lines: List[str] = ["# Tez Tabloları", ""]
    if not args.no_metadata:
        lines += [
            "> Build Metadata:",
            f"> - Timestamp: {datetime.datetime.utcnow().isoformat()}Z",
            f"> - Git Commit: {git_commit_hash()}",
            f"> - Source Patterns: {args.include}",
            ""
        ]

    collected_sections: List[Tuple[str, str]] = []
    seen_titles: Set[str] = set()

    for path in files:
        title, body = parse_file(path)
        if args.drop_duplicates and title in seen_titles:
            continue
        seen_titles.add(title)
        anchor = anchor_slug(title)
        collected_sections.append((anchor, title))
        lines.append(f"## {title}")
        lines.append("")
        normalized_body = normalize_heading_levels(body, base_level=args.normalize_level)
        lines.extend(normalized_body)
        lines.append("")

    if args.toc:
        # TOC başta olsun diye sonradan en başına ekliyoruz (metadata'dan sonra)
        # Metadata + başlık sonrası ekleme:
        insertion_index = 2  # Başlık (# Tez Tabloları) ve boş satırdan sonra
        # Eğer metadata yazıldıysa onu atlayıp sonrasına koyalım
        for i, l in enumerate(lines):
            if l.startswith("> Build Metadata"):
                # Metadata bitişini bul
                pass
        # Basit: başlıktan hemen sonra ekleyelim
        toc_block = make_toc(collected_sections)
        lines[2:2] = toc_block  # başlıktan sonra

    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[thesis] wrote {args.out} (sections={len(collected_sections)})")

if __name__ == "__main__":
    main()