# src/mdke/asr/whisper_infer.py
from __future__ import annotations
import argparse
from pathlib import Path
import time
from typing import List, Dict, Any, Optional
import os, platform, sys

import torch
import pandas as pd
import numpy as np
from tqdm import tqdm

from transformers import WhisperProcessor, WhisperForConditionalGeneration
import soundfile as sf
import librosa

from mdke.utils.io import load_yaml, Paths, ensure_dirs, save_jsonl, get_logger
from mdke.utils.langmap import normalize_lang
from mdke.utils.metrics import (
    compute_wer_cer,
    compute_rtf,
    tr_token_bias_ratio,
    latin_hawar_ratio,
)

# (HF için kritik değil ama zararsız) Windows/OpenMP ortam koruması
if platform.system().lower().startswith("win"):
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_THREADING_LAYER", "GNU")


def load_audio_16k(path: str) -> np.ndarray:
    """Load audio as mono 16 kHz float32."""
    try:
        audio, sr = sf.read(path)
        if sr != 16000:
            audio = librosa.resample(audio.astype(np.float32), orig_sr=sr, target_sr=16000)
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        return audio.astype(np.float32)
    except Exception:
        audio, sr = librosa.load(path, sr=16000, mono=True)
        return audio.astype(np.float32)


def get_prompt_ids_if_any(processor: WhisperProcessor, lang: str, max_tokens: int = 224) -> Optional[List[int]]:
    """
    Bias prompt:
      - kmr -> configs/prompts/kmr_bias.txt (if exists)
      - zza -> configs/prompts/zza_bias.txt (if exists)
    Tokenize → truncate (max_tokens) → return List[int].
    """
    if lang not in ("kmr", "zza"):
        return None
    bias_path = Path(f"configs/prompts/{lang}_bias.txt")
    if not bias_path.exists():
        return None
    bias_text = bias_path.read_text(encoding="utf-8").strip()
    if not bias_text:
        return None

    # Güvenilir truncation: tokenizer ile tokenlara çevir, özel token ekleme.
    try:
        toks = processor.tokenizer(
            bias_text,
            add_special_tokens=False,
            return_attention_mask=False,
            truncation=False
        )["input_ids"]
    except Exception:
        return None

    if not isinstance(toks, list):
        try:
            toks = list(toks)
        except Exception:
            return None

    if len(toks) > max_tokens:
        toks = toks[:max_tokens]

    return toks


def infer_split(
    cfg,
    std_lang: str,
    split: str,
    limit: Optional[int] = None,
    batch_size: int = 8,
    beam_size: int = 1,
    gen_lang: Optional[str] = None,  # <-- added
) -> Dict[str, Any]:
    logger = get_logger(f"whisper_{std_lang}_{split}")
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)

    df_path = paths.processed / f"cv_{std_lang}_{split}.parquet"
    if not df_path.exists():
        raise FileNotFoundError(f"Missing processed file: {df_path}")
    df = pd.read_parquet(df_path)

    if limit is not None:
        df = df.iloc[:limit].reset_index(drop=True)
        logger.info(f"Limiting to first {len(df)} rows for a quick run.")

    model_id = cfg["asr"]["whisper"]["model"]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    logger.info(f"Loading model: {model_id} (device={device}, dtype={dtype})")
    processor: WhisperProcessor = WhisperProcessor.from_pretrained(model_id)
    model: WhisperForConditionalGeneration = WhisperForConditionalGeneration.from_pretrained(
        model_id, torch_dtype=dtype
    ).to(device)
    model.eval()

    supports_dynamic = hasattr(model.config, "use_dynamic_input_length")
    if supports_dynamic:
        model.config.use_dynamic_input_length = True
        if hasattr(model, "generation_config") and hasattr(model.generation_config, "use_dynamic_input_length"):
            model.generation_config.use_dynamic_input_length = True
        logger.info("Enabled dynamic input length for Whisper (no 3000-frame requirement).")

    if gen_lang is None:
        gen_lang = "tr" if std_lang == "tr" else None

    prompt_ids = get_prompt_ids_if_any(processor, std_lang)
    if prompt_ids is not None:
        # Burada artık 224 civarı görmelisin
        logger.info(f"Using {std_lang.upper()} prompt bias with {len(prompt_ids)} tokens.")
    if gen_lang:
        logger.info(f"Forcing generation language: {gen_lang}")

    outputs = []
    total_audio_s = 0.0
    t0 = time.time()
    n = len(df)
    logger.info(f"Start inference: n={n}, batch_size={batch_size}, beam_size={beam_size}, split={split}, lang={std_lang}")

    if gen_lang is not None or supports_dynamic:
        pad_mode = "longest"
        max_len = None
    else:
        pad_mode = "max_length"
        try:
            max_len = int(getattr(processor.feature_extractor, "nb_max_frames", 3000))
        except Exception:
            max_len = 3000
        logger.info(f"Autodetect on old Transformers: padding to max_length={max_len} frames.")

    err_log = paths.reports / f"logs/asr_errors_{std_lang}_{split}.txt"
    err_log.parent.mkdir(parents=True, exist_ok=True)

    for i in tqdm(range(0, n, batch_size), desc=f"infer[{std_lang}/{split}]"):
        batch = df.iloc[i:i + batch_size]
        audios = []
        for p in batch["path"].tolist():
            a = load_audio_16k(p)
            total_audio_s += len(a) / 16000.0
            audios.append(a)

        proc_out = processor(
            audios,
            sampling_rate=16000,
            return_tensors="pt",
            padding=pad_mode,
            max_length=max_len,
            return_attention_mask=True,
        )
        input_features = proc_out["input_features"].to(device=device, dtype=dtype)
        attention_mask = proc_out.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(device)

        try:
            with torch.inference_mode():
                predicted_ids = model.generate(
                    input_features=input_features,
                    attention_mask=attention_mask,
                    num_beams=beam_size,
                    task="transcribe",
                    **({"language": gen_lang} if gen_lang is not None else {}),
                    **({"prompt_ids": prompt_ids} if prompt_ids is not None else {}),
                )
            texts = processor.batch_decode(predicted_ids, skip_special_tokens=True)
        except Exception as e:
            texts = []
            for j, pth in enumerate(batch["path"].tolist()):
                try:
                    with torch.inference_mode():
                        single_ids = model.generate(
                            input_features=input_features[j:j+1],
                            attention_mask=None if attention_mask is None else attention_mask[j:j+1],
                            num_beams=beam_size,
                            task="transcribe",
                            **({"language": gen_lang} if gen_lang is not None else {}),
                            **({"prompt_ids": prompt_ids} if prompt_ids is not None else {}),
                        )
                    txt = processor.batch_decode(single_ids, skip_special_tokens=True)[0]
                except Exception as ee:
                    txt = ""
                    with err_log.open("a", encoding="utf-8") as ef:
                        ef.write(f"{pth}\t{str(ee)}\n")
                texts.append(txt)

        for (idx, text) in zip(batch.index.tolist(), texts):
            outputs.append({
                "path": df.at[idx, "path"],
                "gt_text": df.at[idx, "text"],
                "pred_text": text,
                "duration_s": float(df.at[idx, "duration_s"]),
                "split": split,
                "lang": std_lang,
            })

    wall = time.time() - t0
    rtf = compute_rtf(total_audio_s, wall)
    logger.info(f"Finished. total_audio_s={total_audio_s:.1f}s, wall={wall:.1f}s, rtf={rtf:.3f}")

    refs = [o["gt_text"] for o in outputs]
    hyps = [o["pred_text"] for o in outputs]
    metrics = compute_wer_cer(refs, hyps)

    bias_ratio = None
    if std_lang != "tr":
        sw_path = Path("configs/stopwords/tr.txt")
        if sw_path.exists():
            tr_sw = {
                w.strip().lower()
                for w in sw_path.read_text(encoding="utf-8").splitlines()
                if w.strip() and not w.startswith("#")
            }
        else:
            tr_sw = {"ve", "ile", "de", "da", "bu", "şu", "o", "bir", "çok", "mi", "mu", "mü", "mı"}
        bias_ratio = tr_token_bias_ratio(hyps, tr_sw)

    latin_ratio = None
    if std_lang in ("kmr", "zza"):
        latin_ratio = float(latin_hawar_ratio(hyps))

    interim_out = paths.interim / f"asr/whisper_{std_lang}_{split}.jsonl"
    save_jsonl(outputs, interim_out)

    rep = {
        "model": model_id,
        "lang": std_lang,
        "split": split,
        "n": len(outputs),
        "wer": float(metrics["wer"]),
        "cer": float(metrics["cer"]),
        "rtf": float(rtf),
        "total_audio_s": float(total_audio_s),
        "wall_s": float(wall),
        "tr_token_bias": None if bias_ratio is None else float(bias_ratio),
        "latin_hawar_ratio": latin_ratio,
        "beam_size": int(beam_size),
        "batch_size": int(batch_size),
    }
    rep_path = paths.reports / f"asr_whisper_{std_lang}_{split}.json"
    rep_path.parent.mkdir(parents=True, exist_ok=True)
    rep_path.write_text(__import__("json").dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

    logger.info("Saved predictions → %s", interim_out)
    logger.info("Saved report → %s", rep_path)
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--lang", type=str, required=True, help="tr | kmr | zza (aliases: ku, diq)")
    ap.add_argument("--split", type=str, default="validation", choices=["train", "validation", "test"])
    ap.add_argument("--limit", dest="limit", type=int, default=None,
                    help="Only run the first N examples (debug/smoke test).")
    ap.add_argument("--limit_n", dest="limit", type=int, default=None,
                    help="Alias for --limit (first N examples).")
    ap.add_argument("--batch_size", type=int, default=8)
    ap.add_argument("--beam_size", type=int, default=1)
    ap.add_argument("--gen_lang", type=str, default=None,
                    help="Force Whisper generation language (e.g., ku, diq, tr). Use 'auto' to disable.")
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    std_lang = normalize_lang(args.lang)

    # Resolve generation language preference for infer_split
    resolved_gen_lang = None if (args.gen_lang and args.gen_lang.strip().lower() == "auto") else (args.gen_lang.strip().lower() if args.gen_lang else None)

    rep = infer_split(
        cfg, std_lang, args.split,
        limit=args.limit, batch_size=args.batch_size, beam_size=args.beam_size,
        gen_lang=resolved_gen_lang,  # <-- pass through
    )
    print(rep)

if __name__ == "__main__":
    main()