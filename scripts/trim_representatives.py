#!/usr/bin/env python
"""
Trim representative term lists (e.g., keep top-15) for interpretable summaries.

Outputs:
  - reports/analysis/representatives_{lang}_{variant}_top15.md
"""
import argparse, re
from pathlib import Path

HDR = re.compile(r"^##\s+Topic\s+(\d+)\s+\|")

def trim(in_md: Path, out_md: Path, keep: int):
    lines = in_md.read_text(encoding="utf-8").splitlines()
    blocks = []
    cur = []
    count = 0
    for line in lines:
        if HDR.match(line.strip()):
            if cur:
                blocks.append(cur)
            cur = [line]
        else:
            if cur:
                cur.append(line)
    if cur:
        blocks.append(cur)
    trimmed = blocks[:keep]
    out_lines = [f"# Representatives - trimmed top{keep}", ""]
    for b in trimmed:
        out_lines.extend(b)
        if b and b[-1].strip() != "":
            out_lines.append("")
    out_md.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"[trim] {in_md.name} -> {out_md} (topics={len(trimmed)})")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_md", type=Path, required=True)
    ap.add_argument("--out_md", type=Path, required=True)
    ap.add_argument("--topk", type=int, default=15)
    args = ap.parse_args()
    trim(args.in_md, args.out_md, args.topk)

if __name__ == "__main__":
    main()