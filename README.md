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