from __future__ import annotations
import argparse, re
from pathlib import Path
import pandas as pd
from mdke.utils.io import Paths, ensure_dirs, load_yaml

RESIDUAL_RE = re.compile(
    r"(?i)\b(?:"
    r"thumb|küçükresim|upright|frameless|align|left|right|sağ|sol|center|"
    r"colspan|rowspan|bgcolor|background|style|class|imagesize|plotarea|"
    r"barincrement|legend|bars|scale"
    r")\b"
)

def run(cfg, lang: str, src_sfx: str, dst_sfx: str, write_report: bool) -> str:
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)
    in_pq = paths.processed / f"text_corpus_{lang}{src_sfx}.parquet"
    if not in_pq.exists():
        raise FileNotFoundError(f"Girdi yok: {in_pq}")
    df = pd.read_parquet(in_pq)
    col = "text_norm" if "text_norm" in df.columns else "text"
    if col not in df.columns:
        raise KeyError(f"Metin kolonu bulunamadı: {col}")
    # Non-capturing regex + na=False -> uyarı yok, fillna() gerekmez
    mask = df[col].str.contains(RESIDUAL_RE, na=False)
    dropped = int(mask.sum())
    kept = int((~mask).sum())
    out_pq = paths.processed / f"text_corpus_{lang}{dst_sfx}.parquet"
    df.loc[~mask].reset_index(drop=True).to_parquet(out_pq, index=False)
    print(f"[{lang}] input={len(df)} dropped={dropped} kept={kept} -> {out_pq}")
    if write_report:
        rep_dir = paths.reports / "text_stats"
        rep_dir.mkdir(parents=True, exist_ok=True)
        (rep_dir / f"residual_media_{lang}.txt").write_text(
            f"input={len(df)}\ndropped={dropped}\nkept={kept}\nsource={in_pq}\nout={out_pq}\n",
            encoding="utf-8"
        )
        print(f"[{lang}] report -> {rep_dir / f'residual_media_{lang}.txt'}")
    return str(out_pq)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--lang", required=True, choices=["tr","kmr","zza"])
    ap.add_argument("--src_sfx", default="", help='Kaynak korpus soneki (örn: "_sprint3")')
    ap.add_argument("--dst_sfx", default="_clean", help='Çıkış soneki (örn: "_clean")')
    ap.add_argument("--report", action="store_true", help="Rapor dosyası yaz")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    print(run(cfg, args.lang, args.src_sfx, args.dst_sfx, args.report))

if __name__ == "__main__":
    main()
    