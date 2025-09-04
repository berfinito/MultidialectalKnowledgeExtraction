import os
import sys
import time
import pandas as pd
import numpy as np
import librosa
from pathlib import Path
from mdke.text.transliterate_kmrzza import transliterate, has_arabic

from mdke.utils.io import save_jsonl
from mdke.asr.whisper_infer import Paths, ensure_dirs
from faster_whisper import WhisperModel

ACCEPTED_LANG_CODES = {
    "en", "tr", "de", "fr", "es", "it", "nl", "pt", "ru", "uk", "pl", "sv", "fi", "da", "no", "cs", "ro", "bg", "el", "hu",
    "ku", "diq", "ar", "fa", "zh", "ja", "ko"
}

def _to_ct2_model_id(base_id):
    return base_id

def load_audio(audio_path, sr=16000):
    audio, _ = librosa.load(audio_path, sr=sr, mono=False)
    if audio.ndim == 2:
        audio = np.mean(audio, axis=0)
    return audio

def compute_wer(refs, hyps):
    import jiwer
    return jiwer.wer(refs, hyps)

def compute_cer(refs, hyps):
    import jiwer
    return jiwer.cer(refs, hyps)

def compute_latin_hawar_ratio(preds):
    total = sum(len(p) for p in preds)
    if total == 0:
        return None
    latin_hawar = "abcdefghijklmnopqrstuvwxyzçğıöşüêîûqxw"
    count = sum(sum(c in latin_hawar for c in p.lower()) for p in preds)
    return count / total

def compute_tr_token_bias(preds):
    tr_chars = "abcçdefgğhıijklmnoöprsştuüvyz"
    total = sum(len(p) for p in preds)
    if total == 0:
        return None
    count = sum(sum(c in tr_chars for c in p.lower()) for p in preds)
    return count / total

def infer_split_ct2(
    cfg,
    std_lang,
    split,
    force_lang=None,
    postproc="none",
    limit=None,
    beam_size=1,
    vad_filter=False,
    bias_prompt=None,
    report_suffix=""
):
    raw = Path(cfg["paths"]["raw"])
    interim = Path(cfg["paths"]["interim"])
    processed = Path(cfg["paths"]["processed"])
    reports = Path(cfg["paths"]["reports"])

    paths = Paths(raw=raw, interim=interim, processed=processed, reports=reports)
    ensure_dirs(paths)

    if std_lang == "tr":
        ct2_id = cfg["asr"]["whisper"]["ct2_tr_model"]
        base_id = ct2_id
    elif std_lang == "kmr":
        ct2_id = cfg["asr"]["whisper"]["ct2_kmr_model"]
        base_id = ct2_id
    elif std_lang == "zza":
        ct2_id = cfg["asr"]["whisper"]["ct2_zza_model"]
        base_id = ct2_id
    else:
        ct2_id = cfg["asr"]["whisper"]["model"]
        base_id = ct2_id

    compute_type = cfg["asr"]["whisper"].get("ct2_compute_type", "float16")

    proc = Path(paths.processed)
    parquet_path = proc / f"cv_{std_lang}_{split}.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(f"Missing processed parquet: {parquet_path}")
    df = pd.read_parquet(parquet_path)
    if limit:
        df = df.head(int(limit))

    # PATCH: bias prompt override
    initial_prompt = None
    if bias_prompt:
        if Path(bias_prompt).exists():
            initial_prompt = Path(bias_prompt).read_text(encoding="utf-8").strip()
            if not initial_prompt:
                initial_prompt = None
        else:
            print(f"[WARN] Bias prompt file not found: {bias_prompt}")
    else:
        prompt_path = Path("configs/prompts") / f"{std_lang}_bias.txt"
        if prompt_path.exists():
            initial_prompt = prompt_path.read_text(encoding="utf-8").strip()
            if not initial_prompt:
                initial_prompt = None

    force_lang_req = (force_lang or "auto").lower().strip()
    valid = ACCEPTED_LANG_CODES | {"auto", None}
    lang_arg = None if force_lang_req == "auto" else (force_lang_req if force_lang_req in valid else None)

    temp = 0.0
    device = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "auto"
    wmodel = WhisperModel(ct2_id, device=device, compute_type=compute_type)

    # YENİ: CT2’nin desteklediği dilleri modelden öğren ve fallback uygula
    try:
        supported = set(getattr(wmodel, "supported_languages", []) or [])
    except Exception:
        supported = set()  # beklenmedik durumda “auto”ya düşeceğiz

    if force_lang_req == "auto":
        lang_arg = None  # autodetect
    elif force_lang_req in supported:
        lang_arg = force_lang_req
    else:
        print(f"[WARN] Language '{force_lang_req}' not supported by CT2; falling back to auto.")
        lang_arg = None

    outputs = []
    total_audio_s = 0.0
    wall_start = time.time()
    for i, row in df.iterrows():
        audio_path = row["audio_path"] if "audio_path" in row else row.get("path")
        if not audio_path or not Path(audio_path).exists():
            continue
        audio = load_audio(audio_path)
        if hasattr(audio, "ndim") and audio.ndim == 2:
            audio = audio.mean(axis=1)
        duration_s = float(row.get("duration_s", len(audio) / 16000.0))
        total_audio_s += duration_s

        try:
            segments, info = wmodel.transcribe(
                audio,
                beam_size=beam_size,
                language=lang_arg,           # None => autodetect
                initial_prompt=initial_prompt,
                vad_filter=vad_filter,
                temperature=temp
            )
            pred_raw = " ".join([seg.text for seg in segments])
            detected_language = getattr(info, "language", None)
            detected_lang_prob = getattr(info, "language_probability", None)
        except Exception as e:
            print(f"[ERR] {audio_path}: {e}")
            # Hatalı örneği boş tahmin ile kaydedip devam edelim (veya continue da edebilirsin)
            pred_raw = ""
            detected_language = None
            detected_lang_prob = None

        pred_translit = transliterate(pred_raw, mode="strict") if postproc.startswith("translit") else pred_raw
        has_arab = has_arabic(pred_raw)

        outputs.append({
            "id": row.get("id", f"{split}_{i}"),
            "audio_path": audio_path,
            "ref": row.get("text", ""),
            "pred_raw": pred_raw,
            "pred_translit": pred_translit,
            "has_arabic": has_arab,
            "duration_s": duration_s,
            "lang": std_lang,
            "detected_language": detected_language,
            "detected_lang_prob": detected_lang_prob,
        })

        if (i + 1) % 25 == 0 or (i + 1) == len(df):
            print(f"[{i+1}/{len(df)}] decoded...")

    wall = time.time() - wall_start

    suffix = f"_{report_suffix}" if report_suffix else ""
    interim_out = paths.interim / f"asr_post/whisperct2_{std_lang}_{split}{suffix}.jsonl"
    save_jsonl(outputs, interim_out)
    rep_path = paths.reports / f"asr_whisperct2_{std_lang}_{split}{suffix}.json"
    rep_path.parent.mkdir(parents=True, exist_ok=True)

    if len(outputs) == 0:
        rep = {
            "model": f"{base_id} (faster-whisper:{ct2_id})",
            "lang": std_lang,
            "split": split,
            "n": 0,
            "wer_raw": None,
            "cer_raw": None,
            "latin_hawar_ratio_raw": None,
            "tr_token_bias_raw": None,
            "wer_translit": None,
            "cer_translit": None,
            "latin_hawar_ratio_translit": None,
            "tr_token_bias_translit": None,
            "rtf": float("nan"),
            "total_audio_s": float(total_audio_s),
            "wall_s": float(wall),
            "beam_size": int(beam_size),
            "force_lang_requested": force_lang_req,
            "force_lang_effective": lang_arg,
            "postproc": postproc,
        }
        rep_path.write_text(__import__("json").dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[CT2] saved: {interim_out}")
        print(f"[CT2] saved: {rep_path}")
        return rep

    wer_raw = compute_wer([o["ref"] for o in outputs], [o["pred_raw"] for o in outputs])
    cer_raw = compute_cer([o["ref"] for o in outputs], [o["pred_raw"] for o in outputs])
    latin_hawar_ratio_raw = compute_latin_hawar_ratio([o["pred_raw"] for o in outputs])
    tr_token_bias_raw = compute_tr_token_bias([o["pred_raw"] for o in outputs])

    wer_translit = compute_wer([o["ref"] for o in outputs], [o["pred_translit"] for o in outputs])
    cer_translit = compute_cer([o["ref"] for o in outputs], [o["pred_translit"] for o in outputs])
    latin_hawar_ratio_translit = compute_latin_hawar_ratio([o["pred_translit"] for o in outputs])
    tr_token_bias_translit = compute_tr_token_bias([o["pred_translit"] for o in outputs])

    rep = {
        "model": f"{base_id} (faster-whisper:{ct2_id})",
        "lang": std_lang,
        "split": split,
        "n": len(outputs),
        "wer_raw": wer_raw,
        "cer_raw": cer_raw,
        "latin_hawar_ratio_raw": latin_hawar_ratio_raw,
        "tr_token_bias_raw": tr_token_bias_raw,
        "wer_translit": wer_translit,
        "cer_translit": cer_translit,
        "latin_hawar_ratio_translit": latin_hawar_ratio_translit,
        "tr_token_bias_translit": tr_token_bias_translit,
        "rtf": wall / total_audio_s if total_audio_s > 0 else float("nan"),
        "total_audio_s": float(total_audio_s),
        "wall_s": float(wall),
        "beam_size": int(beam_size),
        "force_lang_requested": force_lang_req,
        "force_lang_effective": lang_arg,
        "postproc": postproc,
    }

    rep_path.write_text(__import__("json").dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[CT2] saved: {interim_out}")
    print(f"[CT2] saved: {rep_path}")
    return rep

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--lang", type=str, required=False)
    parser.add_argument("--split", type=str, required=True)
    parser.add_argument("--beam_size", type=int, default=1)
    parser.add_argument("--vad_filter", type=bool, default=False)
    parser.add_argument("--postproc", type=str, default="none")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force_lang", type=str, default=None)
    parser.add_argument("--bias_prompt", type=str, default=None)
    parser.add_argument("--out", type=str, default=None)
    parser.add_argument("--dataset_lang", type=str, default=None)
    parser.add_argument("--decode_lang", type=str, default=None)
    parser.add_argument("--initial_prompt", type=str, default=None)
    parser.add_argument("--report_suffix", type=str, default=None)
    args = parser.parse_args()

    import yaml
    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    bias_prompt = args.bias_prompt or args.initial_prompt
    rep_suffix = args.report_suffix or ""
    std_lang = args.dataset_lang if args.dataset_lang else args.lang
    decode_lang = args.decode_lang if args.decode_lang else std_lang

    rep = infer_split_ct2(
        cfg,
        std_lang=std_lang,
        split=args.split,
        force_lang=decode_lang,
        postproc=args.postproc,
        limit=args.limit,
        beam_size=args.beam_size,
        vad_filter=args.vad_filter,
        bias_prompt=bias_prompt,
        report_suffix=rep_suffix
    )
    if args.out:
        out_path = Path(args.out)
    else:
        suffix = f"_{rep_suffix}" if rep_suffix else ""
        out_path = Path(f"reports/asr_whisperct2_{std_lang}_{args.split}{suffix}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(__import__("json").dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[CT2] saved (custom): {out_path}")