# Tez Tabloları

> Build Metadata:
> - Timestamp: 2025-09-18T23:07:41.653933Z
> - Git Commit: 1a65470
> - Source Patterns: topic_coherence.md,keyword_overlap.md,keyword_coverage.md,representatives_tr_both_top15.md,representatives_kmr_both_top15.md,representatives_zza_both_top15.md,case1_*,case2_*,case3_*,case4_*,kg_examples_*.md,kg_interpretation.md,project_execution_summary.md

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

## Representatives - trimmed top15

### Topic 0 | albüm, albümü, müzik, şarkı, gitar
- oda orkestrası için senfoni.
- 1980'lerin başında akordeoncu ıvan milev'in teşvikleriyle "mladost" düğün orkestrasına girdi.

### Topic 1 | john, lisesi, anadolu, william, bantia
- tıva şamanları (тувинские шаманы)., м.: «маска», 2009, 328 стор.
- barnes, a.

### Topic 2 | windows, microsoft, için, kullanıcı, veya
- nokia 3; hmd global tarafından tasarlanmış, nokia markalı, android işletim sistemini kullanan orta seviye bir akıllı telefon.
- kamera, yalnızca telefonlarda bulunan ios'lara benzer bir panorama yakalama özelliğine sahiptir.

### Topic 3 | üniversitesi, mezun, nde, fakültesi, lisesi
- okul iklimi; güçlü bir liderlik, yüksek performans beklentileri, güvenli ve düzenli bir ortam, temel beceriler ve öğrenci gelişimini izleme sisteminin temel alındığı, edmond'un etkili okullar modelinin temel bir bileşenidir.
- derecesiyle mezun olmuştur.

### Topic 4 | parti, partisi, milletvekili, başkanı, genel
- 2017 seçimleri ardından radikal parti ile temasa geçilmiş ve 2017 yılında iki radikal parti birleşerek radikal hareket adını almış parti udı'den de ayrılmıştır.
- 2000'deki üçüncü konferansında "yekiti kürdistan partisi - suriye" merkez komitesi'ne seçildi ve 2006'da üçüncü konferansında yekiti partisi'nin siyasi bürosunun bir üyesi olarak seçildi.

### Topic 5 | ilçesine, ilinin, bağlı, mahalledir, köydür
- sebald's 'a place in the country'" başlıklı inceleme yazısı (ingilizce)
- boston, washington, dc ve new york'tan oluşan bölgede kurgusal şehir mega city one kurulmuştur.

### Topic 6 | psychotria, tedavi, veya, neden, kan
- bu hücre dışı yapıların bir araya gelmesi salgı sistemlerine dayalıdır.
- mitokondri ve kloroplastlar gibi dna taşıyan organeller, sırasıyla, hücrenin geri kalanının en azından bir kısmının atadan kalma bir arke prokaryot hücresinden türetilmiş olabileceği, eski simbiyotik oksijen soluyan bakterilerin ve siyanobakterilerin kalıntılarıdır.

### Topic 7 | film, filmi, tiyatrosu, yapımı, filmde
- mukadderat, nadim güç tarafından yönetilen senaryosunu erdi ışık'ın kaleme aldığı başrollerinde nur sürer, aslıhan gürbüz ve osman sonant'ın yer aldığı 2024 yapımı komedi, dram filmi.
- hızlı ve ölü için yazar simon moree'un komutuyla mayıs, 1993'te sony pictures entertainment tarafından satın alınan ve aktris sharon stone tarafından co-prodüktör olarak imzalandı.

### Topic 8 | evli, evlendi, çocuk, oğlu, babasıdır
- bazı kayıtlar, ikisinin petersburg seferi sırasında tanıştığını ve culpeper, virginia'da evlendiğini bildiriyor.
- tony'nin yakınlarda evlenmeyi pek düşünmediği susan (wendy craig) adında bir de nişanlısı vardır.

### Topic 9 | bölüm, 2021, televizyon, 2019, tarihinde
- 2009 yılında jelte m.
- summer 2007, vol.

### Topic 10 | kitap, gazetesi, şiir, roman, kitabı
- genellikle faruk nafiz çamlıbel duyarlılığında ve aşk, ayrılık, özlem temaları ekseninde çoğalttığı şiirini, 1973 yılında büyük oğlu vedat oğuzcan'ın vefatı üzerine, hayatın boşluğu, ölüm ve acı gibi derinliklere, öz ve biçim yoğunlaştırmalarına yöneltmiştir.
- zevk, eğlence, içki şiirlerinin temelini oluşturmuştur.

### Topic 11 | gol, maçta, maçı, attı, maçında
- (30 gol katkısı)
- michael thomas neredeyse sezonun son şutu sayılabilecek bir vuruşla kırmızıların defansını aşarak arsenal'in ikinci golünü kaydetmiş ve liverpool'un, henüz hiçbir ingiliz kulübünün gerçekleştiremediği, lig şampiyonluğu ve fa cup'ı birlikte iki sezon üst üste kazanmayı başarmasını engelledi.

### Topic 12 | manyetik, hidrojen, dalga, kuantum, enerji
- yüksek kinetik enerjili elektronların ve pozitifi iyonların tekrar birleştirilmesi genelde kendiliğinden iyonlaştırıcı rydberd durumlarını oluşturken düşük enerjili tekrar birleştirim makul durağan rydberg atomlarıyla sonuçlanır.
- manyetizma fiziği, demir, nikel, kobalt (fe, ni ve co) benzeri maddeleri çeken cisimleri, mıknatısın çevresinde oluşan manyetik alan, manyetik kuvvet ve bunların etkileşimlerini araştıran fizik dalıdır.

### Topic 13 | nüfusu, nüfus, şehrin, sayımına, itibarıyla
- ilçenin nüfusu 148.032 insan (2009 sayımlarına göre)'dir.
- komünün nüfusu 2016 yılı itibarıyla 2.732'dir.

### Topic 14 | savaşı, ordu, ordusu, savaş, karşı
- kılıç arslan kuvvetleri haçlılar ve bizanslıların ağır süvari taarruzlarını en azından bir süre önlemişler ve 4.000 civarında zayiat verdirmiştirler.
- biggs ile wedge (az maaş alan iki galbadian askeri) bu görevi yapmak üzeredirler ve "iletişim kulesi"nin üstündedirler.

## Representatives - trimmed top15

### Topic 0 | komun, îtalyayê, şaredariyên, şaredariyeke, parêzgeha
- maiori komun û şaredariyeke parêzgeha salernoya li herêma kampaniyayê ye ku yek ji şaredariyên li başûrê rojavayê îtalyayê ye.
- di vê heyama salê êdî ev seramaya destpêka zivistanê işkestiye û eger jî berfek bibare zû dihele û vedibe.

### Topic 1 | jdb, paşa, the, parser, output
- victor hugo (1802-1885), lamartine (1790-1869), musset (1810-1857), friedrich hölderlin (1770-1843), heinrich von kleist (1777-1811) byron (1788-1824), coleridge (1772-1834), keats (1795-1821), manzoni (1785-1873), pellico (1788-1854), leopardi (1798-1837),mellive (1819-1891), edgar allan poe(1809-1849), whitman (1816-1892), şêx nurî şêx salih, reşît necîp, goran, ebdurehman nifûs, kamûran elî bedirxan, qedrîcan, osman sebrî, cegerxwîn, celadet alî bedirxan
- hasan cemal (jdb.

### Topic 2 | jî, xwe, ji, mirov, ku
- di axiveran de henry könig wek vebêjer, gerhart hinze wek zamorra û christine pappert wek nicole duval hebûn.
- çarenivîs (qeder) "ji roja ku mirov ji dayîka xwe dibe tê dunyayê û hetanî roja ku mirov dimire, ji kar û kirên ku mirov dikin û bûyerên ku tên serê mirovan, rê ya ku mirov tê de diçe û ji liv, tevger, fikr û ramanên mirov re qeder tê gutin" yanî jiyana mirovan qedera mirovan e.

### Topic 3 | min, ez, me, te, bûm
- bi tevşo kevirekî ez ê bişikînim.
- Ez kar dikim

### Topic 4 | kurdî, zimanê, kurd, kurdistanê, kurmancî
- sala du hezar û bîst û yekê ew ê bibe sala kurdî.
- di mehkemê da xwedî û berpirsiyarê rojnamê gotin: "bi kurdî weşan derxistin heqê me ye û emê bikin!"

### Topic 5 | almanyayê, landkreis, navçeya, şaredariyeke, bavyera
- tettau şaredariyeke navçeya (landkreis) kronach li herêma bavyera ya almanyayê ye.
- essingen şaredariyeke navçeya (landkreis) ostalbkreis li herêma baden-württemberg a almanyayê ye.

### Topic 6 | gundekî, navçeya, girêdayî, gund, ser
- bêmbo , gundekî ku bi navçeya şemzînana hekariyê ve girêdayî ye.
- ûrik , gundekî girêdayê navçeya îlîç a erzînganê ye.

### Topic 7 | ziman, zimanê, zimanên, zimanekî, zimanî
- awaye dîyelektikê ku hegel têne ser ziman mengiwer û ankû "îdealîzm" e.
- assembly (bixwîne esêmblî), zimanekî bernamesaziyê ye.

### Topic 8 | pirtûk, pirtûka, pirtûkên, min, pirtûkê
- Dermanê ji me re pêwîst li ser pelekê dinivîse.
- ev roman, ji ve nerînê, xwendevantîye di dibistan û zaningehên tirkande baș dide naskirin.

### Topic 9 | azerbaycana, navenda, îranê, rojhilat, bajarê
- virniq , gundekî ser bi navenda bajarê tebrîzê li azerbaycana rojhilat ya îranê ye.
- qişlaq necefxanlû , gundekî ser bi navenda bajarê eherê li azerbaycana rojhilat ya îranê ye.

### Topic 10 | wê, ji, bo, re, ew
- Ew ê wê birevîne.
- Her dima li fera jêrê.

### Topic 11 | sala, bûye, di, dayik, de
- gerard 't hooft perwerdeya xwe ya amadeyî sala 1964î li dalton lyceum li den haag bidawî dike.
- veavakirina di rêzeya piçûk watchmen (1986) de bi dawî bû.

### Topic 12 | wan, te, hey, tune, wey
- Zarokan çawa qad paqij kir?
- Wan xwest

### Topic 13 | bavê, wî, pîrê, malbata, min
- Ji aliyê xwandinê ve jî bavê wî guhên xwe baş didayê.
- Ew bavê min e.

### Topic 14 | tu, hûn, te, xwe, dikî
- Qet li halê xwe napirsî
- Berçavê te sor bûye.

## Representatives - trimmed top15

### Topic 0 | yê, ke, zî, kurdan, cinîyan
- hêzanê asayîşê zereyî 30 hezar endamê xo seba pawitişê erazîyan wezîfedar kerdî.
- cao ke rızci tey rızcinı keno ê cay rê zi vanê dukanê rızi ya zi rızxane.

### Topic 1 | ez, mi, ma, xo, to
- ma pêro bîyî egîd, ma xo eştî verarê to û lew na to.
- heto ke roc beno vindi.

### Topic 2 | yê, vera, hêrişê, tirke, cinîyan
- nê hêrişî têna vera şingal û mexmûrî nîyê, vera estbîyayîşê kurdan o.
- roza kobanê: têkoşînê cinîyan ê dinya û xoverdayîşê cinîyan ê kurdan çimeyê awanbîyayîşê ypjyî yo.

### Topic 3 | nefero, amardışê, peyêni, 000, hezar
- her kesî waştêne bizano.
- ay wextan enê cayanê ma di heş û verg û teyr û turî zaf bî, goştê cesedan pêro ameybi werî.

### Topic 4 | grafikê, diagrami, gorey, nıfusê, sero
- grafikê diyagrami sero gorey serran ra nıfusê avertoni;
- grafikê diagrami sero gorey seran ra nıfusê mansigné;

### Topic 5 | nahiyeyê, hunermend, zazaki, sar, elmanya
- hewl başli/sifê rwej/roji bıke, zerrê rwejıd (roji de) qarşi olayonıd (biyayis de) quweta xo bezkerdışo.
- çunkî eger qeçî bibîyay se, mi do yan zewajdê ci rê yan eskereyda ci rê, yan mektebdê ci rê xerc bikerdê.

### Topic 6 | keşıf, terefê, biyo, ra, de
- de terefê i ra keşıf biyo.
- de terefê i ra keşıf biyo.

### Topic 7 | ez, nêkenê, mi, nêzana, ma
- la merdimo ke mirdîya xo nêwano nêeşkeno binuso.
- çend gamî ravêr şî, labelê nêşkîya xo biresno ereba.

### Topic 8 | kanalizasyoni, şebekey, sistemê, awe, ratneyao
- blanzée de şebekey awe esto û sistemê kanalizasyoni vıraziyao.
- valognes de şebekey awe esto û sistemê kanalizasyoni ratneyao.

### Topic 9 | estareyanê, komê, neweyê, katalogê, cısım
- no cısım katalogê neweyê pêroyi de, komê estareyanê miyan de ca gêno.
- no cısım katalogê neweyê pêroyi de, komê estareyanê miyan de ca gêno.

### Topic 10 | tirkî, tirkîya, îstanbul, stanbul, 975
- there is no use for this since everybody knows turkish?
- la her kesî reyde tirkî qisey kena.

### Topic 11 | philadelphia, pittsburgh, john, william, james
- necmettin erbakan (b.
- mason jr., d.

### Topic 12 | katalogê, neweyê, cısım, pêroyi, gêno
- no cısım katalogê neweyê pêroyi de ca gêno.
- no cısım katalogê neweyê pêroyi de ca gêno.

### Topic 13 | kurdî, kurdîstanî, şarê, rayberê, abdullah
- yanî ne kurd esto ne kurdî, herinda înan de "kürt kökenli" û "kürt kökenliler" estê.
- mît başûrê kurdîstanî de rehet têgêreno.

### Topic 14 | elektrik, internet, anciyao, kanalizasyoni, şebekey
- brûlon de şebekey awe esto, sistemê kanalizasyoni, elektrik û internet anciyao.
- saulce-sur-rhône de şebekey awe esto, sistemê kanalizasyoni, elektrik û internet anciyao.

## Case Study 1 — Aynı Tema, Çok-Dilli (CV)

Amaç: CV konuşmalarında aynı temayı TR/KMR/ZZA için karşılaştırmak.
Yöntem: CV/both varyantı topic temsilcileri ve KeyBERT listeleri incelendi.

Nicel özet:
- KeyBERT: J(text,cv) ~ 0 → kaynaklar arası tamamlayıcılık yüksek.
- Coverage: cv/both’ta KeyBERT kapsamı yüksek.

Nitel referanslar:
- TR (both): reports/analysis/representatives_tr_both_top15.md
- KMR (both): reports/analysis/representatives_kmr_both_top15.md
- ZZA (both): reports/analysis/representatives_zza_both_top15.md

Kısa yorum:
- (Örn.) Spor/siyaset/yerleşim temaları ortak; diakritik/yerel adlandırmalar ve kalıp kullanımlarında dil-özgü farklar belirgin.

## Case Study 2 — Aynı Konu, Çok Konuşmacı (Text)

Amaç: Tek bir konu (“göç”/“eğitim”) etrafında farklı paragrafların etkisini görmek.
Yöntem: Wiki/Zazagorani text varyantı temsilciler ve KeyBERT listeleri incelendi.

Nicel özet:
- YAKE (unigram) varyantlardan az etkilenir; KeyBERT çok-kelimeli, bağlama duyarlı.

Nitel referanslar:
- TR reps (text/both): reports/analysis/representatives_tr_both_top15.md
- KMR reps (text/both): reports/analysis/representatives_kmr_both_top15.md
- ZZA reps (text/both): reports/analysis/representatives_zza_both_top15.md

Kısa yorum:
- (Örn.) Çekirdek düğümler sabit; çevresel düğümler dil/lehçe-özgü kültürel işaretler taşıyor.

## Case3 Original Vs Mt

<!-- UPDATE (MT Pilot):
     NLLB-200 (600M, fp16, beam=4) ile kmr_Latn->tur_Latn ve diq_Latn->tur_Latn 300+300 hip üretildi.
     Kaynaklar mojibake temizlendi (*.fixed.src); çıktı dosyaları *.fixed.hyp.
     TR referans segmentleri YOK => BLEU/ChrF ve topic/keyword drift analizi BU SÜRÜMDE BLOKELENDİ.
     Devam koşulu: hizalı TR referansları sağla, sonra mt_pilot_quality.py çalıştır. -->
     
### Case Study 3 — Orijinal vs Makine Çevirisi (DEFERRED)

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

## Case Study 4 — Speech (CV) vs Text

### TR

- KeyBERT:
  - J(text,cv): 0.0
  - Coverage% → text: 16.5 | cv: 85.5 | both: 15.5
  - Yorum: text–cv kesişimi çok düşük; cv/both kapsamı yüksek (konuşma verisinde terimler geçiyor).

- YAKE:
  - J(text,cv): 0.156
  - Coverage% → text: 100.0 | cv: 100.0 | both: 100.0
  - Yorum: Unigram doğası gereği daha stabil; tamamlayıcılığı KeyBERT daha iyi yansıtıyor.

### KMR

- KeyBERT:
  - J(text,cv): 0.0
  - Coverage% → text: 30.5 | cv: 99.0 | both: 100.0
  - Yorum: text–cv kesişimi çok düşük; cv/both kapsamı yüksek (konuşma verisinde terimler geçiyor).

- YAKE:
  - J(text,cv): 0.282
  - Coverage% → text: 100.0 | cv: 99.5 | both: 100.0
  - Yorum: Unigram doğası gereği daha stabil; tamamlayıcılığı KeyBERT daha iyi yansıtıyor.

### ZZA

- KeyBERT:
  - J(text,cv): 0.0
  - Coverage% → text: 31.5 | cv: 98.0 | both: 98.0
  - Yorum: text–cv kesişimi çok düşük; cv/both kapsamı yüksek (konuşma verisinde terimler geçiyor).

- YAKE:
  - J(text,cv): 0.216
  - Coverage% → text: 100.0 | cv: 100.0 | both: 100.0
  - Yorum: Unigram doğası gereği daha stabil; tamamlayıcılığı KeyBERT daha iyi yansıtıyor.

Kaynaklar:
- [reports/analysis/keyword_overlap.md](reports/analysis/keyword_overlap.md)
- [reports/analysis/keyword_coverage.md](reports/analysis/keyword_coverage.md)

## KG Examples — Both Top15 (TR/KMR/ZZA)

| Lang | Nodes | Edges | WeightedSum | AvgWeightedDeg | Density | AvgEdgeW | MedDeg | MaxDeg | MinDeg |
|------|-------|-------|-------------|----------------|---------|----------|--------|--------|--------|
| tr | 73 | 150 | 150 | 4.11 | 0.057 | 1.00 | 4 | 8 | 4 |
| kmr | 66 | 150 | 150 | 4.55 | 0.070 | 1.00 | 4.0 | 12 | 4 |
| zza | 65 | 142 | 150 | 4.62 | 0.068 | 1.06 | 4 | 8 | 4 |

Açıklama:
- Nodes: Terim çeşitliliği.
- Edges: Birlikte görünen terim çiftleri.
- WeightedSum: Kenar ağırlık toplamı (konu sayısı üzerinden).
- AvgWeightedDeg: Ortalama ağırlıklı derece.
- Density: Olası bağlantıların kullanım oranı.
- AvgEdgeW: Kenar başına tekrar.
- Mode: top15 (top15 = sadece trimmed reps; full = tüm topics reps).

## KG Examples — Both FULL (TR/KMR/ZZA)

| Lang | Nodes | Edges | WeightedSum | AvgWeightedDeg | Density | AvgEdgeW | MedDeg | MaxDeg | MinDeg |
|------|-------|-------|-------------|----------------|---------|----------|--------|--------|--------|
| tr | 535 | 1130 | 1140 | 4.26 | 0.008 | 1.01 | 4 | 16 | 4 |
| kmr | 505 | 1155 | 1180 | 4.67 | 0.009 | 1.02 | 4 | 28 | 4 |
| zza | 444 | 1119 | 1290 | 5.81 | 0.011 | 1.15 | 4.0 | 56 | 4 |

Açıklama:
- Nodes: Terim çeşitliliği.
- Edges: Birlikte görünen terim çiftleri.
- WeightedSum: Kenar ağırlık toplamı (konu sayısı üzerinden).
- AvgWeightedDeg: Ortalama ağırlıklı derece.
- Density: Olası bağlantıların kullanım oranı.
- AvgEdgeW: Kenar başına tekrar.
- Mode: full (top15 = sadece trimmed reps; full = tüm topics reps).

## KG Interpretation (Top15 vs Full)

Özet:
- Ölçek artışıyla (Node 7–8x) seyrekleşme (density ↓) normal; mini KG erken kavramsal çekirdek görüntüsü veriyor.
- ZZA full grafikte hub yoğunluğu (max degree 56) → kültürel/yerel ad kümeleri merkezî bağlayıcı rol üstleniyor.
- Ortalama edge ağırlığı ≈1 → tekrar oranı düşük; PMI tabanlı genişletme önerilir.
- KMR’de hub artışı (12→28) çekirdek coğrafya / kimlik terimlerinin köprü rolünü gösteriyor.
- Full KG, entity linking & bipartite modülerlik analizleri için zengin topolojik temel sunuyor.

Ek: Ayrıntılı ağırlık dağılımları için *_kg_*_(pmi|tfidf)_stats.json dosyalarına bakınız.

## Project Execution Summary

Bu belge sprint bazlı ilerlemeyi, test case (TC) kapsamını, ablation setlerini, case study durumunu ve ileri iş kalemlerini izlenebilir biçimde özetler.

### 1. Sprint Templatı ve Gerçekleşenler

| Sprint | Odak | Ana Çıktılar | İlgili Artefaktlar |
|--------|------|--------------|--------------------|
| S1 | ASR Baseline | Whisper (medium/large) valid/test WER/CER, bias & beam aramaları | reports/asr_*.json, asr_summary_*.md |
| S2 | Cross-Dialect & Model Seçimi | ZZA/KMR dil zorluk analizi, bias etkisi, decode varyantları | confusion_*.json, asr_compare_* |
| S3 | Text Ingest & N-gram | Wiki + Zazagorani çekme, temizleme, n-gram istatistikleri | reports/text_stats/* |
| S4 | Normalization & Final Corpora | Unicode NFKC, lowercase, segmentasyon, deduplikasyon | data/processed/*.parquet, scripts/utils |
| S5 | Topic & Keywords + Ablations + Case Studies + Mini KG | BERTopic varyantları, KeyBERT/YAKE, coherence/overlap/coverage, reps, KG, case1/2/4 | reports/analysis/*.md |

### 2. Core Test Cases

| TC | Tanım | Durum | Kanıt / Dosyalar |
|----|------|-------|------------------|
| TC-1 | Çok-dilli ASR değerlendirme (WER/CER/RTF) | Tamamlandı | asr_*summary*.md, confusion_*.json |
| TC-2 | Cross-dialect decoding etkisi | Tamamlandı | confusion_*_TRdecode.json, bias varyantları |
| TC-3 | ASR + LM Fusion (shallow) | Deferred | future_work.md (Fusion bölümü) |
| TC-4 | Topic & Keyword Extraction (çok-kaynak) | Tamamlandı | topic_coherence.md, keyword_overlap.md, keyword_coverage.md |

### 3. Ablations ve Analizler

| Ablation | Amaç | Metod / Metrik | Çıktı |
|----------|------|----------------|-------|
| Topic Coherence | Varyant kalite karşılaştırma | c_npmi, c_v, outlier% | topic_coherence.md |
| Keyword Overlap | Kaynak tamamlayıcılık | Jaccard, new_in_both% | keyword_overlap.md |
| Keyword Coverage | Terim doküman içi kapsama | covered%, avg_doc_coverage | keyword_coverage.md |
| Representatives (Interpretability) | Nitel doğrulama | Top terimler + örnek cümle | representatives_*_both_top15.md |
| Mini KG | Kavramsal köprü yoğunluğu | Co-occurrence graph stats | kg_examples_all.md |
| (Opsiyonel) Full KG | Tüm topic’lerle geniş grafik | density/degree dağılım | (henüz yok → future_work.md) |

### 4. Case Studies

| Case | Başlık | Durum | Dosya |
|------|--------|-------|-------|
| CS-1 | Aynı Tema, Çok-Dilli (CV) | Tamamlandı | case1_same_theme_multi_dialect.md |
| CS-2 | Aynı Konu, Çok Konuşmacı (Text) | Tamamlandı | case2_same_topic_multi_speakers.md |
| CS-3 | Orijinal vs MT | Deferred | case3_original_vs_mt.md |
| CS-4 | Speech (CV) vs Text | Tamamlandı | case4_speech_vs_text.md |

### 5. Repro / İzlenebilirlik Referansları

- Ortam: `env.txt`, `env_freeze.txt`, `versions.json`, `git_commit.txt`
- Komut Özetleri: future_work.md (Repro bölümü)
- Veri Kaynakları: `data/raw/commonvoice/*`, `data/raw/wiki/*`, `data/raw/zazagorani/*`
- Üretilmiş Tablolar: `thesis_tables.md` (konsolidasyon)

### 6. Riskler ve Sınırlar

| Alan | Risk | Etki | Karşılık |
|------|------|------|----------|
| MT Kalitesi (CS-3) | Düşük ZZA çeviri kalitesi | Yanıltıcı drift ölçümleri | Pilot + kalite eşiği (ChrF>40) |
| Fusion Gecikmesi | LM eğitimi zaman maliyeti | WER iyileştirmesi kaçırıldı | Gelecek sprint planı |
| Entity Linking | Çok-dilli ad varyantları | KG bağlamsal zayıflık | Wikidata tabanlı eşleme planlandı |
| Full KG Boyutu | Hafıza & karmaşıklık | Yürütme süresi artışı | top15 ön-filtre → sonra full deney |

### 7. Future Work (Özet)

- Shallow Fusion (KenLM 3/5-gram, λ grid)
- Full-topic + bipartite KG
- Entity Linking (Wikidata Q-ID eşleşme)
- Edge PMI / TF-IDF ağırlıkları
- MT vs Original Topic/Keyword Drift (CS-3 tam uygulama)
- ASR fine-tuning (lehçe uyarlama)
- Gelişmiş deduplikasyon (LSH + fuzzy hashing)

### 8. Kapanış

Çok-kaynaklı (text + CV) yaklaşım; overlap (düşük Jaccard) ve coverage (yüksek cv kapsamı) metrikleriyle tamamlayıcılığı gösterdi; mini KG köprü terim yoğunluğu dil/lehçe farklarını nicelleştirdi; deferred alanlar future_work.md’de metodoloji ile kayıt altına alındı.
