.PHONY: prepare ingest_cv

prepare:
\t@echo "Preparing folders..."
\t@python -c "from mdke.utils.io import Paths, ensure_dirs; \
from pathlib import Path; \
paths=Paths(Path('data/raw'),Path('data/interim'),Path('data/processed'),Path('reports')); \
ensure_dirs(paths); print('OK')"

# örnek: make ingest_cv LANG=kmr
ingest_cv:
\t@echo "Ingest Common Voice (local) for LANG=$(LANG)"
\t@python -m mdke.data.ingest_commonvoice --mode local --lang $(LANG)
