import argparse
from pathlib import Path
from typing import List
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tqdm import tqdm

# -----------------------------
# Yardımcılar
# -----------------------------
def resolve_bos_id(tok, tgt_lang: str) -> int:
    """
    NLLB hedef dil BOS id'sini güvenli biçimde bul.
    Önce lang_code_to_id varsa onu dener; yoksa tokenizer token map üzerinden dener.
    """
    # 1) Klasik yol (slow tokenizer'larda mevcut)
    if hasattr(tok, "lang_code_to_id") and tgt_lang in tok.lang_code_to_id:
        return tok.lang_code_to_id[tgt_lang]

    # 2) Fast tokenizer için fallback: dil kodunu token'a çevir
    bos_id = tok.convert_tokens_to_ids(tgt_lang)
    if bos_id is None or bos_id == getattr(tok, "unk_token_id", None):
        bos_id = tok.convert_tokens_to_ids(f"__{tgt_lang}__")

    if bos_id is None or bos_id == getattr(tok, "unk_token_id", None):
        raise SystemExit(f"[fatal] Hedef dil kodu çözülemedi: {tgt_lang}")

    return bos_id


def load_model(name: str, dtype: str, device: str, compile_model: bool):
    # dtype seçimi
    if dtype == "float16":
        torch_dtype = torch.float16
    elif dtype == "bfloat16":
        torch_dtype = torch.bfloat16
    else:
        torch_dtype = torch.float32

    # NLLB için slow tokenizer güvenli (lang_code_to_id mevcut)
    tok = AutoTokenizer.from_pretrained(name, use_fast=False)

    # safetensors varsa onu kullan, yoksa .bin yükle
    local_path = Path(name)
    use_safetensors = (local_path.exists() and (local_path / "model.safetensors").exists())

    model = AutoModelForSeq2SeqLM.from_pretrained(
        name,
        dtype=torch_dtype if torch_dtype != torch.float32 else None,  # torch_dtype -> dtype (deprecation yok)
        low_cpu_mem_usage=True,
        device_map=None,
        use_safetensors=use_safetensors,
    )

    dev = torch.device(device)
    model.to(dev, dtype=torch_dtype if torch_dtype != torch.float32 else None)
    model.eval()

    if compile_model and torch_dtype != torch.bfloat16:
        try:
            model = torch.compile(model)
        except Exception:
            pass
    return tok, model, dev, torch_dtype


def pack_by_tokens(lines: List[str], tok, max_batch_tokens: int, max_sentences: int):
    """Sıra korunur – kaba token tahmini (kelime * 1.3)."""
    batch, batch_tok = [], 0
    for line in lines:
        est = max(1, int(len(line.split()) * 1.3))
        if batch and (batch_tok + est > max_batch_tokens or len(batch) >= max_sentences):
            yield batch
            batch, batch_tok = [], 0
        batch.append(line)
        batch_tok += est
    if batch:
        yield batch


def get_autocast(dev_type: str, enable: bool, dt: torch.dtype):
    if enable and dev_type == "cuda":
        use_dt = torch.bfloat16 if dt == torch.bfloat16 else torch.float16
        return lambda: torch.autocast(device_type=dev_type, dtype=use_dt)
    return torch.no_grad


# -----------------------------
# Çekirdek NLLB çeviri
# -----------------------------
def translate_nllb(
    lines: List[str],
    tok,
    model,
    src_lang: str,
    tgt_lang: str,
    max_new_tokens: int,
    max_batch_tokens: int,
    max_sentences: int,
    dev: torch.device,
    use_autocast: bool,
    beams: int,
    checkpoint_path: Path,
    checkpoint_every: int,
    adaptive: bool,
    torch_dtype: torch.dtype,
):
    tok.src_lang = src_lang
    bos_id = resolve_bos_id(tok, tgt_lang)

    out: List[str] = []
    total = len(lines)
    start_idx = 0

    while start_idx < total:
        # Kalan satırlar
        remaining = lines[start_idx:]
        batches = list(pack_by_tokens(remaining, tok, max_batch_tokens, max_sentences))
        if not batches:
            break

        ctx_factory = get_autocast(dev.type, use_autocast, torch_dtype)

        for b in tqdm(
            batches,
            desc=f"mt[{src_lang}->{tgt_lang}] tokens={max_batch_tokens} sents={max_sentences}",
            leave=False,
        ):
            try:
                with ctx_factory():
                    enc = tok(
                        b,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=256,
                    ).to(dev)
                    gen = model.generate(
                        **enc,
                        forced_bos_token_id=bos_id,
                        num_beams=beams,
                        do_sample=False,
                        min_new_tokens=8,
                        max_new_tokens=max_new_tokens,
                        no_repeat_ngram_size=3,
                        repetition_penalty=1.1,
                        length_penalty=1.05,
                        early_stopping=True,
                    )
                    dec = tok.batch_decode(gen, skip_special_tokens=True)
                out.extend(dec)
                start_idx += len(b)

                # Checkpoint
                if checkpoint_every > 0 and (len(out) % checkpoint_every == 0):
                    checkpoint_path.write_text("\n".join(out), encoding="utf-8")

            except torch.cuda.OutOfMemoryError:
                torch.cuda.empty_cache()
                if not adaptive:
                    raise
                # Adaptif küçültme
                new_tokens = max(1024, int(max_batch_tokens * 0.75))
                new_sents = max(4, int(max_sentences * 0.75))
                print(
                    f"[WARN] OOM -> max_batch_tokens {max_batch_tokens}->{new_tokens} | "
                    f"max_sentences {max_sentences}->{new_sents}"
                )
                max_batch_tokens = new_tokens
                max_sentences = new_sents
                # Döngüyü kır: yeniden paketleme için outer while'a dön
                break

        else:
            # for döngüsü normal bitti (OOM break yok) -> devam edecek
            continue

        # OOM adapt break ile geldiysek while tekrar edecek (yeniden paketleme)
        continue

    return out


# -----------------------------
# main
# -----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="facebook/nllb-200-distilled-600M veya yerel klasör")
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--src_lang", type=str, required=True, help="örn: kmr_Latn / diq_Latn")
    ap.add_argument("--tgt_lang", type=str, required=True, help="örn: tur_Latn")
    ap.add_argument("--max_new_tokens", type=int, default=96)
    ap.add_argument("--max_batch_tokens", type=int, default=4096)
    ap.add_argument("--max_sentences", type=int, default=32)
    ap.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--dtype", choices=["float16", "bfloat16", "float32"], default="float16")
    ap.add_argument("--beams", type=int, default=1)
    ap.add_argument("--no_autocast", action="store_true")
    ap.add_argument("--compile", action="store_true")
    ap.add_argument("--checkpoint_every", type=int, default=200)
    ap.add_argument("--no_adaptive", action="store_true", help="OOM adaptif küçültmeyi kapat")
    args = ap.parse_args()

    torch.set_grad_enabled(False)
    if args.device.startswith("cuda"):
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.set_float32_matmul_precision("high")

    lines = [l.rstrip("\n") for l in args.src.read_text(encoding="utf-8").splitlines() if l.strip()]
    tok, model, dev, torch_dtype = load_model(args.model, args.dtype, args.device, args.compile)

    print(
        f"[info] device={dev} cuda_available={torch.cuda.is_available()} "
        f"model_device={next(model.parameters()).device} dtype={torch_dtype}"
    )

    chk_path = Path(str(args.out) + ".part")

    hyps = translate_nllb(
        lines,
        tok,
        model,
        args.src_lang,
        args.tgt_lang,
        args.max_new_tokens,
        args.max_batch_tokens,
        args.max_sentences,
        dev,
        use_autocast=(not args.no_autocast and args.dtype in {"float16", "bfloat16"}),
        beams=args.beams,
        checkpoint_path=chk_path,
        checkpoint_every=args.checkpoint_every,
        adaptive=(not args.no_adaptive),
        torch_dtype=torch_dtype,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(hyps), encoding="utf-8")
    print(f"[mt] model={args.model} dtype={args.dtype} beams={args.beams} lines={len(hyps)} -> {args.out}")
    if chk_path.exists():
        chk_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
