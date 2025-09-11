"""
mdke.text: metin kaynak ingest ve yardımcıları.
Alt modüller:
- ingest_wikipedia
- ingest_zazagorani
- transliterate_kmrzza
"""

# Not: build_corpus ayrı bir CLI (scripts/text_build_corpus.py), paket modülü değildir.
from . import ingest_wikipedia
from . import ingest_zazagorani
from . import transliterate_kmrzza

__all__ = ["ingest_wikipedia", "ingest_zazagorani", "transliterate_kmrzza"] 