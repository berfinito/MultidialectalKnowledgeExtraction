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

.PHONY: final

final:
\tpython scripts/materialize_final_aliases.py --config configs/experiment.yaml
\tpython scripts/sprint4_summarize.py --config configs/experiment.yaml --tag_base normh
\tpython scripts/sprint4_make_markdown.py --config configs/experiment.yaml
\t@echo "Final artefaktlar hazır. Rapor: reports/sprint-4-summary.{json,md}"



.PHONY: kg_centrality kg_plots kg_exports final_v1

kg_centrality:
\tpython scripts/kg_centrality_analysis.py --patterns "reports/analysis/*_kg_full_*.tsv" "reports/analysis/*_kg_top15_*.tsv"

kg_plots:
\tpython scripts/plot_kg.py --tsv reports/analysis/tr_kg_full_pmi.tsv --top_edges 200 --out reports/analysis/plots/tr_kg_full_pmi_top200.png
\tpython scripts/plot_kg.py --tsv reports/analysis/kmr_kg_full_pmi.tsv --top_edges 200 --out reports/analysis/plots/kmr_kg_full_pmi_top200.png
\tpython scripts/plot_kg.py --tsv reports/analysis/zza_kg_full_pmi.tsv --top_edges 200 --out reports/analysis/plots/zza_kg_full_pmi_top200.png
\tpython scripts/plot_kg.py --tsv reports/analysis/tr_kg_top15_tfidf.tsv --top_edges 150 --out reports/analysis/plots/tr_kg_top15_tfidf_top150.png
\tpython scripts/plot_kg.py --tsv reports/analysis/kmr_kg_top15_tfidf.tsv --top_edges 150 --out reports/analysis/plots/kmr_kg_top15_tfidf_top150.png
\tpython scripts/plot_kg.py --tsv reports/analysis/zza_kg_top15_tfidf.tsv --top_edges 150 --out reports/analysis/plots/zza_kg_top15_tfidf_top150.png

kg_exports:
\tpython scripts/export_kg.py --tsv reports/analysis/tr_kg_full_pmi.tsv --out reports/analysis/exports/tr_kg_full_pmi.gexf
\tpython scripts/export_kg.py --tsv reports/analysis/kmr_kg_full_pmi.tsv --out reports/analysis/exports/kmr_kg_full_pmi.gexf
\tpython scripts/export_kg.py --tsv reports/analysis/zza_kg_full_pmi.tsv --out reports/analysis/exports/zza_kg_full_pmi.gexf
\tpython scripts/export_kg.py --tsv reports/analysis/tr_kg_top15_tfidf.tsv --out reports/analysis/exports/tr_kg_top15_tfidf.graphml
\tpython scripts/export_kg.py --tsv reports/analysis/kmr_kg_top15_tfidf.tsv --out reports/analysis/exports/kmr_kg_top15_tfidf.graphml
\tpython scripts/export_kg.py --tsv reports/analysis/zza_kg_top15_tfidf.tsv --out reports/analysis/exports/zza_kg_top15_tfidf.graphml

final_v1:
\t@echo "Generating final summary..."
\t@powershell -NoProfile -Command "if (-Not (Test-Path 'reports/analysis/final_summary.md')) { New-Item -ItemType File 'reports/analysis/final_summary.md' | Out-Null }"
\tpython -c "print('See reports/analysis/final_summary.md')"
\t$(MAKE) kg_centrality
\t$(MAKE) kg_plots
\t$(MAKE) kg_exports
\tpytest -q
\t@echo "v1 finalized. See README and reports/analysis/final_summary.md"