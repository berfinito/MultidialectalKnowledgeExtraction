"""Whisper ASR inference for TR/KMR/ZZA with reproducible reports and optional beam dump.

Key features:
- Final policy: TR=whisper-medium (forced 'tr'), KMR/ZZA=whisper-large-v2 (auto), bias=OFF, beam=1
- Optional beam dump: emits *_beams.jsonl with alt hypotheses and scores
- Robust generate(): forced_decoder_ids on generation_config; no attention_mask; dynamic input length
- Metrics: WER/CER (jiwer), RTF, tr_token_bias (proxy), latin_hawar_ratio

Outputs:
- data/interim/asr/whisper_{lang}_{split}[_tag][_beams].jsonl
- reports/asr_whisper_{lang}_{split}[_tag].json
"""
from __future__ import annotations
import argparse
from pathlib import Path
import time
from typing import List, Dict, Any, Optional
import os, platform

import torch
import pandas as pd
import numpy as np
from tqdm import tqdm

from transformers import WhisperProcessor, WhisperForConditionalGeneration, logging as hf_logging
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

# Windows/OpenMP ortam koruması
if platform.system().lower().startswith("win"):
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_THREADING_LAYER", "GNU")

# HF uyarılarını azalt
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
hf_logging.set_verbosity_error()


def load_audio_16k(path: str) -> np.ndarray:
    """Load mono 16 kHz float32 audio. Resample if needed; downmix to mono."""
    try:
        audio, sr = sf.read(path)
        if sr != 16000:
            audio = librosa.resample(audio.astype(np.float32), orig_sr=sr, target_sr=16000)
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        return audio.astype(np.float32)
    except Exception:
        audio, _ = librosa.load(path, sr=16000, mono=True)
        return audio.astype(np.float32)


def std_to_whisper_lang(std_lang: str) -> Optional[str]:
    """Project language codes to Whisper codes (tr->tr, kmr->ku, zza->diq)."""
    if std_lang == "tr":
        return "tr"
    if std_lang == "kmr":
        return "ku"
    if std_lang == "zza":
        return "diq"
    return None


def build_forced_decoder_ids(processor: WhisperProcessor, lang_choice: Optional[str]) -> tuple[Optional[List[List[int]]], str]:
    """
    Safely build forced_decoder_ids on generation_config; fallback to transcribe-only if needed.
    Güvenli forced_decoder_ids üret:
      - lang_choice None/'auto' → task='transcribe' (dil autodetect)
      - lang_choice verilmişse → dene; hata olursa task='transcribe'
    Dönüş: (forced_decoder_ids | None, effective_lang_label)
    """
    def transcribe_only() -> Optional[List[List[int]]]:
        try:
            return processor.get_decoder_prompt_ids(task="transcribe")
        except Exception:
            return None

    if not lang_choice or lang_choice.strip().lower() in ("auto", "none", ""):
        return transcribe_only(), "auto"

    lang_norm = lang_choice.strip().lower()
    try:
        fdi = processor.get_decoder_prompt_ids(language=lang_norm, task="transcribe")
        return fdi, lang_norm
    except Exception:
        return transcribe_only(), "auto"


def read_bias_text(std_lang: str, max_chars: int = 1200, max_words: int = 400) -> Optional[str]:
    """
    Bias metnini güvenli şekilde kısalt: önce ilk max_chars karakter,
    sonra ilk max_words kelime; TR için bias yok.
    """
    if std_lang not in ("kmr", "zza"):
        return None
    bias_path = Path(f"configs/prompts/{std_lang}_bias.txt")
    if not bias_path.exists():
        return None
    txt = bias_path.read_text(encoding="utf-8").strip()
    if not txt:
        return None
    txt = " ".join(txt.split())
    if len(txt) > max_chars:
        txt = txt[:max_chars]
    words = txt.split()
    if len(words) > max_words:
        txt = " ".join(words[:max_words])
    return txt


def get_prompt_ids_if_any(processor: WhisperProcessor, std_lang: str, max_tokens: int = 224) -> Optional[List[int]]:
    """
    Return trimmed prompt_ids for bias text (KMR/ZZA only); None if missing/empty.
    get_prompt_ids ile prompt hazırla; aşırı uzunlukları kes (her durumda ≤ max_tokens).
    """
    bias_text = read_bias_text(std_lang)
    if not bias_text:
        return None
    try:
        ids = processor.get_prompt_ids(bias_text)
    except Exception:
        return None

    def to_flat_list(x):
        try:
            import torch as _torch
            if isinstance(x, _torch.Tensor):
                x = x.tolist()
        except Exception:
            pass
        if isinstance(x, (tuple, np.ndarray)):
            x = x.tolist()
        if isinstance(x, list) and len(x) > 0 and isinstance(x[0], list):
            x = x[0]
        if not isinstance(x, list):
            try:
                x = list(x)
            except Exception:
                return None
        x = [int(t) for t in x if isinstance(t, (int, np.integer))]
        return x

    flat = to_flat_list(ids)
    if not flat:
        return None
    if len(flat) > max_tokens:
        flat = flat[:max_tokens]
    return flat


def infer_split(
    cfg,
    std_lang: str,
    split: str,
    limit: Optional[int] = None,
    batch_size: int = 8,
    beam_size: int = 1,
    gen_lang: Optional[str] = None,
    use_bias: bool = False,  # Varsayılan: kapalı (KMR/ZZA’da bias faydasız/riskli)
    min_new_tokens: int = 8,
    max_new_tokens: int = 160,
    tag: str = "",  # outputs/logs için ek son ek
    dump_beams: bool = False,  # beam adaylarını JSONL'e dök
) -> Dict[str, Any]:
    logger = get_logger(f"whisper_{std_lang}_{split}")
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)

    # Tag normalizasyonu
    if tag:
        safe_tag = "".join(c for c in str(tag) if (c.isalnum() or c in ("-", "_")))
        tag_suffix = f"_{safe_tag}" if safe_tag else ""
    else:
        tag_suffix = ""

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

    # Dinamik giriş uzunluğu (varsa) aç
    if hasattr(model.config, "use_dynamic_input_length"):
        model.config.use_dynamic_input_length = True
        if hasattr(model, "generation_config") and hasattr(model.generation_config, "use_dynamic_input_length"):
            model.generation_config.use_dynamic_input_length = True
        logger.info("Enabled dynamic input length for Whisper.")

    # Dil tercihi: TR → tr; KMR/ZZA → auto; CLI override eder
    if gen_lang and gen_lang.strip().lower() == "auto":
        lang_choice = None
    elif gen_lang:
        lang_choice = gen_lang.strip().lower()
    else:
        lang_choice = "tr" if std_lang == "tr" else None  # kmr/zza: auto

    forced_decoder_ids, effective_lang = build_forced_decoder_ids(processor, lang_choice)
    logger.info(f"Generation language: {effective_lang}")

    # Bias prompt
    prompt_ids = None
    if use_bias and std_lang in ("kmr", "zza"):
        prompt_ids = get_prompt_ids_if_any(processor, std_lang)
    if prompt_ids is not None:
        logger.info(f"Using {std_lang.upper()} prompt bias with {len(prompt_ids)} tokens.")

    # ÖNEMLİ: forced_decoder_ids'ı bir kere generation_config'e yaz, generate çağrılarında geçme
    try:
        if forced_decoder_ids is not None:
            if hasattr(model, "generation_config"):
                model.generation_config.forced_decoder_ids = forced_decoder_ids
            else:
                model.config.forced_decoder_ids = forced_decoder_ids
    except Exception as e:
        logger.warning(f"Failed to set forced_decoder_ids on generation_config: {e}")

    # Beam dump modu tek bayrak
    beams_mode = bool(dump_beams and beam_size > 1)

    outputs = []
    total_audio_s = 0.0
    t0 = time.time()
    n = len(df)
    logger.info(f"Start inference: n={n}, batch_size={batch_size}, beam_size={beam_size}, split={split}, lang={std_lang}")

    # Pad modu
    pad_mode = "longest"
    max_len = None  # dynamic input length ile birlikte güvenli

    err_log = paths.reports / f"logs/asr_errors_{std_lang}_{split}{tag_suffix}.txt"
    err_log.parent.mkdir(parents=True, exist_ok=True)

    # Fallback sayaçları
    batch_fallback_retries = 0
    single_fallback_fixes = 0

    # Erken bias kapatma için sayaçlar
    seen_batches = 0
    retry_batches = 0
    disable_check_after = 16
    disable_threshold = 0.5

    for i in tqdm(range(0, n, batch_size), desc=f"infer[{std_lang}/{split}]"):
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

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
        # attention_mask üretsek de generate'te kullanmayacağız (Whisper + input_features ile sorun çıkarabiliyor)
        attention_mask = proc_out.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(device)

        # Toplu generate
        try:
            if beams_mode:
                with torch.inference_mode():
                    gen_kwargs = dict(
                        input_features=input_features,
                        # attention_mask yok
                        num_beams=int(beam_size),
                        num_return_sequences=int(beam_size),
                        min_new_tokens=int(min_new_tokens),
                        max_new_tokens=int(max_new_tokens),
                        return_dict_in_generate=True,
                        output_scores=True,
                    )
                    if prompt_ids is not None:
                        gen_kwargs["prompt_ids"] = prompt_ids
                    gen_out = model.generate(**gen_kwargs)

                sequences = gen_out.sequences  # [batch*beam, T]
                seq_scores = getattr(gen_out, "sequences_scores", None)  # [batch*beam] (log-benzeri)
                decoded_all = processor.batch_decode(sequences, skip_special_tokens=True)

                texts = []
                grouped = []
                for bi in range(len(batch)):
                    start = bi * beam_size
                    end = start + beam_size
                    cand_txts = decoded_all[start:end]
                    if seq_scores is not None:
                        cand_scores = [float(s) for s in seq_scores[start:end].tolist()]
                    else:
                        cand_scores = [float("nan")] * len(cand_txts)
                    best_i = max(
                        range(len(cand_txts)),
                        key=lambda k: cand_scores[k] if not np.isnan(cand_scores[k]) else -1e9
                    )
                    texts.append(cand_txts[best_i])
                    alt_txts = [t for j, t in enumerate(cand_txts) if j != best_i]
                    alt_scores = [s for j, s in enumerate(cand_scores) if j != best_i]
                    grouped.append({
                        "best_index": int(best_i),
                        "all_hyps": cand_txts,
                        "all_scores": cand_scores,
                        "alt_hyps": alt_txts,
                        "alt_scores": alt_scores,
                    })

                # bellek temizliği
                try:
                    del gen_out, sequences, seq_scores, decoded_all
                except Exception:
                    pass
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

            else:
                with torch.inference_mode():
                    predicted_ids = model.generate(
                        input_features=input_features,
                        # attention_mask yok
                        min_new_tokens=int(min_new_tokens),
                        max_new_tokens=int(max_new_tokens),
                        num_beams=1,
                        **({"prompt_ids": prompt_ids} if prompt_ids is not None else {}),
                    )
                texts = processor.batch_decode(predicted_ids, skip_special_tokens=True)
                grouped = None

        except Exception as e:
            logger.warning(f"Batch generate failed; falling back to single items. Reason: {e}")
            texts = []
            grouped = [] if beams_mode else None
            for j in range(len(batch)):
                try:
                    with torch.inference_mode():
                        if beams_mode:
                            gen_out = model.generate(
                                input_features=input_features[j:j+1],
                                num_beams=int(beam_size),
                                num_return_sequences=int(beam_size),
                                min_new_tokens=int(min_new_tokens),
                                max_new_tokens=int(max_new_tokens),
                                return_dict_in_generate=True,
                                output_scores=True,
                                **({"prompt_ids": prompt_ids} if prompt_ids is not None else {}),
                            )
                            seq = gen_out.sequences
                            sc = getattr(gen_out, "sequences_scores", None)
                            cand_txts = processor.batch_decode(seq, skip_special_tokens=True)
                            if sc is not None:
                                cand_scores = [float(s) for s in sc.tolist()]
                            else:
                                cand_scores = [float("nan")] * len(cand_txts)
                            best_i = max(
                                range(len(cand_txts)),
                                key=lambda k: cand_scores[k] if not np.isnan(cand_scores[k]) else -1e9
                            )
                            txt = cand_txts[best_i]
                            alt_txts = [t for k, t in enumerate(cand_txts) if k != best_i]
                            alt_scores = [s for k, s in enumerate(cand_scores) if k != best_i]
                            grouped.append({
                                "best_index": int(best_i),
                                "all_hyps": cand_txts,
                                "all_scores": cand_scores,
                                "alt_hyps": alt_txts,
                                "alt_scores": alt_scores,
                            })
                            # bellek temizliği
                            del gen_out, seq, sc
                        else:
                            single_ids = model.generate(
                                input_features=input_features[j:j+1],
                                num_beams=int(beam_size),
                                do_sample=False,
                                min_new_tokens=int(min_new_tokens),
                                max_new_tokens=int(max_new_tokens),
                            )
                            txt = processor.batch_decode(single_ids, skip_special_tokens=True)[0]
                    texts.append(txt)
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except Exception as ee:
                    txt = ""
                    texts.append(txt)
                    with err_log.open("a", encoding="utf-8") as ef:
                        ef.write(f"{batch['path'].iloc[j]}\t{str(ee)}\n")

        # Bias toplu fallback (yüksek boş oranı) + erken kapatma istatistiği
        retried_this_batch = False
        if prompt_ids is not None and use_bias:
            empty_idx = [k for k, t in enumerate(texts) if not str(t).strip()]
            if len(empty_idx) >= max(1, len(texts) // 2):
                retried_this_batch = True
                logger.info(f"High empty-rate with bias prompt ({len(empty_idx)}/{len(texts)}). Retrying batch without prompt.")
                try:
                    with torch.inference_mode():
                        predicted_ids2 = model.generate(
                            input_features=input_features,
                            # attention_mask yok
                            num_beams=int(beam_size),
                            do_sample=False,
                            min_new_tokens=int(min_new_tokens),
                            max_new_tokens=int(max_new_tokens),
                        )
                    texts2 = processor.batch_decode(predicted_ids2, skip_special_tokens=True)
                    for k in empty_idx:
                        texts[k] = texts2[k]
                    batch_fallback_retries += 1
                except Exception as e:
                    logger.warning(f"Batch retry without prompt failed: {e}")

            # Kalan boşlar için tekil bias'sız fallback
            remain_empty = [k for k, t in enumerate(texts) if not str(t).strip()]
            if remain_empty:
                for k in remain_empty:
                    try:
                        with torch.inference_mode():
                            single_ids = model.generate(
                                input_features=input_features[k:k+1],
                                num_beams=int(beam_size),
                                do_sample=False,
                                min_new_tokens=int(min_new_tokens),
                                max_new_tokens=int(max_new_tokens),
                            )
                        txt = processor.batch_decode(single_ids, skip_special_tokens=True)[0]
                        if str(txt).strip():
                            texts[k] = txt
                            single_fallback_fixes += 1
                    except Exception:
                        pass

        # Erken kapatma: ilk disable_check_after batch’te retry oranı yüksekse bias’ı tamamen kapat
        seen_batches += 1
        if retried_this_batch:
            retry_batches += 1
        if use_bias and prompt_ids is not None and seen_batches == disable_check_after:
            rate = retry_batches / max(1, seen_batches)
            if rate >= disable_threshold:
                logger.info(f"Disabling bias prompt for the rest of the run (retry_rate={rate:.2f}).")
                prompt_ids = None
                use_bias = False

        for local_idx, (idx, text) in enumerate(zip(batch.index.tolist(), texts)):
            record = {
                "utt_id": f"{split}_{idx}",
                "path": df.at[idx, "path"],
                "gt_text": df.at[idx, "text"],
                "pred_text": text,
                "duration_s": float(df.at[idx, "duration_s"]),
                "split": split,
                "lang": std_lang,
            }
            if beams_mode:
                if grouped is not None and local_idx < len(grouped):
                    g = grouped[local_idx]
                    best_score = g["all_scores"][g["best_index"]]
                    record["logp_acoustic"] = (
                        None
                        if (best_score is None or (isinstance(best_score, float) and np.isnan(best_score)))
                        else float(best_score)
                    )
                    record["alt_hyps"] = g["alt_hyps"]
                    record["beam_scores"] = g["alt_scores"]
                    record["beam_size"] = int(beam_size)
                else:
                    record["logp_acoustic"] = None
                    record["alt_hyps"] = []
                    record["beam_scores"] = []
                    record["beam_size"] = int(beam_size)
            outputs.append(record)

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

    # Çıktı dosya adı: beams_mode ise her zaman _beams.jsonl
    interim_out = paths.interim / f"asr/whisper_{std_lang}_{split}{tag_suffix}.jsonl"
    if beams_mode:
        interim_out = paths.interim / f"asr/whisper_{std_lang}_{split}{tag_suffix}_beams.jsonl"
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
        "forced_language": effective_lang,
        "prompt_tokens": None if prompt_ids is None else int(len(prompt_ids)),
        "min_new_tokens": int(min_new_tokens),
        "max_new_tokens": int(max_new_tokens),
        "bias_fallback_batch_retries": int(batch_fallback_retries),
        "bias_fallback_single_fixes": int(single_fallback_fixes),
        "tag": (tag if tag else None),
        "dump_beams": bool(dump_beams),
    }
    rep_path = paths.reports / f"asr_whisper_{std_lang}_{split}{tag_suffix}.json"
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
    ap.add_argument("--limit", dest="limit", type=int, default=None, help="Only first N examples (debug).")
    ap.add_argument("--limit_n", dest="limit", type=int, default=None, help="Alias for --limit.")
    ap.add_argument("--batch_size", type=int, default=8)
    ap.add_argument("--beam_size", type=int, default=1)
    ap.add_argument("--gen_lang", type=str, default=None,
                    help="Forced language (tr|ku|diq|auto). Default: tr for TR, auto otherwise.")
    ap.add_argument("--no_bias", action="store_true", help="Bias prompt'ı kapat.")
    ap.add_argument("--force_bias", action="store_true", help="Bias prompt'ı açık (KMR/ZZA için opsiyonel; önerilmez).")
    ap.add_argument("--min_new", type=int, default=8, help="min_new_tokens for generation.")
    ap.add_argument("--max_new", type=int, default=160, help="max_new_tokens for generation.")
    ap.add_argument("--tag", type=str, default="", help="Çıktı dosyaları için ek son ek, örn: 'small', 'medium'.")
    ap.add_argument("--dump_beams", action="store_true",
                    help="Beam>1 ise beam hip'lerini ve skorları JSONL olarak kaydet.")
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    std_lang = normalize_lang(args.lang)

    # Bias politikası: TR her zaman kapalı; KMR/ZZA default kapalı; sadece --force_bias ile aç
    if std_lang == "tr":
        final_use_bias = False
    else:
        if args.no_bias:
            final_use_bias = False
        elif args.force_bias:
            final_use_bias = True
        else:
            final_use_bias = False

    rep = infer_split(
        cfg, std_lang, args.split,
        limit=args.limit, batch_size=args.batch_size, beam_size=args.beam_size,
        gen_lang=(None if (args.gen_lang and args.gen_lang.strip().lower()=="auto") else (args.gen_lang.strip().lower() if args.gen_lang else None)),
        use_bias=final_use_bias,
        min_new_tokens=args.min_new,
        max_new_tokens=args.max_new,
        tag=args.tag,
        dump_beams=args.dump_beams,
    )
    print(rep)


if __name__ == "__main__":
    main()
