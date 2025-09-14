from __future__ import annotations
import unicodedata
import re

# Normalize curly quotes/apostrophes to ASCII
APOSTROPHES = {
    "\u2018": "'", "\u2019": "'", "\u201B": "'",
    "\u201C": '"', "\u201D": '"',
    "\u00B4": "'", "\u02BC": "'",
}

def _replace_apostrophes(s: str) -> str:
    return s.translate(str.maketrans(APOSTROPHES))

def _strip_combining_dot_above(s: str) -> str:
    # Remove combining dot above (U+0307) that causes "i̇" issues
    return s.replace("\u0307", "")

def turkish_lower(s: str) -> str:
    # Special-case before lower: İ -> i, I -> ı
    s = s.replace("İ", "i").replace("I", "ı")
    s = s.lower()
    s = _strip_combining_dot_above(s)
    return s

def generic_lower(s: str) -> str:
    # Keep diacritics for KMR/ZZA; just lower
    return s.lower()

def normalize_text(text: str, lang: str) -> str:
    """
    Normalize Unicode + whitespace:
    - NFKC compose
    - Standardize quotes/apostrophes
    - Language-aware lower (TR fixes İ/ı)
    - Collapse whitespace
    """
    if not text:
        return ""
    s = unicodedata.normalize("NFKC", text)
    s = _replace_apostrophes(s)
    if lang == "tr":
        s = turkish_lower(s)
    else:
        s = generic_lower(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s