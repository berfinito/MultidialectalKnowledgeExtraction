# src/mdke/data/ingest_commonvoice.py
from __future__ import annotations
import argparse
from pathlib import Path
from typing import List, Dict

import pandas as pd
from tqdm import tqdm

from mdke.utils.io import load_yaml, Paths, ensure_dirs, get_logger
from mdke.utils.langmap import normalize_lang

# duration hesaplamak için librosa kullanıyoruz (mp3 desteği stabil)
import librosa

def _compute_duration_seconds(audio_path: Path) -> float:
    try:
        dur = float(librosa.get_duration(path=str(audio_path)))
        return dur
    except Exception:
        return 0.0

def _find_cv_version_dir(lang_root: Path) -> Path:
    # örn: data/raw/commonvoice/tr/cv-corpus-22.0-2025-06-20-tr.tar → extract sonrası:
    # data/raw/commonvoice/tr/cv-corpus-22.0-2025-06-20/tr/...
    # burada "cv-corpus-22.0-2025-06-20" ile başlayan klasörü buluyoruz
    candidates = [p for p in lang_root.iterdir() if p.is_dir() and p.name.startswith("cv-corpus-")]
    if not candidates:
        raise FileNotFoundError(f"Common Voice version directory not found under {lang_root}")
    # birden fazla varsa en uzun isimli olan(son sürüm) genellikle doğru
    candidates.sort(key=lambda p: len(p.name), reverse=True)
    return candidates[0]

def _load_local_split_df(base_dir: Path, lang_stem: str, split: str, min_dur: float, max_dur: float) -> pd.DataFrame:
    # base_dir: .../cv-corpus-22.0-2025-06-20
    # içeride: base_dir/<lang_stem>/{train.tsv,validated.tsv,test.tsv,clips/}
    lang_dir = base_dir / lang_stem
    tsv_name = {
        "train": "train.tsv",
        "validation": "validated.tsv",
        "test": "test.tsv",
    }[split]
    tsv_path = lang_dir / tsv_name
    clips_dir = lang_dir / "clips"

    if not tsv_path.exists():
        raise FileNotFoundError(f"Missing TSV for split={split}: {tsv_path}")
    if not clips_dir.exists():
        raise FileNotFoundError(f"Missing clips directory: {clips_dir}")

    df = pd.read_csv(tsv_path, sep="\t", quoting=3)
    # beklenen sütunlar: client_id, path, sentence
    for col in ["client_id", "path", "sentence"]:
        if col not in df.columns:
            raise KeyError(f"Expected column '{col}' not found in {tsv_path}. Found: {list(df.columns)[:10]}")

    # tam audio path
    audio_paths: List[Path] = []
    for rel in df["path"].astype(str).tolist():
        # path sütunu genelde sadece dosya adı (ör: common_voice_tr_123456.mp3)
        audio_paths.append(clips_dir / rel)

    # duration hesapla (tqdm ile)
    durations = []
    for p in tqdm(audio_paths, desc=f"duration[{split}]"):
        durations.append(_compute_duration_seconds(p))

    out = pd.DataFrame({
        "speaker": df["client_id"].astype(str),
        "path": [str(p) for p in audio_paths],
        "text": df["sentence"].astype(str),
        "duration_s": durations,
        "split": split,
    })
    # süre filtresi
    mask = (out["duration_s"] >= min_dur) & (out["duration_s"] <= max_dur)
    out = out[mask].reset_index(drop=True)
    return out

def ingest_local(cfg_path: Path, lang_code_in: str) -> None:
    cfg = load_yaml(cfg_path)
    logger = get_logger(f"ingest_cv_local")

    std_lang = normalize_lang(lang_code_in)     # tr|kmr|zza
    logger.info(f"Standardized lang code: {lang_code_in} → {std_lang}")

    # local kök
    local_root = Path(cfg["data"]["commonvoice"]["local_root"])
    lang_root = local_root / std_lang
    if not lang_root.exists():
        raise FileNotFoundError(f"Local lang root not found: {lang_root}")

    # cv sürüm klasörünü bul
    version_dir = _find_cv_version_dir(lang_root)

    # CV iç klasör adı (lang stem) — dikkat:
    # CV-22.0 içinde dil dizini, ISO-639-3 kullanır: tr, kmr, zza
    lang_stem = std_lang

    # süre filtresi
    min_dur = float(cfg["data"]["commonvoice"]["min_dur"])
    max_dur = float(cfg["data"]["commonvoice"]["max_dur"])
    splits = cfg["data"]["commonvoice"]["splits"]

    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)

    frames: List[pd.DataFrame] = []
    for split in splits:
        logger.info(f"Loading local split: {std_lang}/{split}")
        df_split = _load_local_split_df(version_dir, lang_stem, split, min_dur, max_dur)
        df_split["lang"] = std_lang
        frames.append(df_split)

        out_path = paths.processed / f"cv_{std_lang}_{split}.parquet"
        df_split.to_parquet(out_path, index=False)
        logger.info(f"Saved {len(df_split):,} rows → {out_path}")

    # küçük özet
    total = sum(len(f) for f in frames)
    logger.info(f"Done. Total rows ({std_lang}): {total:,}")

def ingest_hf(cfg_path: Path, lang_code_in: str) -> None:
    # HF modu önceki sürümde yazdığımız gibiydi; local mod ana yolumuz.
    # İstersen burada HF çekmeyi sürdürebiliriz; şimdilik odak local.
    from datasets import load_dataset, Audio

    cfg = load_yaml(cfg_path)
    logger = get_logger(f"ingest_cv_hf")

    # HF dili: tr | ku | diq —> normalize edip HF'ye uygun geri çeviri:
    std_lang = normalize_lang(lang_code_in)     # tr|kmr|zza
    hf_lang = {"tr": "tr", "kmr": "ku", "zza": "diq"}[std_lang]

    min_dur = float(cfg["data"]["commonvoice"]["min_dur"])
    max_dur = float(cfg["data"]["commonvoice"]["max_dur"])
    splits = cfg["data"]["commonvoice"]["splits"]

    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)

    ds_name = "mozilla-foundation/common_voice_16_1"
    logger.info(f"Loading HF dataset: {ds_name} ({hf_lang}) ...")

    import pandas as pd
    from datasets import load_dataset, Audio

    def _duration_seconds(example) -> float:
        arr = example["audio"]["array"]
        sr = example["audio"]["sampling_rate"]
        return float(len(arr) / sr) if arr is not None and sr else 0.0

    for split in splits:
        logger.info(f"→ split={split}")
        ds = load_dataset(ds_name, hf_lang, split=split)
        ds = ds.cast_column("audio", Audio())
        ds = ds.map(lambda e: {"duration_s": _duration_seconds(e)}, desc="compute_duration")
        ds = ds.filter(lambda e: (e["duration_s"] >= min_dur) and (e["duration_s"] <= max_dur),
                       desc=f"filter_{min_dur}_{max_dur}s")

        cols = ["client_id", "path", "sentence", "duration_s"]
        missing = [c for c in cols if c not in ds.column_names]
        if missing:
            raise KeyError(f"Missing columns: {missing}")

        df = pd.DataFrame({
            "speaker": ds["client_id"],
            "path": ds["path"],
            "text": ds["sentence"],
            "duration_s": ds["duration_s"],
            "split": [split]*len(ds),
            "lang": [std_lang]*len(ds),
        })
        out_path = paths.processed / f"cv_{std_lang}_{split}.parquet"
        df.to_parquet(out_path, index=False)
        logger.info(f"Saved {len(df):,} rows → {out_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--lang", type=str, required=True, help="tr | kmr | zza | (aliases: ku, diq)")
    ap.add_argument("--mode", type=str, default="local", choices=["local", "hf"])
    args = ap.parse_args()

    if args.mode == "local":
        ingest_local(args.config, args.lang)
    else:
        ingest_hf(args.config, args.lang)

if __name__ == "__main__":
    main()
