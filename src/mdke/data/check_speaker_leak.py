from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

from mdke.utils.io import load_yaml, Paths, ensure_dirs, get_logger
from mdke.utils.langmap import normalize_lang

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--lang", type=str, required=True, help="tr | kmr | zza (aliases: ku, diq)")
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    logger = get_logger("speaker_leak")

    std_lang = normalize_lang(args.lang)  # tr|kmr|zza
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)

    # parquet dosyalarını oku
    dfs = {}
    for split in ["train", "validation", "test"]:
        fp = paths.processed / f"cv_{std_lang}_{split}.parquet"
        if not fp.exists():
            raise FileNotFoundError(f"Missing processed file: {fp}")
        df = pd.read_parquet(fp, columns=["speaker"])
        dfs[split] = df

    def uniq_speakers(df: pd.DataFrame) -> set[str]:
        return set(df["speaker"].astype(str).tolist())

    s_train = uniq_speakers(dfs["train"])
    s_val   = uniq_speakers(dfs["validation"])
    s_test  = uniq_speakers(dfs["test"])

    inter_train_val = s_train & s_val
    inter_train_test = s_train & s_test
    inter_val_test = s_val & s_test

    report_lines = []
    report_lines.append(f"=== {std_lang} ===")
    report_lines.append(f"train speakers = {len(s_train)}")
    report_lines.append(f"validation speakers = {len(s_val)}")
    report_lines.append(f"test speakers = {len(s_test)}")
    report_lines.append("")
    report_lines.append(f"train ∩ validation = {len(inter_train_val)}")
    report_lines.append(f"train ∩ test        = {len(inter_train_test)}")
    report_lines.append(f"validation ∩ test   = {len(inter_val_test)}")
    report = "\n".join(report_lines)

    out_txt = paths.reports / f"leakage_{std_lang}.txt"
    out_txt.parent.mkdir(parents=True, exist_ok=True)
    out_txt.write_text(report, encoding="utf-8")

    logger.info("Speaker leakage report written → %s", out_txt)
    print(report)

if __name__ == "__main__":
    main()
