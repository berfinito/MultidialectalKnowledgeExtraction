# Project Execution Summary

Bu belge sprint bazlı ilerlemeyi, test case (TC) kapsamını, ablation setlerini, case study durumunu ve ileri iş kalemlerini izlenebilir biçimde özetler.

## 1. Sprint Templatı ve Gerçekleşenler

| Sprint | Odak | Ana Çıktılar | İlgili Artefaktlar |
|--------|------|--------------|--------------------|
| S1 | ASR Baseline | Whisper (medium/large) valid/test WER/CER, bias & beam aramaları | reports/asr_*.json, asr_summary_*.md |
| S2 | Cross-Dialect & Model Seçimi | ZZA/KMR dil zorluk analizi, bias etkisi, decode varyantları | confusion_*.json, asr_compare_* |
| S3 | Text Ingest & N-gram | Wiki + Zazagorani çekme, temizleme, n-gram istatistikleri | reports/text_stats/* |
| S4 | Normalization & Final Corpora | Unicode NFKC, lowercase, segmentasyon, deduplikasyon | data/processed/*.parquet, scripts/utils |
| S5 | Topic & Keywords + Ablations + Case Studies + Mini KG | BERTopic varyantları, KeyBERT/YAKE, coherence/overlap/coverage, reps, KG, case1/2/4 | reports/analysis/*.md |

## 2. Core Test Cases

| TC | Tanım | Durum | Kanıt / Dosyalar |
|----|------|-------|------------------|
| TC-1 | Çok-dilli ASR değerlendirme (WER/CER/RTF) | Tamamlandı | asr_*summary*.md, confusion_*.json |
| TC-2 | Cross-dialect decoding etkisi | Tamamlandı | confusion_*_TRdecode.json, bias varyantları |
| TC-3 | ASR + LM Fusion (shallow) | Deferred | future_work.md (Fusion bölümü) |
| TC-4 | Topic & Keyword Extraction (çok-kaynak) | Tamamlandı | topic_coherence.md, keyword_overlap.md, keyword_coverage.md |

## 3. Ablations ve Analizler

| Ablation | Amaç | Metod / Metrik | Çıktı |
|----------|------|----------------|-------|
| Topic Coherence | Varyant kalite karşılaştırma | c_npmi, c_v, outlier% | topic_coherence.md |
| Keyword Overlap | Kaynak tamamlayıcılık | Jaccard, new_in_both% | keyword_overlap.md |
| Keyword Coverage | Terim doküman içi kapsama | covered%, avg_doc_coverage | keyword_coverage.md |
| Representatives (Interpretability) | Nitel doğrulama | Top terimler + örnek cümle | representatives_*_both_top15.md |
| Mini KG | Kavramsal köprü yoğunluğu | Co-occurrence graph stats | kg_examples_all.md |
| (Opsiyonel) Full KG | Tüm topic’lerle geniş grafik | density/degree dağılım | (henüz yok → future_work.md) |

## 4. Case Studies

| Case | Başlık | Durum | Dosya |
|------|--------|-------|-------|
| CS-1 | Aynı Tema, Çok-Dilli (CV) | Tamamlandı | case1_same_theme_multi_dialect.md |
| CS-2 | Aynı Konu, Çok Konuşmacı (Text) | Tamamlandı | case2_same_topic_multi_speakers.md |
| CS-3 | Orijinal vs MT | Deferred | case3_original_vs_mt.md |
| CS-4 | Speech (CV) vs Text | Tamamlandı | case4_speech_vs_text.md |

## 5. Repro / İzlenebilirlik Referansları

- Ortam: `env.txt`, `env_freeze.txt`, `versions.json`, `git_commit.txt`
- Komut Özetleri: future_work.md (Repro bölümü)
- Veri Kaynakları: `data/raw/commonvoice/*`, `data/raw/wiki/*`, `data/raw/zazagorani/*`
- Üretilmiş Tablolar: `thesis_tables.md` (konsolidasyon)

## 6. Riskler ve Sınırlar

| Alan | Risk | Etki | Karşılık |
|------|------|------|----------|
| MT Kalitesi (CS-3) | Düşük ZZA çeviri kalitesi | Yanıltıcı drift ölçümleri | Pilot + kalite eşiği (ChrF>40) |
| Fusion Gecikmesi | LM eğitimi zaman maliyeti | WER iyileştirmesi kaçırıldı | Gelecek sprint planı |
| Entity Linking | Çok-dilli ad varyantları | KG bağlamsal zayıflık | Wikidata tabanlı eşleme planlandı |
| Full KG Boyutu | Hafıza & karmaşıklık | Yürütme süresi artışı | top15 ön-filtre → sonra full deney |

## 7. Future Work (Özet)

- Shallow Fusion (KenLM 3/5-gram, λ grid)
- Full-topic + bipartite KG
- Entity Linking (Wikidata Q-ID eşleşme)
- Edge PMI / TF-IDF ağırlıkları
- MT vs Original Topic/Keyword Drift (CS-3 tam uygulama)
- ASR fine-tuning (lehçe uyarlama)
- Gelişmiş deduplikasyon (LSH + fuzzy hashing)

## 8. Kapanış

Çok-kaynaklı (text + CV) yaklaşım; overlap (düşük Jaccard) ve coverage (yüksek cv kapsamı) metrikleriyle tamamlayıcılığı gösterdi; mini KG köprü terim yoğunluğu dil/lehçe farklarını nicelleştirdi; deferred alanlar future_work.md’de metodoloji ile kayıt altına alındı.