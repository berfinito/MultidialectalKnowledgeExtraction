# BERTopic run (tr)

- docs: 50000
- device: cuda
- params: {"language": "multilingual", "min_topic_size": 50, "calculate_probabilities": true, "verbose": true, "seed": 42, "umap": {"n_neighbors": 30, "n_components": 10, "min_dist": 0.0, "metric": "cosine", "random_state": 42}, "hdbscan": {"min_cluster_size": 50, "min_samples": 10}, "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "sources": ["cv", "text"], "cv_weight": 2}