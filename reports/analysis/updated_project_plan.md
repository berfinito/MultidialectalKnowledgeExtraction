# Çok‑Lehçeli Konuşmadan Bilgi Çıkarımı (TR/KMR/ZZA) — Plan v1 Final

Tez Başlığı (öneri):
- TR: Konuşmadan Bilgi Grafına: Türkçe, Kurmanci ve Zazaca İçin Çok‑Lehçeli Bilgi Çıkarımı
- EN: From Speech to Knowledge Graphs: Multidialectal Knowledge Extraction for Turkish, Kurmanji, and Zazaki

## 1. Problem, Motivasyon ve Etki

Problem:
- Düşük kaynaklı TR/KMR/ZZA; lehçe farkları (fonoloji, yazım, kelime) ve script drift (Latin/Hawar) ASR ve metin işlemede hata üretir.
- Veri azlığı → yüksek WER/CER; konu/anahtar terim kapsamı sınırlı.

Motivasyon:
- Kültürel miras, erişilebilirlik, adil teknoloji; çok‑lehçeli sistemlerde araştırma boşluğunu kapatmak.

Etki:
- Temizlenmiş, dedup edilmiş TR/KMR/ZZA metin korpusları (paragraf+cümle) üretildi:
  - data/processed/text_corpus_{tr,kmr,zza}_final.parquet
  - data/processed/text_sentences_{tr,kmr,zza}_final.parquet
- Per‑dil ASR model/politika seçildi:
  - TR: openai/whisper-medium; KMR/ZZA: openai/whisper-large-v2
- Topics/keywords; co‑occurrence tabanlı Knowledge Graph (PMI/TF‑IDF), merkeziyet ve görselleştirmeler:
  - reports/analysis/{tr,kmr,zza}_kg_{full,top15}_{pmi,tfidf}.tsv
  - centrality, plots (PNG), exports (GEXF/GraphML)

## 2. Araştırma Soruları

- RQ1: Çok‑lehçeli ASR’de model/ayar seçimi nasıl değişiyor? Cross‑dialect transfer ne kadar başarılı?
  - Uygulandı; raporlar: reports/asr_compare_medium_large.md, reports/asr_best_medium_large.md ve per‑run JSON’lar.
- RQ2: Wikipedia/Zazagorani temizleme/normalizasyon kararları kaliteyi nasıl etkiliyor?
  - Uygulandı; sprint‑3/4 raporları, n‑gram ve text_stats dosyaları.
- RQ3: Topic/keyword çıkarımı “text vs cv vs both” varyantlarında nasıl farklılaşıyor?
  - Uygulandı; reports/analysis/topic_coherence.md, keyword_coverage.md, keyword_overlap.md.
- RQ4: KG, lehçeler arası ortaklık ve farkları gösterebiliyor mu?
  - Uygulandı; co‑occurrence KG + centrality/komponent analizi + PNG/GEXF/GraphML.

## 3. Veri Kaynakları ve Lisans

- Common Voice v22.0 (TR/KMR/ZZA) — CC0 (data/raw/commonvoice/*)
- Wikipedia dumps: trwiki, kuwiki, diqwiki — CC‑BY‑SA (data/raw/wiki/*)
- Zazagorani — VarDial (data/raw/zazagorani/*)
- Etik: Kişisel veri yok; lisans uyumlu.

## 4. Metodoloji ve Pipeline

Akış: speech → ASR → text ingest/temizlik → segment/dedup → topics/keywords → KG → analysis

### ASR Katmanı

Teknolojiler:
- Hugging Face Transformers Whisper; Python 3.11; CUDA (opsiyonel); jiwer (WER/CER); librosa/soundfile (IO).
- Kod: src/mdke/asr/whisper_infer.py; CT2 pilot: src/mdke/asr/whisper_infer_ct2.py
- Yardımcılar: src/mdke/utils/metrics.py (RTF, bias, ratio), src/mdke/utils/io.py

Final Model/Politika:
- TR: openai/whisper-medium, forced_language=tr, bias=OFF, beam=1
- KMR/ZZA: openai/whisper-large-v2, language auto, bias=OFF, beam=1
- min_new_tokens ≈ 8–12, max_new_tokens ≈ 120–160; dynamic input length açık
- forced_decoder_ids generation_config üzerinden; attention_mask generate’e verilmez

Değerlendirme:
- Raporlar: reports/asr_whisper_{lang}_{split}*.json
- Karşılaştırma tabloları: reports/asr_compare_medium_large.md, reports/asr_best_medium_large.md
- Koşu dizini: reports/asr_index.md

Beam & Fusion (Ek):
- Beam JSONL dump (alt hip+skor): data/interim/asr/*_beams.jsonl
- Fusion pilot (yeniden puanlama iskeleti): scripts/asr_decode_fusion.py; raporlar reports/exports/fusion_*.md
- Şema test: tests/test_asr_beams_schema.py

### Text Katmanı

Teknolojiler/Skriptler:
- scripts/text_build_corpus.py, text_filter_sections.py, text_postfilter_media.py
- Normalizasyon: NFKC + TR İ/ı kuralı; scripts/fix_mojibake.py
- Segment: scripts/text_sentence_segment.py; Dedup: scripts/text_dedup.py
- N‑gram: scripts/text_ngrams.py; Rapor: scripts/text_report.py

Artefaktlar:
- data/processed/text_corpus_{lang}_final.parquet
- data/processed/text_sentences_{lang}_final.parquet
- reports/ngrams/*, reports/text_stats/*

### Topics & Keywords

Teknolojiler:
- BERTopic (UMAP + HDBSCAN). LDA baseline planlanmıştı, bu sürümde kullanılmadı.
- Keywords: YAKE, KeyBERT; TF‑IDF karşılaştırmalı analizler
- Scriptler: scripts/topics_bertopic.py, compute_topic_coherence.py, topic_representatives.py, trim_representatives.py, keywords_extract.py, keywords_overlap_analysis.py, keywords_coverage.py

Artefaktlar:
- reports/topics/*_bertopic_topics*.json, *_doc_topics*.parquet, *_info*.md
- reports/keywords/{lang}_{yake|keybert}_{text|cv|both}.json
- Analizler: reports/analysis/topic_coherence.md, keyword_overlap.md, keyword_coverage.md
- Representatives (nitel doğrulama): reports/analysis/representatives_{tr,kmr,zza}_{text,cv,both}*.md

### Knowledge Graph

Uygulanan Yaklaşım:
- Topic temsilci terimlerinden co‑occurrence KG; ağırlık: PMI (ln) ve TF‑IDF
- Scriptler: scripts/kg_from_reps_terms.py, kg_weighting.py
- Merkeziyet/Topoloji: scripts/kg_centrality_analysis.py (degree, weighted degree, eigenvector, betweenness (örneklem), clustering, components)
- Görselleştirme: scripts/plot_kg.py (PNG)
- Export: scripts/export_kg.py (GEXF/GraphML)

Artefaktlar:
- TSV + stats: reports/analysis/{tr,kmr,zza}_kg_{full,top15}_{pmi,tfidf}.{tsv,json}
- Centrality: reports/analysis/centrality/*.json, summary.md
- PNG: reports/analysis/plots/*_top{150|200}.png
- GEXF/GraphML: reports/analysis/exports/*.gexf, *.graphml
- Yorum: reports/analysis/kg_interpretation.md

Not (Plan Değişikliği):
- spaCy NER + Wikidata linking + Louvain communities (orijinal plan) bu sürümde yapılmadı; co‑occurrence KG ile merkeziyet/komponent analizi uygulandı.

## 5. Sprint Roadmap (Gerçekleşen)

- Sprint‑1: ASR baseline + bias/beam aramaları → Tamam
- Sprint‑2: Cross‑dialect + model seçimi + confusion → Tamam
- Sprint‑3: Text ingest + temizlik + n‑gram → Tamam
- Sprint‑4: Unicode norm + segment + dedup → Tamam
- Sprint‑5: Topics/Keywords + KG (PMI/TF‑IDF) + çizimler/exportlar + ablation → Tamam
- Sprint‑6: Case Studies → CS‑1/2/4 tamam; CS‑3 (MT drift) metodoloji yazıldı, deferred (case3_original_vs_mt.md)

## 6. Metrikler

- ASR: WER, CER, RTF, latin_hawar_ratio, tr_token_bias
- Text: retention %, n‑gram QC
- Topics: #topics, coherence (c_v, c_npmi), outlier%
- Keywords: coverage, Jaccard overlap, multiword%
- KG: node/edge, degree/wDegree, eigenvector, betweenness p90, components

## 7. Teslimatlar

- ASR raporları: reports/asr_whisper_{lang}_{split}_{variant}.json; tablolar: asr_compare_medium_large.md, asr_best_medium_large.md
- ASR beam & fusion pilot: data/interim/asr/*_beams.jsonl, reports/exports/fusion_*.md
- Text corpus & sentences: data/processed/text_corpus_*_final.parquet, text_sentences_*_final.parquet
- N‑gramlar / text_stats: reports/ngrams/*, reports/text_stats/*
- Topics/Keywords: reports/topics/*.json, reports/keywords/*.json
- KG: reports/analysis/*_kg_*_{pmi,tfidf}.tsv + *_stats.json + plots/ + exports/
- Case Studies: reports/analysis/case{1,2,4}.md; CS‑3 metodoloji: case3_original_vs_mt.md
- Sprint özetleri: reports/sprint-{1..4}-summary.{json,md}; S5/6 konsolide: reports/analysis/thesis_tables.md
- Repro bundle: reports/env.txt, env_freeze.txt, versions.json, git_commit.txt, gpu.txt

## 8. Riskler & Önlemler

- Bias prompt → OFF; fallback ve erken kapama mantığı
- TR forced lang; KMR/ZZA auto
- Unicode İ/ı → normH
- Dedup exact (near‑dup LSH: future work)
- KG entity linking / Louvain: v2
- MT drift (CS‑3): kalite eşiği (ChrF>40) sonrası