"""
IO utilities and small helpers:

- Paths dataclass and ensure_dirs() to manage data/reports folders.
- YAML loader and JSONL read/write with UTF-8.
- Seed setter (numpy/torch/cudnn) for reproducibility.
- Lightweight logger factory.

Used by: ASR inference, KG scripts, and many pipeline steps.
"""
from __future__ import annotations
import json
import logging
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Dict, Any, Generator

import numpy as np
import yaml

@dataclass
class Paths:
    """Standard project paths bundle."""
    raw: Path
    interim: Path
    processed: Path
    reports: Path

def ensure_dirs(paths: Paths) -> None:
    """Create all folders in Paths if missing (idempotent)."""
    for p in [paths.raw, paths.interim, paths.processed, paths.reports]:
        p.mkdir(parents=True, exist_ok=True)


def load_yaml(path: str | Path) -> Dict[str, Any]:
    """Load a YAML file into a Python dict with UTF-8 decoding."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_jsonl(items: Iterable[Dict[str, Any]], path: str | Path) -> None:
    """Write an iterable of dicts to JSONL file (UTF-8, one record per line)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

def read_jsonl(path: str | Path) -> Generator[Dict[str, Any], None, None]:
    """Yield dict records from a JSONL file (UTF-8). Skips empty lines."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def set_seed(seed: int) -> None:
    """
    Set RNG seeds for reproducibility across Python, numpy and torch (CPU/GPU),
    and enforce deterministic cudnn behavior.
    """
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def get_logger(name: str = "mdke", level: int = logging.INFO) -> logging.Logger:
    """Get a configured stream logger with a simple timestamped format."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        fmt = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    return logger
