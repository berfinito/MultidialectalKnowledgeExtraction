# -*- coding: utf-8 -*-
import re
from typing import Literal

# Arap/Fars bloklarını yakalamak için kaba kontrol
ARABIC_BLOCK = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")

# Minimal mapping (Kurmançî Hawar odaklı) — gerekirse genişletiriz
MAP_BASE = {
    "ا":"a","أ":"a","إ":"i","آ":"a","ب":"b","پ":"p","ت":"t","ث":"s","ج":"c","چ":"ç",
    "ح":"h","خ":"x","د":"d","ذ":"z","ر":"r","ز":"z","ژ":"j","س":"s","ش":"ş","ص":"s",
    "ض":"z","ط":"t","ظ":"z","ع":"’","غ":"g","ف":"f","ق":"q","ك":"k","ک":"k","گ":"g",
    "ل":"l","م":"m","ن":"n","ه":"h","ة":"e","و":"w","ؤ":"u","ي":"y","ى":"y","ئ":"î",
    "ٰ":"", "‌":" ", "ٔ":"", "٠":"0","١":"1","٢":"2","٣":"3","٤":"4","٥":"5","٦":"6","٧":"7","٨":"8","٩":"9",
    # Kurdish-specific forms
    "ۆ":"o","ێ":"ê","ی":"y","ە":"e","ۆ":"o","ۇ":"u","ۈ":"ü",  # bazıları nadir/lehçesel
}

def translit_char(ch: str) -> str:
    return MAP_BASE.get(ch, ch)

def transliterate(text: str, mode: Literal["strict","light"]="strict") -> str:
    if not ARABIC_BLOCK.search(text):
        return text  # hızlı çıkış
    out = "".join(translit_char(c) for c in text)

    # Ortak normalize
    out = re.sub(r"\s+", " ", out).strip()

    if mode == "light":
        # çok hafif hece kuralları (risk düşük, kazanç orta)
        # و -> w/u/û ayrımı: basit heceleme yerine konservatif iyileştirme
        out = out.replace("iy", "îy").replace("uy", "ûy")  # örnek nazik dokunuş
        # çift tırnak/düzeltme işaretleri sadeleştirme
        out = out.replace("’", "'")

    return out

def has_arabic(text: str) -> bool:
    return bool(ARABIC_BLOCK.search(text))
