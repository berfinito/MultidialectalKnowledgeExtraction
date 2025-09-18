<!-- UPDATE (MT Pilot):
     NLLB-200 (600M, fp16, beam=4) ile kmr_Latn->tur_Latn ve diq_Latn->tur_Latn 300+300 hip üretildi.
     Kaynaklar mojibake temizlendi (*.fixed.src); çıktı dosyaları *.fixed.hyp.
     TR referans segmentleri YOK => BLEU/ChrF ve topic/keyword drift analizi BU SÜRÜMDE BLOKELENDİ.
     Devam koşulu: hizalı TR referansları sağla, sonra mt_pilot_quality.py çalıştır. -->
     
# Case Study 3 — Orijinal vs Makine Çevirisi (DEFERRED)

Durum:
- Zaman kısıtı nedeniyle planlanan MT (örneğin TR<->KMR / TR<->ZZA pivot çeviri) karşılaştırma deneyleri uygulanmadı.
- Bu bölüm metodoloji taslağı ve beklenen katkıyı belgeleyerek ileride tamamlanması için temel sağlar.

Amaç:
- Topic ve keyword dağılımlarının (özellikle çok-kelimeli KeyBERT terimlerinin) orijinal lehçe/dil dokümanları ile makine çevirisi üzerinden elde edilen sürümleri arasında yapısal sapma gösterip göstermediğini ölçmek.

Önerilen Veri Kurulumu:
1. Kaynak: KMR ve ZZA wiki + Zazagorani metinleri.
2. Pivot Dil: TR (daha büyük dil modeli dayanağı).
3. MT Araçları (seçenekler):
   - Helsinki-NLP OPUS-MT modelleri (ku–tr, diq–tr) veya var ise fine-tuned M2M.
4. İki korpus oluşturma:
   - Original: Orijinal lehçe metinleri.
   - MT→Pivot: Lehçe → TR çevirileri.

Deney Boru Hattı:
1. Aynı normalizasyon ve segmentasyon.
2. Topic Modeling:
   - (a) Orijinal lehçe belgeleri (BERTopic)
   - (b) Çevrilmiş (lehçe→TR) belgeler (BERTopic)
3. Karşılaştırma Metrikleri:
   - Topic set overlap: Jaccard (topic label yerine temsilci terim kümeleri bazlı).
   - Term rank correlation: En üst 10 terim için Spearman ρ (topic-topic hizalama greedy eşleştirme).
   - Keyword drift: KeyBERT top-N kesişim oranı (orijinal vs MT).
   - Lexical diversity delta: MT’nin çok-kelimeli oranı düşürüyor mu? (MultiWord%)
4. Hata / Sapma Analizi:
   - Diyakritikli token kaybı.
   - NER / özel ad bozulmaları.
   - Fonetikleştirilmiş formların TR normlarına “yanlış” yakınsaması.

Potansiyel Bulgular (Beklenen):
- MT, lehçe-özgü kültürel / yerel adlandırmaları genelleştirerek bazı topic’leri “daha merkezî” TR dağılımlarına itebilir.
- Çok-kelimeli bileşiklerde bölünme veya sadeleşme → MultiWord% düşüşü.
- Köprü (bridge) topic’lerinin (co-occurrence KG’de yüksek derece adayları) MT’de yoğunluk farklılığı (daha homojen, daha az köprü).

Raporlanacak Örnek Tablolar:
| Lang | Variant | #Topics | Coherence | Outlier% |
|------|---------|---------|-----------|----------|
| kmr | original | … | … | … |
| kmr | mt2tr | … | … | … |
(aynısı zza için)

Keyword Drift (örnek şablon):
| Lang | Method | J(orig,mt) | only_orig | only_mt | shared |
|------|--------|-----------|----------|--------|--------|
| kmr | keybert | … | … | … | … |

Riskler / Neden Ertelendi:
- MT kalitesi özellikle ZZA için düşük → ölçümlerin sinyal-gürültü oranı belirsiz.
- Yüksek maliyet: Çeviri + yeni topic mod. tüm varyantlarda süre sınırına takıldı.

Gelecek Çalışma Adımları:
1. Küçük örnek (pilot 2K doküman) ile kalite ön ölçümü (BLEU/ChrF + manuel 50 cümle).
2. Kalite eşiği (örn. ChrF > 40) sağlanırsa tam korpus deneyine genişleme.
3. Otomatik topic eşleme algoritması (Hungarian assignment ile -cosine sim).
4. KG seviyesinde “edge persistence” analizi: MT’nin kavramsal köprüleri inceltip inceltmediği.

Özet:
Bu case, çok-dilli / çok-lehçeli bilgi çıkarımında “çeviri tabanlı homojenleştirme” etkisini sayısallaştırmayı hedefliyor; metodoloji burada donduruldu ve ileride doğrudan uygulanabilir.
