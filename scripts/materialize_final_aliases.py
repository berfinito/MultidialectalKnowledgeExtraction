from __future__ import annotations
import argparse
from pathlib import Path
import shutil
from mdke.utils.io import Paths, ensure_dirs, load_yaml

LANGS = ["tr", "kmr", "zza"]

def materialize(cfg_path: Path):
    cfg = load_yaml(cfg_path)
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)

    pairs: list[tuple[Path, Path]] = []
    for lang in LANGS:
        pairs.append((
            paths.processed / f"text_corpus_{lang}_normh_clean_nonav_dedup.parquet",
            paths.processed / f"text_corpus_{lang}_final.parquet",
        ))
        pairs.append((
            paths.processed / f"text_sentences_{lang}_normh_clean_nonav.parquet",
            paths.processed / f"text_sentences_{lang}_final.parquet",
        ))

    copied, missing = 0, []
    for src, dst in pairs:
        if not src.exists():
            missing.append(str(src))
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
        print(f"[final] {src.name} -> {dst.name}")

    print(f"Done. Copied: {copied} | Missing inputs: {len(missing)}")

    if missing:
        print("Missing sources:")
        for m in missing:
            print(f"  - {m}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    args = ap.parse_args()
    materialize(args.config)