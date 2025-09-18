# Tez Tabloları

> Build Metadata:
> - Final Assembly Timestamp (UTC): 2025-09-17
> - Consolidation Source: topic_coherence.md, keyword_overlap.md, keyword_coverage.md, representatives_*_both_top15.md, case1_same_theme_multi_dialect.md, case2_same_topic_multi_speakers.md, case3_original_vs_mt.md, case4_speech_vs_text.md, kg_examples_all.md, kg_examples_full.md, kg_interpretation.md, project_execution_summary.md
> - Note: Bu belge manuel kürasyonla stabilize edilmiştir; tekrar üretim için script çalıştırmadan önce pattern listesini gözden geçir.

## İçindekiler

- [Topic Coherence](#topic-coherence)
- [Keyword Coverage](#keyword-coverage)
- [Keyword Overlap & Novelty](#keyword-overlap--novelty)
- [Representatives - kmr/both](#representatives---kmrboth)
- [Representatives - tr/both](#representatives---trboth)
- [Representatives - zza/both](#representatives---zzaboth)
- [Case Study 1 — Aynı Tema, Çok-Dilli (CV)](#case-study-1--aynı-tema-çok-dilli-cv)
- [Case Study 2 — Aynı Konu, Çok Konuşmacı (Text)](#case-study-2--aynı-konu-çok-konuşmacı-text)
- [Case Study 3 — Orijinal vs Makine Çevirisi (DEFERRED)](#case-study-3--orijinal-vs-makine-çevirisi-deferred)
- [Case Study 4 — Speech (CV) vs Text](#case-study-4--speech-cv-vs-text)
- [KG Examples — Both Top15 (TR/KMR/ZZA)](#kg-examples--both-top15-trkmrzza)
- [KG Examples — Both FULL (TR/KMR/ZZA)](#kg-examples--both-full-trkmrzza)
- [KG Interpretation (Top15 vs Full)](#kg-interpretation-top15-vs-full)
- [Project Execution Summary](#project-execution-summary)

---

## Topic Coherence

| Lang | Variant | #Topics | Outlier% | Coherence | Median | Min | Max |
|------|---------|---------|----------|-----------|--------|-----|-----|
| tr | text | 91 | 43.70% | 0.4258 | 0.3829 | 0.0319 | 0.9667 |
| tr | cv | 240 | 38.27% | 0.3134 | 0.3024 | 0.0978 | 0.7679 |
| tr | both | 112 | 46.29% | 0.4023 | 0.3584 | 0.0411 | 0.8938 |
| kmr | text | 117 | 51.39% | 0.5746 | 0.5697 | 0.0792 | 0.9718 |
| kmr | cv | 354 | 33.53% | 0.2804 | 0.2781 | 0.0778 | 0.5563 |
| kmr | both | 117 | 42.70% | 0.4603 | 0.3657 | 0.1372 | 0.9714 |
| zza | text | 139 | 45.43% | 0.5545 | 0.5129 | 0.1173 | 0.9965 |
| zza | cv | 5 | 8.21% | 0.3439 | 0.3799 | 0.2081 | 0.4198 |
| zza | both | 129 | 42.79% | 0.5931 | 0.6045 | 0.1765 | 0.9964 |

## Keyword Coverage

| Lang | Method | Variant | topN | covered_terms | covered% | avg_doc_coverage |
|------|--------|---------|------|---------------|----------|------------------|
| tr | keybert | text | 200 | 33 | 16.50% | 0.011 |
| tr | keybert | cv | 200 | 171 | 85.50% | 0.276 |
| tr | keybert | both | 200 | 31 | 15.50% | 0.298 |
| tr | yake | text | 200 | 200 | 100.00% | 3.225 |
| tr | yake | cv | 200 | 200 | 100.00% | 1.287 |
| tr | yake | both | 200 | 200 | 100.00% | 3.215 |
| kmr | keybert | text | 200 | 61 | 30.50% | 0.009 |
| kmr | keybert | cv | 200 | 198 | 99.00% | 0.032 |
| kmr | keybert | both | 200 | 200 | 100.00% | 0.018 |
| kmr | yake | text | 200 | 200 | 100.00% | 6.296 |
| kmr | yake | cv | 200 | 199 | 99.50% | 2.758 |
| kmr | yake | both | 200 | 200 | 100.00% | 5.050 |
| zza | keybert | text | 200 | 63 | 31.50% | 0.008 |
| zza | keybert | cv | 200 | 196 | 98.00% | 0.171 |
| zza | keybert | both | 200 | 196 | 98.00% | 0.014 |
| zza | yake | text | 200 | 200 | 100.00% | 4.149 |
| zza | yake | cv | 200 | 200 | 100.00% | 1.706 |
| zza | yake | both | 200 | 200 | 100.00% | 4.206 |

## Keyword Overlap & Novelty

### tr - keybert
| Variant | Count | AvgLen | MultiWord |
|---------|-------|--------|-----------|
| text | 200 | 19.5 | 0.990 |
| cv | 200 | 15.0 | 0.915 |
| both | 200 | 18.2 | 0.960 |

| J(text,cv) | J(text,both) | J(cv,both) | only_text | only_cv | both_total | new_in_both | new_in_both% |
|-----------|--------------|-----------|-----------|---------|------------|-------------|--------------|
| 0.000 | 0.008 | 0.010 | 200 | 200 | 200 | 193 | 96.50% |

### tr - yake
| Variant | Count | AvgLen | MultiWord |
|---------|-------|--------|-----------|
| text | 200 | 5.7 | 0.000 |
| cv | 200 | 5.3 | 0.000 |
| both | 200 | 5.7 | 0.000 |

| J(text,cv) | J(text,both) | J(cv,both) | only_text | only_cv | both_total | new_in_both | new_in_both% |
|-----------|--------------|-----------|-----------|---------|------------|-------------|--------------|
| 0.156 | 0.794 | 0.166 | 146 | 146 | 200 | 17 | 8.50% |

### kmr - keybert
| Variant | Count | AvgLen | MultiWord |
|---------|-------|--------|-----------|
| text | 200 | 18.1 | 0.990 |
| cv | 200 | 13.6 | 0.975 |
| both | 200 | 14.0 | 0.970 |

| J(text,cv) | J(text,both) | J(cv,both) | only_text | only_cv | both_total | new_in_both | new_in_both% |
|-----------|--------------|-----------|-----------|---------|------------|-------------|--------------|
| 0.000 | 0.013 | 0.274 | 200 | 200 | 200 | 109 | 54.50% |

### kmr - yake
| Variant | Count | AvgLen | MultiWord |
|---------|-------|--------|-----------|
| text | 200 | 5.2 | 0.000 |
| cv | 200 | 4.4 | 0.000 |
| both | 200 | 5.2 | 0.000 |

| J(text,cv) | J(text,both) | J(cv,both) | only_text | only_cv | both_total | new_in_both | new_in_both% |
|-----------|--------------|-----------|-----------|---------|------------|-------------|--------------|
| 0.282 | 0.835 | 0.329 | 112 | 112 | 200 | 6 | 3.00% |

### zza - keybert
| Variant | Count | AvgLen | MultiWord |
|---------|-------|--------|-----------|
| text | 200 | 19.0 | 0.995 |
| cv | 200 | 13.5 | 0.955 |
| both | 200 | 17.7 | 0.985 |

| J(text,cv) | J(text,both) | J(cv,both) | only_text | only_cv | both_total | new_in_both | new_in_both% |
|-----------|--------------|-----------|-----------|---------|------------|-------------|--------------|
| 0.000 | 0.042 | 0.117 | 200 | 200 | 200 | 142 | 71.00% |

### zza - yake
| Variant | Count | AvgLen | MultiWord |
|---------|-------|--------|-----------|
| text | 200 | 5.1 | 0.000 |
| cv | 200 | 4.4 | 0.000 |
| both | 200 | 5.1 | 0.000 |

| J(text,cv) | J(text,both) | J(cv,both) | only_text | only_cv | both_total | new_in_both | new_in_both% |
|-----------|--------------|-----------|-----------|---------|------------|-------------|--------------|
| 0.216 | 0.905 | 0.212 | 129 | 129 | 200 | 8 | 4.00% |

## Representatives - kmr/both

### Topic 0 | komun, îtalyayê, şaredariyên, şaredariyeke, parêzgeha
- her wiha serokkomar serokwezîr û wezîrên din tayîn dike, fermandarê bilind yê leşkerî ye û ew e ku peymanên navneteweyî îmze dike û li ser bi cîhkirina çekên navokî.
- ginestra degli schiavoni komun û şaredariyeke parêzgeha benevento ya li herêma kampaniyayê ye ku yek ji komunên li başûrê rojavayê îtalyayê ye.

### Topic 1 | jdb, paşa, the, parser, output
- victor hugo (1802-1885), lamartine (1790-1869), musset (1810-1857), friedrich hölderlin (1770-1843), heinrich von kleist (1777-1811) byron (1788-1824), coleridge (1772-1834), keats (1795-1821), manzoni (1785-1873), pellico (1788-1854), leopardi (1798-1837),mellive (1819-1891), edgar allan poe(1809-1849), whitman (1816-1892), şêx nurî şêx salih, reşît necîp, goran, ebdurehman nifûs, kamûran elî bedirxan, qedrîcan, osman sebrî, cegerxwîn, celadet alî bedirxan
- 1968) björn bjelfvenstam (jdb.

### Topic 2 | jî, xwe, ji, mirov, ku
- lê dîsan bitirriya wan nêr in pêwîstî nîn e em binvîsîn û bixwe jî ew di bêrêzik in.
- bay hesen, bay ḧesen, gundekî dûbisê ye li parêzgeha kerkûkê (îraqê).

### Topic 3 | min, ez, me, te, bûm
- Ez ê bi we re eleqedar bibim.
- Em naaxivin.

### Topic 4 | kurdî, zimanê, kurd, kurdistanê, kurmancî
- Kurdî, dê bi vî rengî wekî gulekê geş bibe
- Ji bo siberoja zarokên kurd ronî be.

### Topic 5 | almanyayê, landkreis, navçeya, şaredariyeke, bavyera
- armagh paytexta county armagh e.
- gönnersdorf şaredariyeke navçeya (landkreis) ahrweilerê li rheinland-pfalz, almanyayê ye.

### Topic 6 | gundekî, navçeya, girêdayî, gund, ser
- îlalî an jî îlano (?) , gundekî li ser navçeya mêzgirê ye.
- gundê gêrê an jî girkebir), gundekî ser navçeya heskîfê elihê ye.

### Topic 7 | ziman, zimanê, zimanên, zimanekî, zimanî
- Her wiha ziman û wêje jî rasterast girêdayî hev in
- ziman şêrîn e

### Topic 8 | pirtûk, pirtûka, pirtûkên, min, pirtûkê
- Min jî helbesta li ser şehîdên Şoreşa Rojavayê xwend.
- di duwanzdesaliya xwe de, pûşkîn di dibistana bi nave tsarkoye selo ye de dixwîne.

### Topic 9 | azerbaycana, navenda, îranê, rojhilat, bajarê
- yasvel , gundekî ser bi navenda bajarê çaroymaq li azerbaycana rojhilat ya îranê ye.
- şûredêl , gundekî ser bi navenda bajarê serab li azerbaycana rojhilat ya îranê ye.

### Topic 10 | wê, ji, bo, re, ew
- Çendê hanê wê ew nîşanî xwediya malê dida.
- Newroz, ji bo gelek netewan sersal e

### Topic 11 | sala, bûye, di, dayik, de
- va ye lîsteya girtiyên mirî li girtîgeha amedê di navbera salên 1981 û 1984an de.
- di sala 1986an de ji ber xebatên xwe yên derbarê bibîrxistina wêjeya afrîkayî guncavê xelata nobelê ya wêjeyê hatiye dîtin.

### Topic 12 | wan, te, hey, tune, wey
- Bimeşe.
- Wan aniye.

### Topic 13 | bavê, wî, pîrê, malbata, min
- mala se'diyê kurê mîrxan û birayêt wî ya li başûrî welatî.
- Pere bi te re heye?

### Topic 14 | tu, hûn, te, xwe, dikî
- tu li cem me tuneyî û em bê kes in!
- Ti carî li ser waneyên xwe dereng namîne.

## Representatives - tr/both

### Topic 0 | albüm, albümü, müzik, şarkı, gitar
- 1972 yılında devlet bakanlığı bünyesinde kadro açılması üzerine istanbul şehir orkestrası, istanbul devlet senfoni orkestrası adını aldı.
- albümün çıkış şarkısı "gözlerinde bıraktım aşkı", radyo listelerinde 1 numaraya yükseldi.

### Topic 1 | john, lisesi, anadolu, william, bantia
- la due, william j.
- niki gudex (d.

### Topic 2 | windows, microsoft, için, kullanıcı, veya
- burada listelenen özellikler, değerleri güvenilir bir şekilde bilinen özelliklerdir.
- cihaz, 64 gb'a kadar microsd kart destekler.

### Topic 3 | üniversitesi, mezun, nde, fakültesi, lisesi
- okul iklimi; güçlü bir liderlik, yüksek performans beklentileri, güvenli ve düzenli bir ortam, temel beceriler ve öğrenci gelişimini izleme sisteminin temel alındığı, edmond'un etkili okullar modelinin temel bir bileşenidir.
- ayrıca, amerika ve asya'daki çeşitli ülkelerin üniversiteleriyle öğrenci transfer sistemini uygulamaktadır.

### Topic 4 | parti, partisi, milletvekili, başkanı, genel
- olağan genel kurulda yönetim kurulu başkanlığına abdulkadir tanrıdağlı seçilmiştir.
- dönem dem parti tunceli milletvekilidir.

### Topic 5 | ilçesine, ilinin, bağlı, mahalledir, köydür
- ilin merkezi alliance şehridir.
- beğendik, edirne ilinin keşan ilçesine bağlı bir beldedir.

### Topic 6 | psychotria, tedavi, veya, neden, kan
- bu hücre dışı yapıların bir araya gelmesi salgı sistemlerine dayalıdır.
- diğer opioidler genellikle orta ile şiddetli ağrıların giderilmesi için kullanılır.

### Topic 7 | film, filmi, tiyatrosu, yapımı, filmde
- böylece slyvester stallone'ye ilham vererek "rocky" filmi çekilmiş oldu.
- körfez, yönetmenliğini emre yeksan'ın gerçekleştirdiği, senaryosunu da yeksan ve ahmet büke'nin birlikte yazdığı 2017 çıkışlı sinema filmidir.

### Topic 8 | evli, evlendi, çocuk, oğlu, babasıdır
- rick wright, the screaming abdabs grubunda beraber çalıştığı juliette gale ile 1964'te evlendi.
- birlikte çocukları olmadı; ikisi de 40 yaşındayken evlenmişlerdi.

### Topic 9 | bölüm, 2021, televizyon, 2019, tarihinde
- 2009 yılında jelte m.
- ağustos 2018'de söz konusu vasiliğin ağustos 2020'ye kadar devam etmesi için izin alındı.

### Topic 10 | kitap, gazetesi, şiir, roman, kitabı
- "iki mektup" adlı şiir derlemesi ağırlıklı olarak aşk sözleri içerir ("ottuuşkun", "iyi çagaa", "seriin hatka kütkütken tal...", "saynı, doştu hörtük-harı höme algan", "iyi sonet", "koharaldın saldarından...", "ergelençig sözün söglem", "sagıjımda bodal..." vb.).
- en çok bilinen kitabı rural rides tır.

### Topic 11 | gol, maçta, maçı, attı, maçında
- dakikasında oyuna dahil olan barış, bu maçta gösterdiği performans ve maçın 76.
- kırk beşer dakikalık iki devreden oluşan 90 dakika sonucunda rakibinden daha fazla gol atan takım, maçtan galip olarak ayrılır.

### Topic 12 | manyetik, hidrojen, dalga, kuantum, enerji
- çekirdeğinde hidrojen kaynağı tükenmiş kırmızı devler çekirdeğini çevreleyen bir kabuk içinde hidrojen termonükleer füzyon başlatırlar.
- bu reaksiyonlardan biri de hidrojel sentezidir.

### Topic 13 | nüfusu, nüfus, şehrin, sayımına, itibarıyla
- 1 ekim 2010 itibarıyla nüfusu 291.838'dir.
- ilin nüfusu 2020 sayımına göre 11,529'dur.

### Topic 14 | savaşı, ordu, ordusu, savaş, karşı
- pers savaşları'nda da görüldüğü gibi kendisinden daha büyük, fakat hafif piyadeden oluşan kuvvetler karşısında başarılı olmaktadır.
- doraemon ve grup, orduyu gölde durdurur.

## Representatives - zza/both

### Topic 0 | yê, ke, zî, kurdan, cinîyan
- "her çî bi eşqê welatî dest pêkerd" qadîr buyukkaya hunermendode zaf muhîm o.
- understanding things fall apart.

### Topic 1 | ez, mi, ma, xo, to
- ma naye red kenê.
- roşna: ya, ez zaf wazena.

### Topic 2 | yê, vera, hêrişê, tirke, cinîyan
- nê prosesî de vurîyayîşanê tewr muhîman ra yew zî wareyê perwerdekerdişê maliman de yo.
- emser rîyê vîrusê korona ra xeylêk merdimî agêrayî dewan û bi nê hawayî waştişê seba zîretî zêdîya.

### Topic 3 | nefero, amardışê, peyêni, 000, hezar
- her kesî waştêne bizano.
- nıfusê komune goreyê amardışê peyêni 250 nefero.

### Topic 4 | grafikê, diagrami, gorey, nıfusê, sero
- grafikê diagrami sero gorey serran ra nıfusê sesué;
- grafikê diyagrami sero gorey serran ra nıfusê bresti;

### Topic 5 | nahiyeyê, hunermend, zazaki, sar, elmanya
- sura hıcri de homa veng dano:ma merdumi mılo ke pociyayo u balçıqo ke vuriyayo ey ra vıraşto.
- perse: sill** vano "tu ziwanêk qij nîyo".

### Topic 6 | keşıf, terefê, biyo, ra, de
- de terefê i ra keşıf biyo.
- de terefê i ra keşıf biyo.

### Topic 7 | ez, nêkenê, mi, nêzana, ma
- ontologiya khane fenomenun nas nêkena.
- se kenê nêkenê, tede çare nêvînenê.

### Topic 8 | kanalizasyoni, şebekey, sistemê, awe, ratneyao
- coussey de şebekey awe esto û sistemê kanalizasyoni ratneyao.
- othe de şebekey awe esto û sistemê kanalizasyoni vıraziyayo.

### Topic 9 | estareyanê, komê, neweyê, katalogê, cısım
- no cısım katalogê neweyê pêroyi de, komê estareyanê miyan de ca gêno.
- no cısım katalogê neweyê pêroyi de, komê estareyanê miyan de ca gêno.

### Topic 10 | tirkî, tirkîya, îstanbul, stanbul, 975
- 18 tışrino peyên 1957, i̇stanbul), yew profesorê matematikiyo.
- hetê bînî ra vervatoxê wezaretê karan ê teberî yê çînî shûangî veng da dewleta tirkî ke hukmatê tirkî bandura sûrîye rê hûrmet bimojne.

### Topic 11 | philadelphia, pittsburgh, john, william, james
- necmettin erbakan (b.
- michael m.

### Topic 12 | katalogê, neweyê, cısım, pêroyi, gêno
- no cısım katalogê neweyê pêroyi de ca gêno.
- no cısım katalogê neweyê pêroyi de ca gêno.

### Topic 13 | kurdî, kurdîstanî, şarê, rayberê, abdullah
- belê, neslo newe xwu 'sîyasî' vîneno, la şuûrê kurdîtîye tey çin o.
- dimilkî (kirdkî) jî yek ji zaravayên zimanê kurdî ye û tu hêz nikare vê rastiyê berovajî bike.

### Topic 14 | elektrik, internet, anciyao, kanalizasyoni, şebekey
- brûlon de şebekey awe esto, sistemê kanalizasyoni, elektrik û internet anciyao.
- chessy de şebekey awe esto, sistemê kanalizasyoni, elektrik û internet anciyao.

## Case Study 1 — Aynı Tema, Çok-Dilli (CV)

Amaç: CV konuşmalarında aynı temayı TR/KMR/ZZA için karşılaştırmak.  
Yöntem: CV/both varyantı topic temsilcileri ve KeyBERT listeleri incelendi.

Nicel özet:
- KeyBERT: J(text,cv) ≈ 0 → kaynaklar arası tamamlayıcılık yüksek.
- Coverage: cv/both’ta KeyBERT kapsamı yüksek.

Nitel referanslar:
- TR (both): reports/analysis/representatives_tr_both_top15.md
- KMR (both): reports/analysis/representatives_kmr_both_top15.md
- ZZA (both): reports/analysis/representatives_zza_both_top15.md

Kısa yorum:
- Spor/siyaset/yerleşim temaları ortak; diakritik/yerel adlandırma ve kalıp farkları lehçe/dil özgü varyasyonları gösteriyor.

## Case Study 2 — Aynı Konu, Çok Konuşmacı (Text)

Amaç: Tek bir konu (“göç”/“eğitim”) etrafında farklı paragrafların etkisini gözlemek.  
Yöntem: Wiki + Zazagorani text varyantı temsilciler ve KeyBERT listeleri incelendi.

Nicel özet:
- YAKE (unigram) varyant değişiminden daha az etkilenir.
- KeyBERT çok-kelimeli yapısı nedeniyle bağlamsal çeşitliliği yansıtır.

Nitel referanslar:
- TR reps (text/both): representatives_tr_both_top15.md
- KMR reps (text/both): representatives_kmr_both_top15.md
- ZZA reps (text/both): representatives_zza_both_top15.md

Kısa yorum:
- Çekirdek kavramlar sabit; çevresel terimler kültürel/lehçe özgü bir halo oluşturuyor.

## Case Study 3 — Orijinal vs Makine Çevirisi (DEFERRED)

Durum:
- TR pivot makine çevirisi üzerinden “orijinal lehçe vs MT” topic/keyword drift çalışması zaman kısıtı nedeniyle yapılmadı.
- Metodoloji burada tam kaydedildi (gelecekte doğrudan uygulanabilir).

Amaç:
- Orijinal KMR/ZZA belgeleri ile TR pivot çevirileri arasında topic yapısı, anahtar kelime dağılımı ve leksikal çeşitlilikte sapma (drift) ölçmek.

Önerilen Veri Kurulumu:
1. Kaynak korpuslar: KMR & ZZA wiki + Zazagorani.
2. Pivot dil: TR (model desteği yüksek).
3. MT araçları: Helsinki-NLP OPUS-MT ku–tr, diq–tr veya uygun bir çok-dilli M2M modeli.
4. İki korpus türevi:
   - Original (lehçe)
   - MT→TR (çeviri)

Deney Boru Hattı:
1. Ortak normalizasyon + segmentasyon.
2. Topic Modeling (BERTopic) ayrı ayrı:
   - (a) Orijinal lehçe korpusu
   - (b) Lehçe→TR MT korpusu
3. Karşılaştırma Metrikleri:
   - Topic set overlap (Jaccard) → temsilci terim kümeleri bazlı
   - Term rank correlation (top-10 Spearman ρ) + greedy veya Hungarian eşleştirme
   - Keyword drift (KeyBERT top-N Jaccard, YAKE karşılaştırmalı)
   - Lexical diversity delta (MultiWord% değişimi)
4. Hata / Sapma Analizi:
   - Diakritik kaybı
   - Özel ad / NER bozulması
   - Fonetikleştirme ve TR normlarına aşırı yaklaşma

Potansiyel Bulgular (Beklenen):
- Lehçe özgü kültürel adların genelleşmesi → topic merkezîleşmesi
- Çok-kelimeli bileşiklerin sadeleşmesi → MultiWord% düşüşü
- Köprü (bridge) topiclerinin derecesinde azalma (KG’de)

Rapor Şablonları (Örnek):
| Lang | Variant | #Topics | Coherence | Outlier% |
|------|---------|---------|-----------|----------|
| kmr | original | … | … | … |
| kmr | mt2tr | … | … | … |
| zza | original | … | … | … |
| zza | mt2tr | … | … | … |

Keyword Drift (örnek):
| Lang | Method | J(orig,mt) | only_orig | only_mt | shared |
|------|--------|-----------|----------|--------|--------|
| kmr | keybert | … | … | … | … |

Riskler / Neden Ertelendi:
- ZZA için MT kalite belirsizliği (drift ölçümü gürültülü olabilir)
- Ek kaynak maliyeti (çeviri + ikinci topic eğitimi)

Gelecek Adımlar:
1. Pilot 2K doküman MT kalite ölçümü (ChrF / BLEU + 50 cümle manuel)
2. ChrF > 40 sağlanırsa tam korpus
3. Hungarian assignment ile topic hizalama (cosine embedding)
4. KG edge persistence analizi (hub continuity)

Özet:
- “Çeviri tabanlı homojenleştirme” etkisi nicellenebilecek; metodoloji hazır beklemeye alındı.

## Case Study 4 — Speech (CV) vs Text

### TR
- KeyBERT:
  - J(text,cv): 0.0
  - Coverage% → text: 16.5 | cv: 85.5 | both: 15.5
  - Yorum: text–cv kesişimi çok düşük; konuşma verisi tamamlayıcı.
- YAKE:
  - J(text,cv): 0.156
  - Coverage% → tüm varyantlar 100%
  - Yorum: Unigram stabil; tamamlayıcılığı KeyBERT daha iyi gösterir.

### KMR
- KeyBERT:
  - J(text,cv): 0.0
  - Coverage% → text: 30.5 | cv: 99.0 | both: 100.0
  - Yorum: Benzer tamamlayıcılık.
- YAKE:
  - J(text,cv): 0.282
  - Coverage% → ~100%
  - Yorum: Unigram doğası gereği varyanta duyarsız.

### ZZA
- KeyBERT:
  - J(text,cv): 0.0
  - Coverage% → text: 31.5 | cv: 98.0 | both: 98.0
  - Yorum: Konuşma kaynaklı terim çeşitliliği.
- YAKE:
  - J(text,cv): 0.216
  - Coverage% → 100%
  - Yorum: Yine unigram stabilitesi.

Kaynaklar:
- reports/analysis/keyword_overlap.md
- reports/analysis/keyword_coverage.md

## KG Examples — Both Top15 (TR/KMR/ZZA)

| Lang | Nodes | Edges | WeightedSum | AvgWeightedDeg | Density | AvgEdgeW | MedDeg | MaxDeg | MinDeg |
|------|-------|-------|-------------|----------------|---------|----------|--------|--------|--------|
| tr | 73 | 150 | 150 | 4.11 | 0.057 | 1.00 | 4 | 8 | 4 |
| kmr | 66 | 150 | 150 | 4.55 | 0.070 | 1.00 | 4.0 | 12 | 4 |
| zza | 65 | 142 | 150 | 4.62 | 0.068 | 1.06 | 4 | 8 | 4 |

Açıklama:
- top15 (trimmed reps) → yoğun kavramsal çekirdek
- Edge ağırlıkları ≈1 → tekrar düşük (top-5 terim kesmesi)

## KG Examples — Both FULL (TR/KMR/ZZA)

| Lang | Nodes | Edges | WeightedSum | AvgWeightedDeg | Density | AvgEdgeW | MedDeg | MaxDeg | MinDeg |
|------|-------|-------|-------------|----------------|---------|----------|--------|--------|--------|
| tr | 535 | 1130 | 1140 | 4.26 | 0.008 | 1.01 | 4 | 16 | 4 |
| kmr | 505 | 1155 | 1180 | 4.67 | 0.009 | 1.02 | 4 | 28 | 4 |
| zza | 444 | 1119 | 1290 | 5.81 | 0.011 | 1.15 | 4.0 | 56 | 4 |

Açıklama:
- Ölçek büyüyünce (node 7–8x) density doğal olarak düşer
- Hub yapıları (özellikle ZZA) görünür hale gelir

## KG Interpretation (Top15 vs Full)

Özet:
- Ölçek artışı → density 0.057–0.070’den 0.008–0.011’e → seyrekleşme normal
- ZZA hub patlaması (MaxDeg 8→56) → yerel/kültürel kümeler köprü rolü
- Ortalama edge ağırlığı ≈1 → tekrar sınırlı; PMI / TF-IDF ile zenginleştirme gerekli
- KMR hub artışı (12→28) → coğrafya / kimlik terimlerinin bağlayıcı profili
- Full KG → ileride entity linking + bipartite modularity için topolojik temel

### Weighted KG (PMI vs TF-IDF) Kısa Özet

| Lang | Set    | Topics | RawPairs (T*10) | UniqueEdges | DupLoss% | TF-IDF Weight Range | PMI Avg |
|------|--------|--------|-----------------|-------------|---------|---------------------|--------|
| tr   | top15  | 15     | 150             | 150         |  0.0% | 2.708–2.708         | 3.80   |
| tr   | full   | 114    | 1140            | 1130        |  0.9% | 4.74–10.91          | 6.60   |
| kmr  | top15  | 15     | 150             | 150         |  0.0% | 2.708–2.708         | 3.39   |
| kmr  | full   | 118    | 1180            | 1155        |  2.1% | 4.77–13.54          | 6.24   |
| zza  | top15  | 15     | 150             | 142         |  5.3% | 2.71–4.03           | 3.51   |
| zza  | full   | 129    | 1290            | 1119        | 13.3% | 4.86–23.96          | 5.81   |

Notlar:
- DupLoss%: Potansiyel (topic başına C(5,2)=10) kenar sayısından tekrar yüzünden kayıp.
- ZZA’da yüksek DupLoss% → terim kümeleri daha yoğun ortak çekirdek (lehçe varyantları dar kavramsal merkez).
- TF-IDF top15’in tekil değeri: her çift cf=1 → idf sabit. Full grafikte cf>1 çiftler spektrumu açıyor.
- PMI hiçbir dilde negatif değil; seçilen ilk 5 terim kümeleri birlikte görülme olasılığı beklenenden hep yüksek (yüksek birliktelik çekirdeği).
- Kaynak: İlgili istatistikler reports/analysis/*_kg_{top15,full}_{pmi,tfidf}_stats.json (avg / min / max alanları).

## Project Execution Summary

### 1. Sprint Templatı ve Gerçekleşenler
| Sprint | Odak | Ana Çıktılar | İlgili Artefaktlar |
|--------|------|--------------|--------------------|
| S1 | ASR Baseline | Whisper (medium/large) valid/test WER/CER, bias & beam aramaları | reports/asr_*.json, asr_summary_*.md |
| S2 | Cross-Dialect & Model Seçimi | ZZA/KMR dil zorluk analizi, bias etkisi, decode varyantları | confusion_*.json, asr_compare_* |
| S3 | Text Ingest & N-gram | Wiki + Zazagorani çekme, temizleme, n-gram istatistikleri | reports/text_stats/* |
| S4 | Normalization & Final Corpora | Unicode NFKC, lowercase, segmentasyon, deduplikasyon | data/processed/*.parquet |
| S5 | Topic & Keywords + Ablations + Case Studies + Mini KG | BERTopic varyantları, KeyBERT/YAKE, coherence/overlap/coverage, reps, KG, case1/2/4 | reports/analysis/*.md |

### 2. Core Test Cases
| TC | Tanım | Durum | Kanıt / Dosyalar |
|----|------|-------|------------------|
| TC-1 | Çok-dilli ASR değerlendirme (WER/CER/RTF) | Tamamlandı | asr_*summary*.md, confusion_*.json |
| TC-2 | Cross-dialect decoding etkisi | Tamamlandı | confusion_*_TRdecode.json, bias varyantları |
| TC-3 | ASR + LM Fusion (shallow) | Deferred | future_work.md |
| TC-4 | Topic & Keyword Extraction (çok-kaynak) | Tamamlandı | topic_coherence.md, keyword_overlap.md, keyword_coverage.md |

### 3. Ablations ve Analizler
| Ablation | Amaç | Metod / Metrik | Çıktı |
|----------|------|----------------|-------|
| Topic Coherence | Varyant kalite karşılaştırma | c_npmi, c_v, outlier% | topic_coherence.md |
| Keyword Overlap | Kaynak tamamlayıcılık | Jaccard, new_in_both% | keyword_overlap.md |
| Keyword Coverage | Terim doküman içi kapsama | covered%, avg_doc_coverage | keyword_coverage.md |
| Representatives | Nitel doğrulama | Top terimler + örnek cümle | representatives_* |
| Mini KG | Kavramsal köprü yoğunluğu | Co-occurrence stats | kg_examples_all.md |
| Full KG | Hub / yapı genişlemesi | Degree & density | kg_examples_full.md |

### 4. Case Studies
| Case | Başlık | Durum | Dosya |
|------|--------|-------|-------|
| CS-1 | Aynı Tema, Çok-Dilli (CV) | Tamamlandı | case1_same_theme_multi_dialect.md |
| CS-2 | Aynı Konu, Çok Konuşmacı (Text) | Tamamlandı | case2_same_topic_multi_speakers.md |
| CS-3 | Orijinal vs MT | Deferred | case3_original_vs_mt.md |
| CS-4 | Speech (CV) vs Text | Tamamlandı | case4_speech_vs_text.md |

Case3 (Original vs MT): Pilot KMR/ZZA→TR (NLLB-200) hyp üretildi; referans yok → drift analizi ertelendi.

### 5. Repro / İzlenebilirlik
- Ortam: env.txt, env_freeze.txt, versions.json, git_commit.txt
- Komut Özetleri: future_work.md (Repro bölümü)
- Veri Kaynakları: data/raw/commonvoice/*, data/raw/wiki/*, data/raw/zazagorani/*
- Konsolidasyon: thesis_tables.md

### 6. Riskler ve Sınırlar
| Alan | Risk | Etki | Karşılık |
|------|------|------|----------|
| MT Kalitesi (CS-3) | ZZA çeviri zayıf | Drift ölçümü bozulur | Pilot + kalite eşiği |
| Fusion Gecikmesi | Zaman yetersizliği | WER iyileştirmesi ertelendi | Gelecek sprint |
| Entity Linking | Ad varyantları | KG bağlam kaybı | Wikidata planı |
| Full KG Boyutu | Bellek / karmaşıklık | Çalışma süresi | top15 filtre + incremental |

### 7. Future Work (Özet)
- Shallow Fusion (KenLM 3/5-gram, λ grid)
- Bipartite / full-topic KG
- Entity Linking (Wikidata)
- Edge PMI / TF-IDF ağırlıkları
- MT vs Original drift (tam uygulama)
- ASR fine-tuning (lehçe)
- Gelişmiş deduplikasyon (LSH + fuzzy)

### 8. Kapanış
Çok-kaynaklı (text + CV) yapı: düşük Jaccard + yüksek coverage → tamamlayıcılık kanıtı. Mini & full KG: kavramsal çekirdek 