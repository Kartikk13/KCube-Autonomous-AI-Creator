from __future__ import annotations

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed(text: str) -> list[float]:
    vector = _get_model().encode(text or "", normalize_embeddings=True)
    return vector.tolist()


def cosine_sim(a, b) -> float:
    a_arr = np.asarray(a, dtype=float)
    b_arr = np.asarray(b, dtype=float)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    similarity = float(np.dot(a_arr, b_arr) / (norm_a * norm_b))
    return max(0.0, min(1.0, similarity))
