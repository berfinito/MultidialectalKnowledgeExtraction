# src/mdke/utils/langmap.py
from __future__ import annotations

# Canonical codes we use everywhere in outputs/paths/reports:
#   tr, kmr, zza
# Accepted aliases map to the same canonical code:
#   ku  -> kmr
#   diq -> zza
_ALIASES = {
    "tr": "tr",
    "tur": "tr",
    "kmr": "kmr",
    "ku": "kmr",
    "kur": "kmr",
    "zza": "zza",
    "diq": "zza",
}

def normalize_lang(code: str) -> str:
    """
    Normalize input language code to canonical codes we use in the repo.

    Accepted:
      - 'tr' (or 'tur')        -> 'tr'
      - 'kmr', 'ku', 'kur'     -> 'kmr'
      - 'zza', 'diq'           -> 'zza'
    """
    code = (code or "").strip().lower()
    if code not in _ALIASES:
        raise ValueError(
            f"Unsupported language code: {code!r}. "
            "Use one of tr|kmr|zza (aliases: ku->kmr, diq->zza)."
        )
    return _ALIASES[code]
