# Sprint 4 Summary (normh)

## TR

- source wiki: 2501560
- source zazagorani: NA
- source total: 2501560
- paragraphs (normh): 2438107
- post-filter clean: 2435911 (drop=2196, retain=99.91%)
- section nonav: 2435911 (retain=100.00%)
- dedup: 2435179 (drop=732, retain=99.97%)
- sentences: 7323391
- overall retention: 97.35%
- n-grams (uni): reports\ngrams\tr_normh_clean_nonav_dedup_unigram.txt
- n-grams (bi):  reports\ngrams\tr_normh_clean_nonav_dedup_bigram.txt

## KMR

- source wiki: 179004
- source zazagorani: NA
- source total: 179004
- paragraphs (normh): 167960
- post-filter clean: 167777 (drop=183, retain=99.89%)
- section nonav: 167777 (retain=100.00%)
- dedup: 167737 (drop=40, retain=99.98%)
- sentences: 370211
- overall retention: 93.71%
- n-grams (uni): reports\ngrams\kmr_normh_clean_nonav_dedup_unigram.txt
- n-grams (bi):  reports\ngrams\kmr_normh_clean_nonav_dedup_bigram.txt

## ZZA

- source wiki: 93236
- source zazagorani: 4855
- source total: 98091
- paragraphs (normh): 78189
- post-filter clean: 78141 (drop=48, retain=99.94%)
- section nonav: 78141 (retain=100.00%)
- dedup: 78098 (drop=43, retain=99.94%)
- sentences: 268111
- overall retention: 79.62%
- n-grams (uni): reports\ngrams\zza_normh_clean_nonav_dedup_unigram.txt
- n-grams (bi):  reports\ngrams\zza_normh_clean_nonav_dedup_bigram.txt

## Final artefaktlar

### TR

- Paragraflar (final): `data/processed/text_corpus_tr_final.parquet`
- Cümleler (final): `data/processed/text_sentences_tr_final.parquet`
- Düz metin export: `reports/exports/sentences_tr_final.txt`

### KMR

- Paragraflar (final): `data/processed/text_corpus_kmr_final.parquet`
- Cümleler (final): `data/processed/text_sentences_kmr_final.parquet`
- Düz metin export: `reports/exports/sentences_kmr_final.txt`

### ZZA

- Paragraflar (final): `data/processed/text_corpus_zza_final.parquet`
- Cümleler (final): `data/processed/text_sentences_zza_final.parquet`
- Düz metin export: `reports/exports/sentences_zza_final.txt`
