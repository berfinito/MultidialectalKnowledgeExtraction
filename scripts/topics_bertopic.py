from __future__ import annotations
import argparse, json, random
from pathlib import Path
from typing import List, Optional
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from mdke.utils.io import Paths, ensure_dirs, load_yaml

LANGS = ["tr", "kmr", "zza"]

def pick_input(paths: Paths, lang: str) -> Path:
    txt = paths.reports / "exports" / f"sentences_{lang}_final.txt"
    if txt.exists():
        return txt
    pq = paths.processed / f"text_sentences_{lang}_final.parquet"
    if pq.exists():
        return pq
    raise FileNotFoundError(f"Girdi bulunamadı (TXT ya da Parquet): {txt} | {pq}")

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

def save_topics(topic_model: BERTopic, docs: List[str], out_dir: Path, lang: str, tag: Optional[str] = None):
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"_{tag}" if tag else ""
    info = topic_model.get_topic_info()
    topics_json = []
    for _, row in info.iterrows():
        tid = int(row["Topic"])
        if tid == -1:
            top_terms = []
        else:
            terms = topic_model.get_topic(tid) or []
            top_terms = [{"term": t, "weight": float(w)} for t, w in terms]
        topics_json.append({
            "topic_id": tid,
            "size": int(row["Count"]),
            "name": row.get("Name", f"Topic {tid}"),
            "top_terms": top_terms[:20],
        })
    (out_dir / f"{lang}_bertopic_topics{suffix}.json").write_text(
        json.dumps(topics_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    doc_info = topic_model.get_document_info(docs)
    doc_map = pd.DataFrame({
        "doc_id": range(len(docs)),
        "topic": doc_info["Topic"].astype(int),
        "prob": doc_info.get("Probability", pd.Series([None]*len(docs))),
    })
    doc_map.to_parquet(out_dir / f"{lang}_bertopic_doc_topics{suffix}.parquet", index=False)

def save_info_md(out_dir: Path, lang: str, params: dict, n_docs: int, device: str, tag: Optional[str] = None):
    suffix = f"_{tag}" if tag else ""
    lines = [
        f"# BERTopic run ({lang})",
        "",
        f"- docs: {n_docs}",
        f"- device: {device}",
        f"- params: {json.dumps(params, ensure_ascii=False)}"
    ]
    (out_dir / f"{lang}_bertopic_info{suffix}.md").write_text("\n".join(lines), encoding="utf-8")

def infer_tag(sources: List[str]) -> Optional[str]:
    src = set(sources)
    if src == {"cv", "text"}: return "both"
    if src == {"cv"}: return "cv"
    if src == {"text"}: return "text"
    return None

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

def save_run_docs(out_dir: Path, lang: str, docs: List[str], tag: Optional[str]):
    suffix = f"_{tag}" if tag else ""
    fp = out_dir / f"{lang}_bertopic_docs{suffix}.txt"
    fp.write_text("\n".join(docs), encoding="utf-8")
    print(f"[topics] docs saved -> {fp}")

def run(cfg_path: Path, lang: str, limit: int | None, model_name: str, min_topic_size: int, seed: int,
        batch_size: int, sources: List[str] = ["text"], cv_weight: int = 1,
        umap_neighbors: int = 15, umap_components: int = 5, umap_min_dist: float = 0.0,
        hdb_min_cluster_size: Optional[int] = None, hdb_min_samples: Optional[int] = None):
    cfg = load_yaml(cfg_path)
    paths = Paths(
        raw=Path(cfg["paths"]["raw"]),
        interim=Path(cfg["paths"]["interim"]),
        processed=Path(cfg["paths"]["processed"]),
        reports=Path(cfg["paths"]["reports"]),
    )
    ensure_dirs(paths)
    random.seed(seed)
    torch.manual_seed(seed)

    # Dokümanları derle
    docs = build_docs(paths, lang, sources, limit, cv_weight=cv_weight)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    emb_model = SentenceTransformer(model_name, device=device)
    embeddings = emb_model.encode(
        docs, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True
    )

    params = {
        "language": "multilingual",
        "min_topic_size": min_topic_size,
        "calculate_probabilities": True,
        "verbose": True,
        "seed": seed,
        "umap": {"n_neighbors": umap_neighbors, "n_components": umap_components,
                 "min_dist": umap_min_dist, "metric": "cosine", "random_state": seed},
        "hdbscan": {"min_cluster_size": hdb_min_cluster_size, "min_samples": hdb_min_samples},
    }
    umap_model = UMAP(
        n_neighbors=params["umap"]["n_neighbors"],
        n_components=params["umap"]["n_components"],
        min_dist=params["umap"]["min_dist"],
        metric=params["umap"]["metric"],
        random_state=params["umap"]["random_state"],
    )
    hdbscan_model = None
    if params["hdbscan"]["min_cluster_size"] or params["hdbscan"]["min_samples"]:
        hdbscan_model = HDBSCAN(
            min_cluster_size=params["hdbscan"]["min_cluster_size"] or 15,
            min_samples=params["hdbscan"]["min_samples"] or None,
            metric="euclidean",
            cluster_selection_method="eom",
            prediction_data=True,
        )

    topic_model = BERTopic(
        language=params["language"],
        min_topic_size=params["min_topic_size"],
        calculate_probabilities=params["calculate_probabilities"],
        verbose=params["verbose"],
        nr_topics=None,
        low_memory=True,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
    )
    topics, probs = topic_model.fit_transform(docs, embeddings=embeddings)

    out_dir = paths.reports / "topics"
    tag = infer_tag(sources)
    out_dir.mkdir(parents=True, exist_ok=True)
    save_run_docs(out_dir, lang, docs, tag)
    save_topics(topic_model, docs, out_dir, lang, tag=tag)
    save_info_md(out_dir, lang, params | {"model_name": model_name, "sources": sources, "cv_weight": cv_weight},
                 n_docs=len(docs), device=device, tag=tag)
    print(f"[topics] -> {out_dir}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--lang", type=str, choices=LANGS, default="tr")
    ap.add_argument("--limit", type=int, default=100000, help="örnekleme (doc sayısı); <=0 hepsi")
    ap.add_argument("--model_name", type=str, default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    ap.add_argument("--min_topic_size", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--batch_size", type=int, default=256)
    ap.add_argument("--sources", type=str, default="text", help="cv,text veya both")
    ap.add_argument("--cv_weight", type=int, default=1)
    # Yeni CLI: UMAP/HDBSCAN
    ap.add_argument("--umap_neighbors", type=int, default=15)
    ap.add_argument("--umap_components", type=int, default=5)
    ap.add_argument("--umap_min_dist", type=float, default=0.0)
    ap.add_argument("--hdb_min_cluster_size", type=int, default=None)
    ap.add_argument("--hdb_min_samples", type=int, default=None)

    args = ap.parse_args()
    sources = ["cv","text"] if args.sources == "both" else [s.strip() for s in args.sources.split(",") if s.strip()]

    run(args.config, args.lang, None if args.limit <= 0 else args.limit,
        args.model_name, args.min_topic_size, args.seed, args.batch_size,
        sources=sources, cv_weight=args.cv_weight,
        umap_neighbors=args.umap_neighbors, umap_components=args.umap_components, umap_min_dist=args.umap_min_dist,
        hdb_min_cluster_size=args.hdb_min_cluster_size, hdb_min_samples=args.hdb_min_samples)