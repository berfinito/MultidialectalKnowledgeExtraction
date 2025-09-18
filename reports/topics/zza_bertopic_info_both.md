# BERTopic run (zza)

- docs: 50000
- device: cuda
- params: {"language": "multilingual", "min_topic_size": 50, "calculate_probabilities": true, "verbose": true, "seed": 42, "umap": {"n_neighbors": 15, "n_components": 5, "min_dist": 0.0, "metric": "cosine", "random_state": 42}, "hdbscan": {"min_cluster_size": null, "min_samples": null}, "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "sources": ["cv", "text"], "cv_weight": 2}