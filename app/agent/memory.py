from __future__ import annotations

from app.db.models import get_recent_topics
from app.services.embeddings import cosine_sim


def is_duplicate(
    candidate_embedding: list[float],
    existing_embeddings: list[list[float]],
    threshold: float = 0.87,
) -> bool:
    for existing in existing_embeddings:
        if not existing:
            continue
        if cosine_sim(candidate_embedding, existing) >= threshold:
            return True
    return False


def load_recent(agent_id: str, limit: int = 20) -> list[dict]:
    return get_recent_topics(agent_id, limit=limit)
