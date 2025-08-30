from __future__ import annotations
from typing import List, Dict, Any
from collections import Counter
import time
import re

from jiwer import wer, cer

_word_re = re.compile(r"\w+", flags=re.UNICODE)
_ARABIC = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")
_HEBREW = re.compile(r"[\u0590-\u05FF]")


def normalize_text_basic(s: str) -> str:
    # ASR değerlendirmesi için sade normalize: lowercase + noktalama kaldırma
    s = (s or "").lower()
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def compute_wer_cer(refs: List[str], hyps: List[str]) -> Dict[str, Any]:
    r = [normalize_text_basic(x) for x in refs]
    h = [normalize_text_basic(x) for x in hyps]
    return {
        "wer": float(wer(r, h)),
        "cer": float(cer(r, h)),
    }

def compute_rtf(total_audio_seconds: float, wall_clock_seconds: float) -> float:
    if wall_clock_seconds <= 0:
        return 0.0
    return float(wall_clock_seconds / total_audio_seconds)

def token_split(s: str) -> List[str]:
    return _word_re.findall((s or "").lower())

def tr_token_bias_ratio(pred_texts: List[str], tr_stopwords: set[str]) -> float:
    """
    Geçici 'bias' metriği: non-TR dillerde predicted token'ların
    ne kadarı TR stopword listesine düşüyor? (proxy)
    TODO: Wiki tabanlı TR lexicon hazır olunca bunu onunla değiştir.
    """
    tokens = []
    for t in pred_texts:
        tokens.extend(token_split(t))
    if not tokens:
        return 0.0
    hits = sum(1 for tok in tokens if tok in tr_stopwords)
    return hits / len(tokens)

# src/mdke/utils/metrics.py
import re

_ARABIC = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")  # Arabic/Farsi blocks
_HEBREW = re.compile(r"[\u0590-\u05FF]")

def latin_hawar_ratio(texts):
    """
    0..1 arası: 1.0 = tamamen Latin/Hawar, 0.0 = tamamen Arap/İbranî.
    texts: hipotez string listesi
    """
    total = 0
    bad = 0
    for t in texts:
        t = t or ""
        total += len(t)
        bad += len(_ARABIC.findall(t)) + len(_HEBREW.findall(t))
    if total == 0:
        return 1.0
    return max(0.0, 1.0 - bad / total)
