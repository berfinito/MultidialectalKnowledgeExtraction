# Case Study 4 — Speech (CV) vs Text

## TR

- KeyBERT:
  - J(text,cv): 0.0
  - Coverage% → text: 16.5 | cv: 85.5 | both: 15.5
  - Yorum: text–cv kesişimi çok düşük; cv/both kapsamı yüksek (konuşma verisinde terimler geçiyor).

- YAKE:
  - J(text,cv): 0.156
  - Coverage% → text: 100.0 | cv: 100.0 | both: 100.0
  - Yorum: Unigram doğası gereği daha stabil; tamamlayıcılığı KeyBERT daha iyi yansıtıyor.

## KMR

- KeyBERT:
  - J(text,cv): 0.0
  - Coverage% → text: 30.5 | cv: 99.0 | both: 100.0
  - Yorum: text–cv kesişimi çok düşük; cv/both kapsamı yüksek (konuşma verisinde terimler geçiyor).

- YAKE:
  - J(text,cv): 0.282
  - Coverage% → text: 100.0 | cv: 99.5 | both: 100.0
  - Yorum: Unigram doğası gereği daha stabil; tamamlayıcılığı KeyBERT daha iyi yansıtıyor.

## ZZA

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