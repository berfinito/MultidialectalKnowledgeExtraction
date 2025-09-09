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