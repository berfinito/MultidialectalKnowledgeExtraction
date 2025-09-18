# MT Referans Hazırlık Rehberi

Amaç: KMR / ZZA → TR pivot çevirileri ile orijinal TR referansları hizalamak ve drift ölçümlerine gürültüsüz girdi sağlamak.

## 1. Kaynak Dosya Formatı
- Her satır = tek segment (cümle / kısa paragraf)
- UTF-8, BOM yok
- Ön temizlik: Unicode NFKC, lowercase (karşılaştırma öncesi), fazladan whitespace collapse

## 2. Segmentasyon
Öneri:
1. Noktalama tabanlı cümle bölme (". ? !" + followed by space + uppercase / digit)
2. 600 karakterden uzun segmentleri ek ayraçlara göre böl (",", ";", "—")

## 3. Filtreler
- Boş veya sadece sayı/işaret içeren satırı at
- 2 karakter altı (ör: "ok") incele → çoğu zaman meta gürültü
- Tekrarlanan satırları (tam string eşleşmesi) sadeleştir (frekans tut ki istatistik bozulmasın)

## 4. TR Referans Seti
- Aynı domain (wiki vs wiki, Zazagorani vs benzer tematik TR)
- Her lehçe segmenti için TR’de potansiyel karşılık gerekmez; sadece kalite kıyası değil drift analizi yapacağız:
  - Drift metrikleri: Topic term overlap / rank, keyword Jaccard, lexical diversity, multiword ratio

## 5. Çeviri (Pilot)
- Model: NLLB-200 distilled 600M (fp16, batch token packing)
- Parametreler: beam=4, no_repeat_ngram_size=3, repetition_penalty=1.1
- Kaydet: 1) source.txt 2) hyp.tr.txt 3) meta.jsonl (utt_id, len_src, len_hyp, elapsed_ms)

## 6. Hizalama
- Aynı sıra varsayımı (satır i → satır i) — ek karmaşıklık yok
- Olası bozulma durumunda Levenshtein uzunluk oranı < 0.4 olan satırları “mismatch” etiketiyle ayık listede tut

## 7. Temizlik Kuralları
| Aşama | Kural | Örnek |
|-------|-------|-------|
| Normalizasyon | Çoklu boşluk → tek boşluk | "iki   kelime" → "iki kelime" |
| Noktalama | Unicode tırnak → ASCII | “a” → "a" |
| Diakritik | (Opsiyonel) koru (lehçe analizi için gerekli) | "ê" kalır |
| Sayısal | Yüzdelik alanları boş bırakma | "% 20" → "%20" |

## 8. Kalite Pilot Eşiği
| Metrik | Eşik | Not |
|--------|------|-----|
| ChrF | ≥ 40 | Aksi halde drift çalışması ertelenir |
| BLEU | Bilgilendirici | Düşük olsa bile ChrF temel |
| Uzunluk Oranı | 0.85–1.25 | Aykırı segmentler incelenir |

## 9. Drift Çalışması İçin Etiketler
JSONL alanları (örnek):
```
{"utt_id":"kmr_000123","src":"...","hyp_tr":"...","ref_tr":"...","len_src":34,"len_hyp":31,"chrF":0.52}
```

## 10. Gelecek Otomasyon
- Otomatik segment kalite filtreleme (ChrF < 0.25 → inceleme)
- Hungarian topic alignment (embedding centroid cosine)
- Edge persistence: KG’de orijinal vs pivot ortak/kaybolan kenar listesi

## 11. Özet
Tutarlı satır hizalaması + düşük gürültülü temizlik → drift metrikleri güvenilir.