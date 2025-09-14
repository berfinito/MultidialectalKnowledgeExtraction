from __future__ import annotations
import argparse
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from mdke.utils.io import Paths, ensure_dirs, load_yaml, save_jsonl, get_logger
from mdke.utils.metrics import token_split, latin_hawar_ratio
from mdke.utils.textnorm import normalize_text  # <-- yeni

def run(cfg, lang: str = "zza", limit_files: int | None = None, min_tokens: int = 5, tag: str = ""):
    assert lang == "zza", "Zazagorani ingestor only supports ZZA."
    logger = get_logger("zazagorani_ingest")

    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)

    src_dir = paths.raw / "zazagorani/zza"
    files = sorted([p for p in src_dir.glob("*.txt") if p.is_file()])
    if limit_files:
        files = files[:limit_files]

    out_tag = f"_{tag}" if tag else ""
    out_jsonl = paths.interim / f"text/zazagorani_{lang}{out_tag}.jsonl"
    out_parquet = paths.processed / f"zazagorani_{lang}{out_tag}.parquet"
    out_csv = paths.processed / f"zazagorani_{lang}{out_tag}.csv"

    items = []
    skipped_short = 0
    for p in tqdm(files, desc="zazagorani"):
        txt = p.read_text(encoding="utf-8", errors="ignore").strip()
        toks = token_split(txt)
        if len(toks) < min_tokens:
            skipped_short += 1
            continue
        items.append({
            "doc_id": p.stem,
            "lang": lang,
            "source": "zazagorani",
            "text": txt,
            "text_norm": normalize_text(txt, "zza"),  # <-- güncellendi
            "n_chars": len(txt),
            "n_tokens": len(toks),
            "path": str(p),
        })

    save_jsonl(items, out_jsonl)
    df = pd.DataFrame(items)
    try:
        out_parquet.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out_parquet, index=False)
        written = str(out_parquet)
    except Exception:
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_csv, index=False)
        written = str(out_csv)

    lh = float(latin_hawar_ratio([it["text"] for it in items]))
    logger.info(f"Files={len(files)} Kept={len(items)} Short={skipped_short} latin_hawar={lh:.3f}")
    logger.info(f"JSONL -> {out_jsonl}")
    logger.info(f"Table -> {written}")
    return {"n_files": len(files), "kept": len(items), "skipped_short": skipped_short, "latin_hawar_ratio": lh, "out": {"jsonl": str(out_jsonl), "table": written}}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--limit_files", type=int, default=None)
    ap.add_argument("--min_tokens", type=int, default=5)
    ap.add_argument("--tag", type=str, default="")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    res = run(cfg, "zza", args.limit_files, args.min_tokens, args.tag)
    print(res)

if __name__ == "__main__":
    main()