# Final Summary — Multidialectal Knowledge Extraction (TR/KMR/ZZA)

Bu özet, v1 sürümünde üretilen ana bulguları ve artefaktları tek yerde toplar.

## ASR — Model Seçimi ve Temel Sonuçlar
- Nihai politika: TR → whisper-medium (forced=tr), KMR/ZZA → whisper-large-v2 (auto), bias=OFF, beam=1.
- Karşılaştırma tabloları:
  - [reports/asr_compare_medium_large.md](../asr_compare_medium_large.md)
  - [reports/asr_best_medium_large.md](../asr_best_medium_large.md)
- Beam & Fusion (pilot):
  - Beams JSONL: data/interim/asr/*_beams.jsonl
  - Fusion raporları: [reports/exports/fusion_*](../exports/)
- Örnek run raporları: reports/asr_whisper_*_validation_{greedy_fast|beam*}.json

## Text — Ingest, Temizlik, Segment, Dedup
- Final korpuslar:
  - data/processed/text_corpus_{tr,kmr,zza}_final.parquet
  - data/processed/text_sentences_{tr,kmr,zza}_final.parquet
- QC: reports/ngrams/*, reports/text_stats/*

## Topics & Keywords
- BERTopic varyantları: reports/topics/*_bertopic_topics*.json
- Keywords: reports/keywords/{lang}_{yake|keybert}_{text|cv|both}.json
- Analizler:
  - [reports/analysis/topic_coherence.md](topic_coherence.md)
  - [reports/analysis/keyword_overlap.md](keyword_overlap.md)
  - [reports/analysis/keyword_coverage.md](keyword_coverage.md)
  - Representatives: reports/analysis/representatives_*_both*.md

## Knowledge Graph (PMI/TF‑IDF)
- TSV + Stats: reports/analysis/{tr,kmr,zza}_kg_{full,top15}_{pmi,tfidf}.{tsv,json}
- Centrality:
  - Per‑graph JSON: reports/analysis/centrality/*.json
  - Özet: [reports/analysis/centrality/summary.md](centrality/summary.md)
- Görseller: reports/analysis/plots/* (PNG)
- Export: reports/analysis/exports/* (.gexf, .graphml)
- Yorum: [reports/analysis/kg_interpretation.md](kg_interpretation.md)

## Case Studies
- CS‑1/2/4: reports/analysis/case{1,2,4}.md
- CS‑3 (MT drift): metodoloji — reports/analysis/case3_original_vs_mt.md

## Reproducibility
- Ortam ve sürümler:
  - [reports/env.txt](../env.txt), [reports/env_freeze.txt](../env_freeze.txt)
  - [reports/versions.json](../versions.json), [reports/git_commit.txt](../git_commit.txt), [reports/gpu.txt](../gpu.txt)
- Hızlı komutlar için README’nin “v1 Quickstart” bölümüne bakınız.