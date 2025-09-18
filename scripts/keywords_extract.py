"""
Extract keywords per language and variant (text/cv/both) using supported methods.

Methods:
- YAKE
- KeyBERT

Inputs:
- reports/topics/{lang}_bertopic_docs_{variant}.txt (when methods need docs)
- Or any method-specific inputs already used in the script

Outputs:
- reports/keywords/{lang}_{method}_{variant}.json
  Each file is a JSON array of [term, score] pairs in descending importance.

Usage:
  python scripts/keywords_extract.py --lang tr --method yake --variant both
Notes:
  - Normalization is assumed to be handled earlier in the pipeline (textnorm).
  - Keep method parameters stable across variants for fair comparisons.
"""
from __future__ import annotations
import argparse, json, random
from pathlib import Path
import pandas as pd
from mdke.utils.io import Paths, ensure_dirs, load_yaml
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from typing import List, Dict, Tuple, Optional
import unicodedata
import re
import numpy as np

# Opsiyonel: KeyBERT ve YAKE importları
try:
    from keybert import KeyBERT
except Exception:
    KeyBERT = None
try:
    import yake
except Exception:
    yake = None

LANGS = ["tr", "kmr", "zza"]

def set_seed(seed: int | None):
    if seed is None:
        return
    random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass
    np.random.seed(seed)

def infer_tag(sources: List[str]) -> Optional[str]:
    s = set(sources)
    if s == {"cv","text"}: return "both"
    if s == {"cv"}: return "cv"
    if s == {"text"}: return "text"
    return None

def pick_input(paths: Paths, lang: str) -> Path:
    txt = paths.reports / "exports" / f"sentences_{lang}_final.txt"
    if txt.exists():
        return txt
    pq = paths.processed / f"text_sentences_{lang}_final.parquet"
    if pq.exists():
        return pq
    raise FileNotFoundError(f"Girdi yok: {txt} | {pq}")

def load_sentences(src: Path, limit: int | None) -> List[str]:
    if src.suffix.lower() == ".txt":
        lines = [l.strip() for l in src.read_text(encoding="utf-8").splitlines()]
        s = [l for l in lines if l]
    else:
        df = pd.read_parquet(src)
        for c in ["sentence", "text_norm", "text"]:
            if c in df.columns:
                col = c
                break
        else:
            raise ValueError(f"Uygun kolon yok: {list(df.columns)}")
        s = df[col].astype(str).map(str.strip)
        s = s[s.str.len() > 0].tolist()
    if limit and len(s) > limit:
        random.shuffle(s)
        s = s[:limit]
    return s

def _tr_lower(s: str) -> str:
    return s.replace("I", "ı").replace("İ", "i").lower()

_punct_strip = " \"'‘’“”.,;:!?()[]{}<>~`|/\\"
_roman_re = re.compile(r"^[ivxlcdm]{1,7}$", re.I)
_isbn_re = re.compile(r"(?i)\b(issn|isbn|oclc|doi)\b")
_num_re = re.compile(r"\d")

def _normalize_term(term: str) -> str:
    t = unicodedata.normalize("NFKC", term)
    t = t.strip(_punct_strip)
    t = re.sub(r"\s+", " ", t)
    t = _tr_lower(t)
    return t.strip()

def _load_stopwords(lang: str) -> Optional[set[str]]:
    sw_dir = Path("configs/stopwords")
    cand = {
        "tr": sw_dir / "tr.txt",
        "kmr": sw_dir / "kmr.txt",
        "zza": sw_dir / "zza.txt",
    }.get(lang)
    words: set[str] = set()
    if cand and cand.exists():
        words |= {w.strip() for w in cand.read_text(encoding="utf-8").splitlines() if w.strip()}
    # Karma içerik için birkaç İngilizce yaygın sözcüğü de ekleyelim
    words |= {"the", "of", "and", "in", "to", "for"}
    return words or None

def _good_term(t: str) -> bool:
    if len(t) < 3:
        return False
    if _num_re.search(t):
        return False
    if len(t) <= 4 and _roman_re.match(t):
        return False
    if _isbn_re.search(t):
        return False
    letters = sum(ch.isalpha() for ch in t)
    if letters / max(1, len(t)) < 0.6:
        return False
    return True

def run_yake(docs: List[str], lang: str, topk: int = 200) -> List[Tuple[str, float]]:
    if yake is None:
        raise ImportError("yake yüklü değil: pip install yake")
    lan = "tr" if lang == "tr" else "en"
    text = "\n".join(docs)
    kw = yake.KeywordExtractor(lan=lan, n=1, top=topk*5, dedupLim=0.9, windowsSize=1)
    raw = kw.extract_keywords(text)
    out: Dict[str, float] = {}
    for term, score in raw:
        t = _normalize_term(term)
        if not t or not _good_term(t):
            continue
        out[t] = min(out.get(t, score), float(score))
    return sorted(out.items(), key=lambda x: x[1])[:topk]

def run_keybert(
    docs: List[str],
    model_name: str,
    topk: int = 200,
    chunk_size: int = 2000,
    use_maxsum: bool = True,
    use_mmr: bool = False,
    mmr_diversity: float = 0.4,
    nr_candidates: int = 30,
    top_n: int = 10,
    ngram_min: int = 1,
    ngram_max: int = 2,
    lang: Optional[str] = None,
) -> List[Tuple[str, float]]:
    if KeyBERT is None:
        raise ImportError("keybert yüklü değil: pip install keybert")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    st_model = SentenceTransformer(model_name, device=device)
    print(f"[KeyBERT] device={device}, model={model_name}, chunk_size={chunk_size}, "
          f"use_maxsum={use_maxsum}, use_mmr={use_mmr}, diversity={mmr_diversity}, "
          f"nr_candidates={nr_candidates}, top_n={top_n}, ngram=({ngram_min},{ngram_max})")
    kb = KeyBERT(model=st_model)
    agg: Dict[str, float] = {}
    stopwords = _load_stopwords(lang) if lang else None
    for start in tqdm(range(0, len(docs), chunk_size), desc="KeyBERT chunks", unit="chunk"):
        chunk = docs[start:start+chunk_size]
        results = kb.extract_keywords(
            chunk,
            keyphrase_ngram_range=(ngram_min, ngram_max),
            stop_words=None,  # pre-stopword filtre yok; post aşamada filtreliyoruz
            use_maxsum=use_maxsum,
            use_mmr=use_mmr,
            diversity=mmr_diversity,
            nr_candidates=nr_candidates,
            top_n=top_n,
        )
        for per_doc in results:
            for term, score in per_doc:
                t = _normalize_term(term)
                if not t or not _good_term(t) or (stopwords and t in stopwords):
                    continue
                agg[t] = max(agg.get(t, 0.0), float(score))
    result = sorted(agg.items(), key=lambda x: x[1], reverse=True)[:topk]
    if result:
        mw_ratio = sum(1 for t,_ in result if len(t.split()) >= 2) / len(result)
        print(f"[KeyBERT] multi_word_ratio={mw_ratio:.3f}")
    return result

def load_cv_sentences(paths: Paths, lang: str) -> List[str]:
    import glob
    pat = str(paths.processed / f"cv_{lang}_*.parquet")
    files = glob.glob(pat)
    out: List[str] = []
    for fp in files:
        df = pd.read_parquet(fp)
        for c in ["sentence", "text_norm", "text"]:
            if c in df.columns:
                series = df[c].astype(str).map(str.strip)
                out.extend([s for s in series.tolist() if s])
                break
        else:
            print(f"[WARN] CV parquet'te beklenen kolon yok (sentence/text_norm/text): {fp} -> {list(df.columns)}")
    return out

def load_text_sentences(paths: Paths, lang: str) -> List[str]:
    src = pick_input(paths, lang)
    return load_sentences(src, None)

def build_docs(paths: Paths, lang: str, sources: List[str], limit: int | None, cv_weight: int = 1) -> List[str]:
    docs: List[str] = []
    if "cv" in sources:
        cv_docs = load_cv_sentences(paths, lang)
        docs.extend(cv_docs * max(cv_weight, 1))
    if "text" in sources:
        docs.extend(load_text_sentences(paths, lang))
    random.shuffle(docs)
    if limit and len(docs) > limit:
        docs = docs[:limit]
    return docs

def run(cfg_path: Path, lang: str, limit: int | None, methods: List[str], model_name: str, topk: int,
        chunk_size: int = 2000, use_maxsum: bool = True, use_mmr: bool = False, mmr_diversity: float = 0.4,
        nr_candidates: int = 30, top_n: int = 10, ngram_min: int = 1, ngram_max: int = 2,
        sources: List[str] = ["text"], cv_weight: int = 1):
    cfg = load_yaml(cfg_path)
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)

    docs = build_docs(paths, lang, sources, limit, cv_weight=cv_weight)
    outdir = paths.reports / "keywords"
    outdir.mkdir(parents=True, exist_ok=True)
    tag = infer_tag(sources)
    suffix = f"_{tag}" if tag else ""

    # Parametre info kaydı
    run_info = {
        "lang": lang,
        "sources": sources,
        "cv_weight": cv_weight,
        "limit": limit,
        "methods": methods,
        "model_name": model_name,
        "topk": topk,
        "chunk_size": chunk_size,
        "use_maxsum": use_maxsum,
        "use_mmr": use_mmr,
        "mmr_diversity": mmr_diversity,
        "nr_candidates": nr_candidates,
        "top_n": top_n,
        "ngram_min": ngram_min,
        "ngram_max": ngram_max,
    }
    (outdir / f"{lang}_keywords_params{suffix}.json").write_text(
        json.dumps(run_info, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if "yake" in methods:
        pairs = run_yake(docs, lang, topk=topk)
        (outdir / f"{lang}_yake{suffix}.json").write_text(json.dumps(pairs, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[keywords] YAKE -> {outdir / f'{lang}_yake{suffix}.json'}")

    if "keybert" in methods:
        pairs = run_keybert(
            docs, model_name=model_name, topk=topk, chunk_size=chunk_size,
            use_maxsum=use_maxsum, use_mmr=use_mmr, mmr_diversity=mmr_diversity,
            nr_candidates=nr_candidates, top_n=top_n,
            ngram_min=ngram_min, ngram_max=ngram_max,
            lang=lang,
        )
        (outdir / f"{lang}_keybert{suffix}.json").write_text(json.dumps(pairs, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[keywords] KeyBERT -> {outdir / f'{lang}_keybert{suffix}.json'}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--lang", type=str, choices=LANGS, default="tr")
    ap.add_argument("--limit", type=int, default=100000)
    ap.add_argument("--methods", type=str, default="yake,keybert")
    ap.add_argument("--model_name", type=str, default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    ap.add_argument("--topk", type=int, default=200)
    ap.add_argument("--chunk_size", type=int, default=2000)
    ap.add_argument("--no_maxsum", action="store_true")
    ap.add_argument("--use_mmr", action="store_true")
    ap.add_argument("--mmr_diversity", type=float, default=0.4)
    ap.add_argument("--keybert_nr_candidates", type=int, default=30)
    ap.add_argument("--keybert_topn", type=int, default=10)
    ap.add_argument("--ngram", type=str, default="1,2", help="ör. 1,1 veya 1,2")
    ap.add_argument("--sources", type=str, default="text", help="cv,text veya both")
    ap.add_argument("--cv_weight", type=int, default=1)
    ap.add_argument("--seed", type=int, default=None, help="Deterministik tekrar için seed")
    args = ap.parse_args()

    set_seed(args.seed)
    nmin, nmax = (int(x) for x in args.ngram.split(","))
    sources = ["cv", "text"] if args.sources == "both" else [s.strip() for s in args.sources.split(",") if s.strip()]

    run(
        args.config,
        args.lang,
        None if args.limit <= 0 else args.limit,
        [m.strip() for m in args.methods.split(",") if m.strip()],
        args.model_name,
        args.topk,
        chunk_size=args.chunk_size,
        use_maxsum=not args.no_maxsum,
        use_mmr=args.use_mmr,
        mmr_diversity=args.mmr_diversity,
        nr_candidates=args.keybert_nr_candidates,
        top_n=args.keybert_topn,
        ngram_min=nmin, ngram_max=nmax,
        sources=sources,
        cv_weight=args.cv_weight,
    )