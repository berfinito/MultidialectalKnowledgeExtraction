# Future Work

## 1. ASR + Text LM Fusion (TC-3)
Shallow fusion uygulanmadı. Plan:
- Korpus: Wiki + Zazagorani (her dil) birleşik.
- KenLM: 3-gram & 5-gram.
- Skor: log P_ASR + λ * log P_LM, λ ∈ {0.2,0.4,0.6,0.8,1.0}.
- Hedef: KMR & ZZA WER %5–8 düşüş.
- Ek Analiz: “latin_hawar_ratio” ve diakritik hata azalışı.

## 2. Knowledge Graph Genişletme
Mevcut:
- Mini KG (top15) → yoğun çekirdek.
- Full KG (tüm reps) → hub profili (ZZA max degree 56).

Sorun / Gözlem:
- Edge ağırlıkları ≈1 → hiçbir çift çoklu topic’te sık tekrar etmiyor (ilk 5 terim kısıtı).
- Density düşük → seyrek doğal; yapısal zenginlik hub derecesinde.

Planlı Adımlar:
1. Top10/Top15 term varyantı (tekrar artışı ölçümü).
2. Bipartite Topic–Term graf (community / modularity).
3. Entity Linking (Wikidata Q-ID) hedef precision ≥%80 örneklem.
4. PMI, LLR, TF-IDF edge weighting + düşük ağırlık filtresi.
5. Kaynak katmanı: Speech vs Text alt-graf karşılaştırmalı hub persistansı.
6. Domain segmentasyonu (wiki / cv / zazagorani katmanları).
7. Bridge kavram tespiti: Betweenness & eigenvector centrality farklılık analizi.

## 3. Deferred Case Study (CS-3 MT vs Original)
- Risk: ZZA MT kalite belirsiz; drift ölçümü gürültülü olabilir.
- Pilot: 2K doküman, ChrF > 40 eşiği (ya da manuel 50 cümle değerlendirmesi).
- Metrikler: Topic term set Jaccard, top-10 Spearman ρ, KeyBERT overlap, MultiWord% delta, KG hub derece korelasyonu.
- Hedef: “Homojenleşme” etkisini nicelleştirmek.

## 4. Ek Araştırma Olanakları
- ASR Fine-tuning (lehçe adaptasyonu).
- Adaptif deduplikasyon: MinHash / LSH + fuzzy hashing (simhash).
- Entity-level KG: EL + canonical ad kümesi; cross-dialect alias eşleştirme.
- Temporal / evrim (veri elde edilirse).
- Distillation: Çok-kaynaklı (text+speech) embedding uyumlama.

## 5. Repro Komut Hızlı Özet

```bash
# Topic model (ör: TR both)
python scripts/topics_bertopic.py --lang tr --sources text,cv --cv-weight 0.5
# Keywords (KeyBERT + YAKE)
python scripts/keywords_extract.py --lang tr --sources text,cv,both --topk 200
# Coherence
python scripts/compute_topic_coherence.py --langs tr,kmr,zza --variants text,cv,both --topn 10
# Keyword overlap & coverage
python scripts/keywords_overlap_analysis.py
python scripts/keywords_coverage.py
# Representatives
python scripts/topic_representatives.py --lang tr --variant both --topk_docs 2
# Mini KG
python scripts/kg_from_reps_terms.py --langs tr,kmr,zza --mode top15 --top_terms 5
# Full KG
python scripts/kg_from_reps_terms.py --langs tr,kmr,zza --mode full --top_terms 5 --summary_md reports/analysis/kg_examples_full.md
# Konsolidasyon (full dahil)
python scripts/build_thesis_tables.py --include "topic_coherence.md,keyword_overlap.md,keyword_coverage.md,representatives_tr_both_top15.md,representatives_kmr_both_top15.md,representatives_zza_both_top15.md,case4_speech_vs_text.md,case1_same_theme_multi_dialect.md,case2_same_topic_multi_speakers.md,case3_original_vs_mt.md,kg_examples_all.md,kg_examples_full.md,kg_interpretation.md,project_execution_summary.md"
```

## 6. Artefakt İndeksi
| Tür | Dosya(lar) |
|-----|-----------|
| Ortam | env.txt, env_freeze.txt, versions.json, git_commit.txt |
| Konsolide | thesis_tables.md |
| KG | kg_examples_all.md, kg_examples_full.md, kg_interpretation.md |
| Yürütme Özeti | project_execution_summary.md |
| Deferred Metodoloji | case3_original_vs_mt.md |
| Gelecek Plan | future_work.md |

## 7. Kapanış
Çok-kaynaklı (text + CV) pipeline; düşük Jaccard + yüksek coverage ile tamamlayıcılığı gösterdi; hub analizi (full KG) ek genişleme potansiyelini açtı. Fusion & MT drift & ileri KG (entity + weighting) açık geleceğe devredildi.
