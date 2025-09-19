# ASR Results — Common Voice v22 (TR/KMR/ZZA) — Medium vs Large-v2

Bu paket, TR (Turkish), KMR (Kurmanji), ZZA (Zazaki) için Whisper tabanlı ASR deneylerinin nihai karşılaştırmalarını ve tekrarlanabilirlik artefaktlarını içerir.

## İçerik
- JSON raporlar (12 adet):
  - asr_whisper_{kmr,tr,zza}_{validation,test}_{medium,large}.json
- Tablolar:
  - asr_compare_medium_large.md  (geniş tablo + deltalar)
  - asr_best_medium_large.md     (kısa özet tablo)
- Tekrarlanabilirlik:
  - env.txt          (pip freeze)
  - versions.json    (Python/OS/torch/transformers/jiwer/CUDA/GPU)
  - git_commit.txt   (repo commit kimliği)
  - gpu.txt          (Windows GPU adı) [opsiyonel]
- Konfig/Kod:
  - configs/experiment.yaml, configs/experiment_large.yaml
  - src/mdke/asr/whisper_infer.py
  - scripts/asr_compare_models.py

## Nihai model seçimi ve ayarlar
- KMR → openai/whisper-large-v2
- ZZA → openai/whisper-large-v2
- TR  → openai/whisper-medium
- Ortak ayarlar: bias=OFF; beam_size=1; min_new_tokens=12; max_new_tokens=160
- Dil zorlama: TR forced lang=tr; KMR/ZZA auto (transcribe-only)

## Neden böyle?
- KMR/ZZA: large-v2, WER/CER’i ~%30–38 düşürüyor; RTF’deki değişim kabul edilebilir.
- TR: large-v2 WER’de küçük kazanım sağlasa da CER (+%20–29) ve RTF (+%52–84) kötüleşiyor → medium daha dengeli.

## Nasıl üretildi? (özet)
- Çıkarım: src/mdke/asr/whisper_infer.py (bias=OFF; TR forced; KMR/ZZA auto; beam=1; min/max_new sabit)
- Karşılaştırma: scripts/asr_compare_models.py (baseline=medium; ΔRTF% hesaplanır)
- Ölçüm: WER/CER jiwer ile; önce lowercase + noktalama temizliği (src/mdke/utils/metrics.py). RTF = wall_s / total_audio_s.

## Yeniden çalıştırma (PowerShell örneği)
python scripts\asr_compare_models.py --patterns "reports/asr_whisper_*_*_medium.json" "reports/asr_whisper_*_*_large.json" --baseline medium --out "reports/asr_compare_medium_large.md" --best-out "reports/asr_best_medium_large.md"

## Notlar
- “Small” sadece 512 örnekli pilot olarak koşuldu ve WER/CER çok yüksekti; final kararlar medium/large tam validation+test raporlarına dayandırıldı.

## Thesis Consolidation

Ana bulgular `reports/analysis/thesis_tables.md` içinde konsolide:
- Topic Coherence: Çok-kaynak (text vs cv vs both) varyantları; lehçe/dil bazında kalite / outlier dengesi.
- Keyword Overlap & Coverage: Düşük J(text,cv) + yüksek cv coverage → kaynak tamamlayıcılığı.
- Representatives: TR/KMR/ZZA both top15 nitel doğrulama.
- Case Studies:
  - CS-1 (Tema, Çok-Dilli, CV): Ortak temalar + lehçe farklılığı.
  - CS-2 (Aynı Konu, Çok Konuşmacı): Çekirdek kavram sabit; çevresel kültürel halo.
  - CS-3 (Orijinal vs MT): Deferred (metodoloji dokümante).
  - CS-4 (Speech vs Text): Speech ek kaynağı terminolojik çeşitlilik artırıyor.
- Knowledge Graph: Mini (top15) vs Full — hub gelişimi (ZZA max degree 56), density düşüşü, zengin topoloji.
- Execution Summary: Sprint, test case, ablation, risk izlenebilirliği.

Future work ve reproducibility komutları: `reports/analysis/future_work.md`

Hızlı Repro (örnek):
```powershell
conda activate mdke
python scripts/topics_bertopic.py --lang tr --sources text,cv --cv-weight 0.5
python scripts/keywords_extract.py --lang tr --sources text,cv,both --topk 200
python scripts/compute_topic_coherence.py --langs tr,kmr,zza --variants text,cv,both --topn 10
python scripts/topic_representatives.py --lang tr --variant both --topk_docs 2
python scripts/kg_from_reps_terms.py --langs tr,kmr,zza --mode top15 --top_terms 5
python scripts/kg_from_reps_terms.py --langs tr,kmr,zza --mode full --top_terms 5 --summary_md reports/analysis/kg_examples_full.md
```

Deferred:
- Shallow Fusion (TC-3)
- MT Drift (CS-3)
- Entity Linking + PMI / TF-IDF edge weighting
- Bipartite Topic–Term KG


## v1 Finalization — Artifacts & Quickstart

Artifacts (özet):
- ASR reports: `reports/asr_whisper_*`
- Compare tables: `reports/asr_compare_medium_large.md`, `reports/asr_best_medium_large.md`
- Topics/Keywords: `reports/topics/*`, `reports/keywords/*`, analysis md’leri
- KG (PMI/TF‑IDF): `reports/analysis/*_kg_*_{pmi,tfidf}.{tsv,json}`, centrality, plots, exports (.gexf/.graphml)
- Case studies: `reports/analysis/case*.md`
- Final summary: `reports/analysis/final_summary.md`
- Repro bundle: `reports/env.txt`, `env_freeze.txt`, `versions.json`, `git_commit.txt`, `gpu.txt`

v1 Quickstart (PowerShell):
```powershell
# ASR model karşılaştırma tablolarını yeniden üret
python scripts\asr_compare_models.py --patterns "reports/asr_whisper_*_*_medium.json" "reports/asr_whisper_*_*_large.json" --baseline medium --out "reports/asr_compare_medium_large.md" --best-out "reports/asr_best_medium_large.md"

# KG centrality özetleri
python scripts\kg_centrality_analysis.py --patterns "reports/analysis/*_kg_full_*.tsv" "reports/analysis/*_kg_top15_*.tsv"

# KG çizimler (örnek)
python scripts\plot_kg.py --tsv reports\analysis\tr_kg_full_pmi.tsv --top_edges 200 --out reports\analysis\plots\tr_kg_full_pmi_top200.png

# KG export (örnek)
python scripts\export_kg.py --tsv reports\analysis\tr_kg_full_pmi.tsv --out reports\analysis\exports\tr_kg_full_pmi.gexf

# Testler
pytest -q
```

Thesis title (öneri):
- TR: “Konuşmadan Bilgi Grafına: Türkçe, Kurmanci ve Zazaca İçin Çok‑Lehçeli Bilgi Çıkarımı”
- EN: “From Speech to Knowledge Graphs: Multidialectal Knowledge Extraction for Turkish, Kurmanji, and Zazaki”


## Project Map

Bu bölüm depodaki her dosyanın amacını ve etkilediği çıktıları özetler. Ayrıntılı sürüm: `reports/docs/PROJECT_MAP.md`.

- configs/
  - experiment.yaml, experiment_large.yaml: ASR/işlem konfigleri; `src/mdke/asr/whisper_infer.py`, `scripts/*` tarafından okunur.
  - prompts/, stopwords/: ASR bias metni ve dil-dışı ölçüm listeleri; `whisper_infer.py` metrikleri etkiler.
- data/
  - raw/: Ham kaynaklar (CV, wiki, Zazagorani) [Git dışı].
  - interim/: Ara çıktılar (ASR JSONL, beam JSONL) [Git dışı].
  - processed/: Temizlenmiş/parçalanmış/dedup korpuslar (parquet); topics/keywords girişleri.
- reports/
  - asr_*.json, *_summary.md: ASR metrikleri ve karşılaştırmalar.
  - analysis/: KG TSV+stats, centrality JSON+summary, plots PNG, exports (GEXF/GraphML), case studies.
  - topics/, keywords/: BERTopic ve keyword çıktıları.
  - sprint-*-summary.{json,md}: sprint raporları.
  - env.txt, env_freeze.txt, versions.json, git_commit.txt, gpu.txt: tekrarlanabilirlik.
- scripts/
  - asr_compare_models.py: medium vs large kıyası; `reports/asr_compare_medium_large.md` üretir.
  - asr_decode_fusion.py: beam dump yeniden puanlama (pilot); `reports/exports/fusion_*.md`.
  - topics_bertopic.py, compute_topic_coherence.py: topic model ve coherence.
  - keywords_extract.py, keywords_*: anahtar terimler + coverage/overlap.
  - topic_representatives.py: temsilci terimler; KG girişleri.
  - kg_from_reps_terms.py, kg_weighting.py: co-occurrence + PMI/TF‑IDF ağırlıkları, TSV+stats.
  - kg_centrality_analysis.py: centrality ve `analysis/centrality/summary.md`.
  - plot_kg.py: PNG görselleri.
  - export_kg.py: GEXF/GraphML exportları.
  - text_*: ingest, temizlik, segment, dedup, n‑gram.
  - build_thesis_tables.py: konsolidasyon tabloları.
- src/mdke/
  - asr/whisper_infer.py: ASR inference (beam dump destekli); rapor+JSONL üretir.
  - asr/whisper_infer_ct2.py: CT2/Faster‑Whisper pilot.
  - utils/{io,metrics,langmap,textnorm}.py: IO, metrikler (WER/CER/RTF/bias), dil/simge, normalizasyon.
  - data/ingest_commonvoice.py: CV ingest.
  - text/*: wiki/zazagorani ingest ve transliterasyon yardımcıları.
- tests/
  - test_asr_beams_schema.py: beam JSONL şema kontrolü.
  - test_kg_stats_consistency_extended.py, test_pmi_formula_sanity.py: KG ağırlık ve istatistik doğrulamaları.
  - test_textnorm.py, test_smoke.py: metin norm ve basit duman testi.

## Code comments & style

Kodlar progressive olarak docstring + inline yorumlarla güncellenmektedir. Örnek bir iyileştirme: `scripts/export_kg.py` dosyası (aşağıda önerilen sürüm).


## Knowledge Graph artefacts

| Dil | Set   | Ağırlık | Edges TSV | Export | Plot | Stats JSON |
|-----|-------|---------|-----------|--------|------|------------|
| TR  | full  | PMI     | reports/analysis/tr_kg_full_pmi.tsv | reports/analysis/exports/tr_kg_full_pmi.gexf | reports/analysis/plots/tr_kg_full_pmi.png | reports/analysis/tr_kg_full_pmi_stats.json |
| KMR | full  | PMI     | reports/analysis/kmr_kg_full_pmi.tsv | reports/analysis/exports/kmr_kg_full_pmi.gexf | reports/analysis/plots/kmr_kg_full_pmi.png | reports/analysis/kmr_kg_full_pmi_stats.json |
| ZZA | full  | PMI     | reports/analysis/zza_kg_full_pmi.tsv | reports/analysis/exports/zza_kg_full_pmi.gexf | reports/analysis/plots/zza_kg_full_pmi.png | reports/analysis/zza_kg_full_pmi_stats.json |
| TR  | top15 | TF-IDF  | reports/analysis/tr_kg_top15_tfidf.tsv | reports/analysis/exports/tr_kg_top15_tfidf.graphml | reports/analysis/plots/tr_kg_top15_tfidf.png | reports/analysis/tr_kg_top15_tfidf_stats.json |
| KMR | top15 | TF-IDF  | reports/analysis/kmr_kg_top15_tfidf.tsv | reports/analysis/exports/kmr_kg_top15_tfidf.graphml | reports/analysis/plots/kmr_kg_top15_tfidf.png | reports/analysis/kmr_kg_top15_tfidf_stats.json |
| ZZA | top15 | TF-IDF  | reports/analysis/zza_kg_top15_tfidf.tsv | reports/analysis/exports/zza_kg_top15_tfidf.graphml | reports/analysis/plots/zza_kg_top15_tfidf.png | reports/analysis/zza_kg_top15_tfidf_stats.json |

**KG bundle:** [reports/analysis/kg_bundle_v1.zip](reports/analysis/kg_bundle_v1.zip)

## Project Map & Sprint Summaries

- [PROJECT_MAP.md](reports/docs/PROJECT_MAP.md): Tüm dosya/fonksiyon/artefakt haritası.
- [Thesis Tables](reports/analysis/thesis_tables.md): Konsolide bulgular.
- [Sprint-6 Summary](reports/sprint-6-summary.md): Kapanış ve dokümantasyon durumu.

## How to reproduce (v1)

- KG pipeline: `scripts/kg_weighting.py` → `scripts/export_kg.py` → `scripts/plot_kg.py` → `scripts/kg_centrality_analysis.py`
- KG bundle: [reports/analysis/kg_bundle_v1.zip](reports/analysis/kg_bundle_v1.zip)
- Project map: [reports/docs/PROJECT_MAP.md](reports/docs/PROJECT_MAP.md)
- Sprint-6 summary: [reports/sprint-6-summary.md](reports/sprint-6-summary.md)
- Thesis tables: [reports/analysis/thesis_tables.md](reports/analysis/thesis_tables.md)

## Appendix / Deferred Work

Aşağıdaki adımlar opsiyonel olup v1’de uygulanmamıştır, future work olarak bırakılmıştır:

- CS-3 mini pilot (Deferred, not implemented)
- LDA baseline (Deferred, not implemented)
- NER+Wikidata+Louvain (Deferred, not implemented)

KG bundle arşivi için: [reports/analysis/kg_bundle_v1.zip](reports/analysis/kg_bundle_v1.zip) dosyasına bakınız.

## Appendix — Data Sources & Licensing

- **Mozilla Common Voice v22.0 (TR, KMR, ZZA)** — License: **CC0**  
  Citation: Ardila et al., 2020, Mozilla Common Voice.  
  URL: https://commonvoice.mozilla.org  
  Accessed: 2025-09-19

- **Wikipedia dumps** — Projects: **trwiki (TR)**, **kuwiki (KMR)**, **diqwiki (ZZA)** — License: **CC BY-SA 4.0**  
  Provider: Wikimedia Foundation Dumps  
  URL: https://dumps.wikimedia.org  
  Dump date(s): *fill if you logged exact dump date(s)*  
  Accessed: 2025-09-19

- **Zazagorani (Zazaki) corpus** — License: **VarDial research license**  
  Citation: Öztürk Başaran et al., 2020, Zazagorani (Zazaki) corpus.  
  URL: *project/corpus page if available*  
  Accessed: 2025-09-19

**Ethics & Compliance.** Bu projede kişisel veri toplanmamıştır. Tüm veri kullanımları ilgili lisans koşullarına uygundur (CC0 / CC BY-SA / VarDial). Toplanan ve paylaşılan türetilmiş çıktılar (raporlar, grafikler) lisans koşullarına saygı gösterir ve kaynak atıfları sağlanmıştır.

**Provenance.** Ham kaynak tanımları ve yolları için `sources.json` dosyasına bakınız (versiyonlar, dump adları, yerel dosya yolları).
 
