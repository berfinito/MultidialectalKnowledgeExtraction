# PROJECT MAP — MultidialectalKnowledgeExtraction (v1, 2025-09-18)

Bu doküman, depo yapısını “hangi dosya/klasör ne işe yarar ve neyi etkiler” ekseninde listeler. Amaç: tekrarlanabilirlik, izlenebilirlik ve bakım kolaylığı.

## Top-level
- Makefile
  - final: Sprint-4 özetlerini üretir.
  - kg_centrality, kg_plots, kg_exports, final_v1: KG analiz/çizim/export ve test akışlarını çalıştırır.
- pyproject.toml
  - Python paket meta ve bağımlılık yönetimi (poetry/pip uyumlu).
- README.md
  - ASR sonuç özeti, model/politika, yeniden çalıştırma komutları, v1 final quickstart ve artifacts listesi.
- sources.json
  - Veri kaynakları referansı.
- configs/
  - experiment.yaml, experiment_large.yaml
    - ASR ve pipeline konfigleri; whisper_infer.py ve pek çok script bunları okur.
  - prompts/{kmr,zza}_bias.txt
    - KMR/ZZA için opsiyonel bias metni (varsayılan OFF).
  - stopwords/{tr,kmr,zza}.txt
    - Metrikler ve bazı analizlerde kullanılır (örn. tr_token_bias).
- data/
  - raw/ (Git dışı): Ham veri (Common Voice, Wikipedia dumps, Zazagorani).
  - interim/ (Git dışı): Ara çıktılar (ASR JSONL, beam JSONL).
  - processed/: Temizlenmiş/segment/dedup metin korpusları (parquet).
    - text_corpus_{lang}_final.parquet; text_sentences_{lang}_final.parquet
    - cv_{lang}_{split}.parquet
- reports/ (Git’te izlenir; sadece _trash, _inspect, logs ve *.zip ignore)
  - asr_*.json
    - ASR per-run raporları (WER, CER, RTF, ayar özetleri).
  - asr_compare_medium_large.md, asr_best_medium_large.md
    - Model karşılaştırma tabloları.
  - asr_index.{md,json}
    - ASR koşularının indeks/özeti.
  - confusion_*.json
    - Karakter karışıklığı (ê→e, î→i, û→u) gibi analizler.
  - sprint-*-summary.{json,md}
    - Sprint 1–4 özetleri.
  - env.txt, env_freeze.txt, versions.json, git_commit.txt, gpu.txt
    - Tekrarlanabilirlik artefaktları (pip freeze, sürümler, commit, GPU).
  - deliverable_*.zip, thesis_bundle_ml.zip
    - Dışa aktarma paketleri (isteğe bağlı; zip default ignore).
  - exports/
    - Fusion pilot sonuç markdown’ları (fusion_whisper_*).
  - topics/
    - {lang}_bertopic_topics*.json, *_doc_topics*.parquet, *_info*.md
  - keywords/
    - {lang}_{yake|keybert}_{text|cv|both}.json
  - analysis/
    - *_kg_{full,top15}_{pmi,tfidf}.tsv
      - Knowledge Graph edge listeleri (source, target, weight).
    - *_kg_{full,top15}_{pmi,tfidf}_stats.json
      - Kenar ağırlığı istatistikleri (min/avg/max/edges).
    - centrality/
      - {lang}_kg_*_centrality.json (degree/wDegree/eigenvector/betweenness/cluster/components)
      - summary.md (toplu tablo)
    - plots/
      - *_kg_*_top{N}.png (Görselleştirme)
    - exports/
      - *.gexf, *.graphml (Gephi/Cytoscape için fiziksel KG exportları)
    - case{1..4}_*.md
      - Vaka çalışmaları (CS-3 metodoloji; diğerleri uygulanmış).
    - keyword_coverage.md, keyword_overlap.md, topic_coherence.md, representatives_*.md
    - kg_interpretation.md
    - project_execution_summary.md
    - final_summary.md (v1 artefaktlarının üst-özet)
    - updated_project_plan.md (güncel plan/metod/çıktı)
    - future_work.md

## scripts/ (ana boru hattı betikleri)
ASR:
- asr_compare_models.py
  - Medium vs Large-v2 karşılaştırma tablosu üretir (WER/CER/RTF deltalı).
  - Çıktı: reports/asr_compare_medium_large.md, reports/asr_best_medium_large.md
- asr_decode_fusion.py
  - Beam JSONL üzerinden yeniden puanlama (dummy LM) pilotu; λ-grid ile AvgWER raporu.
  - Çıktı: reports/analysis/fusion_pilot_results.md ve lang-specific md (exports/)
- asr_inventory.py, asr_cleanup.py, asr_export_texts.py
  - ASR veri envanteri/temizliği/dışa metin aktarımı (yardımcı).
- asr_runtime_summary.py, asr_collect_summary.py, asr_bias_effect.py
  - Runtime ve bias etkisine dair özetler (opsiyonel).

Text:
- text_build_corpus.py, text_filter_sections.py, text_postfilter_media.py
  - Wiki/Zazagorani ingest ve temizlik (markup, URL, tablo, medya kalıntısı).
- text_sentence_segment.py
  - Regex tabanlı cümle segmentasyonu.
- text_dedup.py
  - Exact dedup.
- text_export_plain.py, text_export_samples.py
  - Düz metin export ve örnekleme.
- text_ngrams.py, text_report.py
  - n-gram üretimi ve metin raporları.

Topics & Keywords:
- topics_bertopic.py
  - BERTopic varyantları (text/cv/both), UMAP+HDBSCAN.
- compute_topic_coherence.py
  - c_v, c_npmi ile coherence hesapları; varyant karşılaştırma.
- topic_representatives.py, trim_representatives.py
  - Her topic için temsilci terimler ve kırpma işlemleri.
- keywords_extract.py
  - YAKE/KeyBERT çıkartımı.
- keywords_overlap_analysis.py, keywords_coverage.py
  - Jaccard overlap ve coverage analizleri.
- summarize_keywords*.py, summarize_topics_variants.py
  - Özet tablolar.

KG:
- kg_from_reps_terms.py
  - Representatives md’den co-occurrence graph üretimi (GraphML+stats).
- kg_weighting.py
  - PMI (ln) ve TF‑IDF kenar ağırlıkları + istatistik özetleri (TSV+JSON).
- kg_centrality_analysis.py
  - Merkeziyet (degree/wDeg/eigen/btw), clustering, komponent analizi; summary.md.
- plot_kg.py
  - PNG görselleştirme (top-N edge + largest CC).
- export_kg.py
  - GEXF/GraphML exportları.
- update_weighted_kg_table.py
  - Ağırlıklı KG tablolarını güncelleme yardımcıları.

Sprint/Case/Env/Utilities:
- build_thesis_tables.py
  - Tez tablolarını konsolide eder.
- sprint{1..4}_*.py
  - Sprint bazlı rapor/özet üreticiler.
- case4_speech_vs_text.py
  - CS‑4 analiz scripti.
- mt_pilot_quality.py, mt_pilot_stats.py, mt_translate_opus.py
  - MT pilot kalite/istatistik (CS‑3 metodoloji desteği, deferred).
- export_env.py
  - Env snapshot: env_freeze.txt, versions.json vb.
- fix_stats_floats.py, fix_mojibake.py
  - İstatistikleri normalleştirme ve unicode sorunlarına müdahale.
- inspect_topics.py, peek_jsonl.py, make_bias_from_corpus.py, make_char_confusion.py
  - İnceleme ve yardımcı araçlar.
- ct2_smoketest.py
  - CT2/Faster-Whisper hızlı deneme; CT2 kullanımı yoksa deprecate edilebilir.

## src/mdke/ (kütüphane kodu)
ASR:
- asr/whisper_infer.py
  - HF Whisper inference (beam dump, robust generate) → JSONL + raporlar.
- asr/whisper_infer_ct2.py
  - CT2/Faster‑Whisper pilot.

Text & Data:
- text/{ingest_wikipedia, ingest_zazagorani, transliterate_kmrzza}.py
  - Wiki/Zazagorani ingest ve transliterasyon yardımcıları.
- data/ingest_commonvoice.py
  - CV ingest (Makefile: ingest_cv hedefi).

Utils:
- utils/io.py
  - Paths, ensure_dirs, yaml/jsonl util, logger, seed.
- utils/metrics.py
  - WER/CER, RTF, TR token bias ratio, latin_hawar_ratio.
- utils/langmap.py, utils/textnorm.py
  - Dil kodları normalize ve TR İ/ı vb. normalizasyonlar.

## tests/
- test_asr_beams_schema.py
  - Beam JSONL şeması (alt_hyps, beam_scores, beam_size vb.).
- test_kg_stats_consistency_extended.py, test_pmi_formula_sanity.py
  - KG ağırlık ve istatistik doğrulamaları.
- test_textnorm.py, test_smoke.py
  - Normalizasyon ve temel smoke testleri.

## Etkileşim Haritası (Yüksek Seviye)
- whisper_infer.py → data/interim/asr/*.jsonl (+*_beams.jsonl), reports/asr_*.json
- topics_bertopic.py → reports/topics/* (bertopic topics), *_doc_topics.parquet
- topic_representatives.py → reports/analysis/representatives_*.md
- kg_from_reps_terms.py & kg_weighting.py → reports/analysis/*_kg_*_{pmi,tfidf}.{tsv,json}
- kg_centrality_analysis.py → reports/analysis/centrality/*.json, summary.md
- plot_kg.py → reports/analysis/plots/*.png
- export_kg.py → reports/analysis/exports/*.{gexf,graphml}
- build_thesis_tables.py → reports/analysis/thesis_tables.md

## Notlar
- Raporlar artık sürüm kontrolünde; sadece _trash/_inspect/logs ve büyük zipler ignore.
- Entity linking ve Louvain topluluk analizi v2 iş kalemi.
- MT drift (CS‑3) metodolojik olarak hazır; veri/kalite eşiği sonrası uygulanacak.


# PROJECT_MAP

This document inventories the entire repository: purpose, inputs/outputs, dependencies, and where artefacts live. It’s meant to be the single source of truth for the thesis and for maintaining reproducibility.

## Root

- [Makefile](Makefile): Convenience targets to run pipelines (ASR, topics/keywords, KG analytics, finalization).
- [pyproject.toml](pyproject.toml): Python project metadata and dependencies.
- [README.md](README.md): Project intro, v1 finalization, quickstart, and artifact pointers.
- [sources.json](sources.json): External data sources index (used by ingest scripts where relevant).

## Configs

- [configs/experiment.yaml](configs/experiment.yaml): Paths for raw/interim/processed/reports, language lists, tags used across scripts.
- [configs/prompts/zza_bias.txt](configs/prompts/zza_bias.txt): Optional bias prompt text (Zazaki/Zazagorani).
- Stopwords:
  - [configs/stopwords/kmr.txt](configs/stopwords/kmr.txt)
  - [configs/stopwords/tr.txt](configs/stopwords/tr.txt)
  - [configs/stopwords/zza.txt](configs/stopwords/zza.txt)

## Data

- Raw
  - Common Voice: [data/raw/commonvoice/](data/raw/commonvoice/)
    - `kmr/tr/zza/cv-corpus-22.0-2025-06-20/`
  - Wikipedia dumps: [data/raw/wiki/](data/raw/wiki/)
    - [data/raw/wiki/kmr/kuwiki-latest-pages-articles.xml.bz2](data/raw/wiki/kmr/kuwiki-latest-pages-articles.xml.bz2)
    - [data/raw/wiki/tr/trwiki-latest-pages-articles.xml.bz2](data/raw/wiki/tr/trwiki-latest-pages-articles.xml.bz2)
    - [data/raw/wiki/zza/diqwiki-latest-pages-articles.xml.bz2](data/raw/wiki/zza/diqwiki-latest-pages-articles.xml.bz2)
  - Zazagorani corpus:
    - [data/raw/zazagorani/zza/](data/raw/zazagorani/zza/)
- Interim
  - ASR beams and other intermediates: [data/interim/asr/](data/interim/asr/)
    - e.g., `whisper_tr_validation.jsonl`
- Processed
  - Final corpora and splits:
    - [data/processed/cv_kmr_*.parquet](data/processed/)
    - [data/processed/cv_tr_*.parquet](data/processed/)
    - [data/processed/cv_zza_*.parquet](data/processed/)
    - Text corpora/parquets and sentence tables follow the `text_corpus_{lang}{_tag}.parquet` convention

## Reports

- Analysis:
  - [reports/analysis/final_summary.md](reports/analysis/final_summary.md): V1 summary and pointers.
  - [reports/analysis/updated_project_plan.md](reports/analysis/updated_project_plan.md): Plan with actual tools/outputs.
  - [reports/analysis/keyword_overlap.md](reports/analysis/keyword_overlap.md): Overlap across text/cv/both.
  - [reports/analysis/keyword_coverage.md](reports/analysis/keyword_coverage.md): Coverage stats per variant.
  - [reports/analysis/case*.md](reports/analysis/): Case studies (e.g., case4_speech_vs_text.md).
  - [reports/analysis/centrality/summary.md](reports/analysis/centrality/summary.md): KG centrality summary.
  - KG exports: [reports/analysis/exports/](reports/analysis/exports/) for `.gexf`/`.graphml` files.
- Topics:
  - [reports/topics/](reports/topics/): Topic JSON, doc-topic maps, and docs per variant.
- Keywords:
  - [reports/keywords/](reports/keywords/): Per-language/method/variant keyword JSONs.
- Sprint summaries:
  - [reports/sprint-1-summary.json](reports/sprint-1-summary.json) / [reports/sprint-1-summary.md](reports/sprint-1-summary.md)
  - [reports/sprint-2-summary.json](reports/sprint-2-summary.json) / [reports/sprint-2-summary.md](reports/sprint-2-summary.md)
  - [reports/sprint-3-summary.json](reports/sprint-3-summary.json) / [reports/sprint-3-summary.md](reports/sprint-3-summary.md)
  - [reports/sprint-4-summary.json](reports/sprint-4-summary.json) / [reports/sprint-4-summary.md](reports/sprint-4-summary.md)
  - [reports/sprint-5-summary.json](reports/sprint-5-summary.json) / [reports/sprint-5-summary.md](reports/sprint-5-summary.md) (new)
- Environment:
  - [reports/env_snapshot.json](reports/env_snapshot.json)
  - [reports/env_freeze.txt](reports/env_freeze.txt)
- ASR:
  - [reports/asr_whisper_tr_validation.json](reports/asr_whisper_tr_validation.json)
  - [reports/asr_index.md](reports/asr_index.md) (if present)
- Leakage checks:
  - [reports/leakage_tr.txt](reports/leakage_tr.txt)
  - [reports/leakage_kmr.txt](reports/leakage_kmr.txt)
  - [reports/leakage_zza.txt](reports/leakage_zza.txt)

## Scripts (high level)

ASR
- [scripts/asr_bias_effect.py](scripts/asr_bias_effect.py): Analyze effect of bias prompts (if used).
- [scripts/asr_cleanup.py](scripts/asr_cleanup.py): Post-processing/cleanup for ASR outputs.
- [scripts/asr_collect_summary.py](scripts/asr_collect_summary.py): Gather ASR run summaries.
- [scripts/asr_compare_models.py](scripts/asr_compare_models.py): Compare Whisper variants across metrics.
- [scripts/asr_decode_fusion.py](scripts/asr_decode_fusion.py): Fusion or rescoring experiments.
- [scripts/asr_export_texts.py](scripts/asr_export_texts.py): Export ASR texts for downstream.
- [scripts/asr_inventory.py](scripts/asr_inventory.py): Inventory present ASR outputs.
- [scripts/asr_runtime_summary.py](scripts/asr_runtime_summary.py): Runtime/RTF summaries for ASR.

Text pipeline
- [scripts/text_build_corpus.py](scripts/text_build_corpus.py): Build final text corpus (wiki + Zazagorani).
- [scripts/text_filter_sections.py](scripts/text_filter_sections.py): Remove non-content sections.
- [scripts/text_postfilter_media.py](scripts/text_postfilter_media.py): Remove residual media/template artefacts.
- [scripts/text_sentence_segment.py](scripts/text_sentence_segment.py): Segment into sentences.
- [scripts/text_dedup.py](scripts/text_dedup.py): Exact dedup via normalized hashing.
- [scripts/text_export_samples.py](scripts/text_export_samples.py): Random samples CSV.
- [scripts/text_export_plain.py](scripts/text_export_plain.py): Full export to TXT for reading/QC.
- [scripts/text_ngrams.py](scripts/text_ngrams.py): N-gram frequency lists for QC.
- [scripts/text_report.py](scripts/text_report.py): Markdown QC report per language.

Topics/Keywords
- [scripts/topics_bertopic.py](scripts/topics_bertopic.py): BERTopic fit/export files per variant.
- [scripts/topic_representatives.py](scripts/topic_representatives.py): Representatives and samples.
- [scripts/keywords_extract.py](scripts/keywords_extract.py): Extract keywords (YAKE/KeyBERT).
- [scripts/keywords_overlap_analysis.py](scripts/keywords_overlap_analysis.py): Overlap across variants.
- [scripts/keywords_coverage.py](scripts/keywords_coverage.py): Coverage within docs.

Knowledge Graph
- [scripts/kg_weighting.py](scripts/kg_weighting.py): Weighted KG from representatives (PMI/TF-IDF).
- [scripts/kg_centrality_analysis.py](scripts/kg_centrality_analysis.py): Centrality/clustering metrics + summary.
- [scripts/export_kg.py](scripts/export_kg.py): Export TSV edges to GEXF/GraphML.
- [scripts/kg_from_reps_terms.py](scripts/kg_from_reps_terms.py): Lightweight KG from top terms.
- [scripts/plot_kg.py](scripts/plot_kg.py): Plot/visualize KG subsets.
- [scripts/update_weighted_kg_table.py](scripts/update_weighted_kg_table.py): Update aggregate KG tables.
- [scripts/kg_centrality.py](scripts/kg_centrality.py): Legacy minimal centrality summary (deprecated).

Sprints
- [scripts/sprint1_summarize.py](scripts/sprint1_summarize.py) / [scripts/sprint1_make_markdown.py](scripts/sprint1_make_markdown.py)
- [scripts/sprint2_summarize.py](scripts/sprint2_summarize.py) / [scripts/sprint2_make_markdown.py](scripts/sprint2_make_markdown.py)
- [scripts/sprint3_summarize.py](scripts/sprint3_summarize.py) / [scripts/sprint3_make_markdown.py](scripts/sprint3_make_markdown.py)
- [scripts/sprint4_summarize.py](scripts/sprint4_summarize.py) / [scripts/sprint4_make_markdown.py](scripts/sprint4_make_markdown.py) (+ [scripts/sprint4_append_finals_to_md.py](scripts/sprint4_append_finals_to_md.py))
- [scripts/sprint5_summarize.py](scripts/sprint5_summarize.py) / [scripts/sprint5_make_markdown.py](scripts/sprint5_make_markdown.py) (new)

Cases/MT/Pilots
- [scripts/mt_translate_opus.py](scripts/mt_translate_opus.py): OPUS MT usage for pilots.
- [scripts/mt_pilot_stats.py](scripts/mt_pilot_stats.py): MT pilot corpus stats.
- [scripts/mt_pilot_quality.py](scripts/mt_pilot_quality.py): Quality analysis for MT pilot.
- [scripts/case4_speech_vs_text.py](scripts/case4_speech_vs_text.py): Case study comparing speech vs text.

Utilities
- [scripts/fix_mojibake.py](scripts/fix_mojibake.py): Fix mojibake.
- [scripts/fix_stats_floats.py](scripts/fix_stats_floats.py): Clamp min/avg/max for numeric stability.
- [scripts/export_env.py](scripts/export_env.py): Environment snapshot + freeze.
- [scripts/inspect_topics.py](scripts/inspect_topics.py): Quick view of topics.
- [scripts/peek_jsonl.py](scripts/peek_jsonl.py): Pretty-print a few JSONL rows.
- [scripts/make_bias_from_corpus.py](scripts/make_bias_from_corpus.py): Build bias prompt from corpus.
- [scripts/make_char_confusion.py](scripts/make_char_confusion.py): Character confusion counts.
- [scripts/materialize_final_aliases.py](scripts/materialize_final_aliases.py): Copy/alias final artefacts.
- Legacy: [scripts/ct2_smoketest.py](scripts/ct2_smoketest.py) (deprecated if CT2 unused), [scripts/trim_reps.py](scripts/trim_reps.py) (superseded by trim_representatives.py)

## Python package

- [src/mdke/__init__.py](src/mdke/__init__.py)
- ASR:
  - [src/mdke/asr/whisper_infer.py](src/mdke/asr/whisper_infer.py): Whisper inference (HF), beams JSONL dump, dynamic input length, forced_decoder_ids on generation_config, attention_mask omitted.
  - [src/mdke/asr/whisper_infer_ct2.py](src/mdke/asr/whisper_infer_ct2.py): CT2/Faster-Whisper path (legacy if unused).
- Data:
  - [src/mdke/data/ingest_commonvoice.py](src/mdke/data/ingest_commonvoice.py): Common Voice ingestion and splits.
- Utils:
  - [src/mdke/utils/io.py](src/mdke/utils/io.py): Paths dataclass, load/save YAML/JSON(L), logger, seeding, dir ensure.
  - [src/mdke/utils/metrics.py](src/mdke/utils/metrics.py): WER/CER and helper metrics; latin_hawar_ratio.
  - [src/mdke/utils/langmap.py](src/mdke/utils/langmap.py): Language code mappings.
  - [src/mdke/utils/textnorm.py](src/mdke/utils/textnorm.py): NFKC + TR İ/ı normalization, cleanup regexes.

## Pipelines and artefact flow (short)

- ASR (CV → JSONL/JSON reports)
  - Inference → beams → metrics (WER/CER/RTF) → sprint summaries and ASR index
- Text (Wiki+Zazagorani → cleaned corpus)
  - Ingest → filter sections → postfilter media → sentence segment → dedup → QC report/samples/ngrams
- Topics/Keywords
  - BERTopic → representatives (md) → keywords (yake/keybert) → overlap/coverage analysis
- Knowledge Graph
  - Representatives → weighted KGs (PMI/TF-IDF) → centrality/plots/exports (GEXF/GraphML)
- Sprints
  - Sprint 1–4 summaries and MD generators; Sprint 5 generic aggregator added
- Finalization
  - Materialize final aliases, export environment, thesis tables builder

## Reproducibility

- Environment snapshots at reports/env_snapshot.json + reports/env_freeze.txt
- Commit hash in thesis tables (when available)
- All reports tracked in Git (ignore rules updated to keep them)



# PROJECT_MAP — MultidialectalKnowledgeExtraction (v1, 2025-09-18)

Bu doküman, depo yapısını “hangi dosya/klasör ne işe yarar, ne üretir, neye bağlıdır” ekseninde listeler. Amaç: tekrarlanabilirlik, izlenebilirlik ve bakım kolaylığı.

## Kök (Root)

- `Makefile`: ASR, topic/keyword, KG analiz/çizim/export ve finalizasyon kısayolları.
- `pyproject.toml`: Python proje metası ve bağımlılıklar.
- `README.md`: Amaçlar, v1 finalizasyon, sonuçlar, quickstart ve artefakt bağlantıları.
- `sources.json`: Ham veri kaynakları (Wiki, CV vb.).

## Konfigürasyon

- `configs/experiment.yaml`: `paths.raw/interim/processed/reports` ve dil listeleri; pipeline etiketleri.
- `configs/prompts/zza_bias.txt`: (Opsiyonel) Zazaki/Zazagorani bias prompt metni.
- Stopwords:
  - `configs/stopwords/tr.txt`
  - `configs/stopwords/kmr.txt`
  - `configs/stopwords/zza.txt`

## Veri

- `data/raw/`
  - `commonvoice/{tr,kmr,zza}/cv-corpus-22.0-2025-06-20/`
  - `wiki/{tr,kmr,zza}/*latest-pages-articles.xml.bz2`
  - `zazagorani/zza/*.txt`
- `data/interim/`
  - `asr/*` — ör. `whisper_tr_validation.jsonl`, beam/ara çıktılar
- `data/processed/`
  - `cv_{lang}_{split}.parquet`
  - `text_corpus_{lang}{_tag}.{parquet|csv}`
  - `text_sentences_{lang}{_tag}.parquet` (varsa)

## Raporlar

- Analiz:
  - `reports/analysis/final_summary.md`
  - `reports/analysis/keyword_overlap.md`
  - `reports/analysis/keyword_coverage.md`
  - `reports/analysis/centrality/summary.md`
  - KG exportları: `reports/analysis/exports/*.{gexf,graphml}`
  - KG çizimleri (varsa): `reports/analysis/plots/*.png`
  - Vaka çalışmaları: `reports/analysis/case*.md`
- Topics:
  - `reports/topics/{lang}_bertopic_topics.json`
  - `reports/topics/{lang}_bertopic_doc_topics_{variant}.parquet`
  - `reports/topics/{lang}_bertopic_docs_{variant}.txt` (text/cv/both)
- Keywords:
  - `reports/keywords/{lang}_{method}_{variant}.json` (YAKE/KeyBERT)
- Sprint özetleri:
  - `reports/sprint-1-summary.{json,md}`
  - `reports/sprint-2-summary.{json,md}`
  - `reports/sprint-3-summary.{json,md}`
  - `reports/sprint-4-summary.{json,md}`
  - `reports/sprint-5-summary.{json,md}` (yeni)
  - (İsteğe bağlı) `reports/sprint-6-summary.{json,md}` — aşağıdaki yeni scriptlerle
- Ortam:
  - `reports/env_snapshot.json`, `reports/env_freeze.txt`
- ASR ve sızıntı:
  - `reports/asr_whisper_tr_validation.json`, `reports/asr_index.md` (varsa)
  - `reports/leakage_{tr,kmr,zza}.txt`

## Scriptler (ana işlev grupları)

ASR
- `scripts/asr_compare_models.py`: Whisper varyant kıyas (WER/CER/RTF).
- `scripts/asr_decode_fusion.py`: Beam JSONL üzerinden rescoring/fusion pilotları.
- `scripts/asr_inventory.py`, `scripts/asr_cleanup.py`, `scripts/asr_export_texts.py`: envanter/temizlik/dışa aktarım.
- `scripts/asr_runtime_summary.py`, `scripts/asr_collect_summary.py`, `scripts/asr_bias_effect.py`: runtime ve bias analizleri (opsiyonel).

Metin boru hattı
- `scripts/text_build_corpus.py`: Wiki+Zazagorani birleşik metin korpusu.
- `scripts/text_filter_sections.py`: navigasyon/kaynakça vb. bölüm temizleme.
- `scripts/text_postfilter_media.py`: şablon/medya artığı temizleme.
- `scripts/text_sentence_segment.py`: regex tabanlı cümle segmentasyonu.
- `scripts/text_dedup.py`: normalize hash ile exact dedup.
- `scripts/text_export_samples.py`: rastgele örnek CSV.
- `scripts/text_export_plain.py`: TXT dışa aktarım.
- `scripts/text_ngrams.py`: n‑gram sıklıkları.
- `scripts/text_report.py`: metin QC markdown.

Topics & Keywords
- `scripts/topics_bertopic.py`: BERTopic fit/export (UMAP+HDBSCAN).
- `scripts/topic_representatives.py`: temsilci terimler ve örnek cümleler.
- `scripts/keywords_extract.py`: YAKE/KeyBERT çıkarımı.
- `scripts/keywords_overlap_analysis.py`: text/cv/both Jaccard kesişim.
- `scripts/keywords_coverage.py`: anahtar sözcük kapsaması.

KG
- `scripts/kg_weighting.py`: representatives → ağırlıklı KG (PMI ln / TF‑IDF) + TSV/JSON.
- `scripts/kg_centrality_analysis.py`: derece/ağırlıklı derece/eigen/betweenness (sampling)/clustering + summary.md.
- `scripts/export_kg.py`: TSV → GEXF/GraphML export.
- `scripts/kg_from_reps_terms.py`: top terimlerden basit KG (GraphML+stats).
- `scripts/plot_kg.py`: görselleştirme.
- `scripts/update_weighted_kg_table.py`: ağırlıklı KG tablo güncellemeleri.
- `scripts/kg_centrality.py`: (Deprecated) minimal özet.

Sprint/Case/Env/Util
- `scripts/build_thesis_tables.py`: tez tablolarını birleştirir.
- `scripts/sprint{1..4}_*.py`: sprint bazlı özet/markdown.
- `scripts/sprint5_summarize.py`, `scripts/sprint5_make_markdown.py`: Sprint‑5 özet/MD.
- (Opsiyonel yeni) `scripts/sprint6_summarize.py`, `scripts/sprint6_make_markdown.py`: Sprint‑6 dokümantasyon ve paketleme özeti.
- `scripts/case4_speech_vs_text.py`: Konuşma vs Metin karşılaştırma case.
- `scripts/mt_pilot_stats.py`, `scripts/mt_pilot_quality.py`, `scripts/mt_translate_opus.py`: MT pilot destekleri.
- `scripts/export_env.py`: ortam anlık görüntüsü.
- `scripts/fix_stats_floats.py`: min/avg/max clamp düzeltmesi.
- `scripts/fix_mojibake.py`: Unicode/mojibake düzeltmeleri.
- `scripts/inspect_topics.py`, `scripts/peek_jsonl.py`, `scripts/make_bias_from_corpus.py`, `scripts/make_char_confusion.py`: yardımcılar.
- `scripts/ct2_smoketest.py`: CT2 denemesi (kullanılmıyorsa deprecated).

## Python paket kodu

- `src/mdke/asr/whisper_infer.py`: HF Whisper inference; beam dump JSONL; dynamic input length; `forced_decoder_ids` generation_config’ta; attention_mask yok.
- `src/mdke/asr/whisper_infer_ct2.py`: CT2/Faster‑Whisper (legacy).
- `src/mdke/data/ingest_commonvoice.py`: Common Voice ingest.
- `src/mdke/utils/io.py`: Paths, yaml/json(l), logger, seed, ensure_dirs.
- `src/mdke/utils/metrics.py`: WER/CER, latin_hawar_ratio vb.
- `src/mdke/utils/langmap.py`: dil kodları eşlemeleri.
- `src/mdke/utils/textnorm.py`: NFKC + TR İ/ı normalizasyonları.

## Akış (özet)

- ASR → JSONL/JSON raporlar → sprint özetleri
- Metin → temizleme/segment/dedup → QC raporları/samples/ngrams
- Topics → representatives → Keywords (YAKE/KeyBERT) → overlap/coverage
- Representatives → Weighted KG (PMI/TF‑IDF) → centrality/plots/exports
- Final → thesis tables + env snapshot + PROJECT_MAP

## Tekrarlanabilirlik

- Env snapshot: `reports/env_snapshot.json`, `reports/env_freeze.txt`
- Tüm raporlar Git’te izlenir (sadece `_trash`, `_inspect`, `logs`, `*.zip` ignore).

## KG Bundle

- [reports/analysis/kg_bundle_v1.zip](reports/analysis/kg_bundle_v1.zip): Tüm KG artefaktları (TSV, GEXF, GraphML, PNG, centrality JSON/MD).

## Sprint-6 Summary

- [reports/sprint-6-summary.md](reports/sprint-6-summary.md): Kapanış, docstring coverage, deprecated scriptler, env snapshot.

## Future Work / Vitrin

- CS-3 mini pilot, LDA baseline, NER+Wikidata+Louvain/Leiden (v2 için öneri).