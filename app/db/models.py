import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import text

from app.db.database import get_db


def _serialize_embedding(embedding: list[float] | None) -> bytes | None:
    if embedding is None:
        return None
    return json.dumps(embedding).encode("utf-8")


def _deserialize_embedding(raw) -> list[float] | None:
    if raw is None:
        return None
    if isinstance(raw, memoryview):
        raw = raw.tobytes()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return None
        if isinstance(parsed, list):
            return [float(value) for value in parsed]
    return None


def _row_with_embedding(row) -> dict:
    data = dict(row._mapping)
    data["embedding"] = _deserialize_embedding(data.get("embedding"))
    return data


def insert_agent(agent_id, persona_name, persona_domain, persona_voice):
    initialized_at = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        conn.execute(
            text(
                """
                INSERT INTO agent (agent_id, persona_name, persona_domain, persona_voice, initialized_at)
                VALUES (:agent_id, :persona_name, :persona_domain, :persona_voice, :initialized_at)
                """
            ),
            {
                "agent_id": agent_id,
                "persona_name": persona_name,
                "persona_domain": persona_domain,
                "persona_voice": persona_voice,
                "initialized_at": initialized_at,
            },
        )


def insert_topic(
    agent_id: str,
    topic: dict,
    embedding: list[float] | None = None,
) -> str:
    topic_id = str(uuid.uuid4())
    discovered_at = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        conn.execute(
            text(
                """
                INSERT INTO topics (
                    topic_id, agent_id, title, summary, source_url,
                    discovered_at, status, rejection_reason, embedding
                )
                VALUES (
                    :topic_id, :agent_id, :title, :summary, :source_url,
                    :discovered_at, :status, :rejection_reason, :embedding
                )
                """
            ),
            {
                "topic_id": topic_id,
                "agent_id": agent_id,
                "title": topic.get("title", ""),
                "summary": topic.get("summary", ""),
                "source_url": topic.get("source_url", ""),
                "discovered_at": discovered_at,
                "status": "published",
                "rejection_reason": None,
                "embedding": _serialize_embedding(embedding),
            },
        )
    return topic_id


def insert_post(
    post_id: str,
    agent_id: str,
    topic_id: str,
    text_content: str,
    rationale: str,
    sources,
    embedding: list[float] | None = None,
):
    created_at = datetime.now(timezone.utc).isoformat()
    if isinstance(sources, list):
        sources = json.dumps(sources)
    with get_db() as conn:
        conn.execute(
            text(
                """
                INSERT INTO posts (
                    id, agent_id, topic_id, text, rationale, sources,
                    created_at, embedding
                )
                VALUES (
                    :id, :agent_id, :topic_id, :text, :rationale, :sources,
                    :created_at, :embedding
                )
                """
            ),
            {
                "id": post_id,
                "agent_id": agent_id,
                "topic_id": topic_id,
                "text": text_content,
                "rationale": rationale,
                "sources": sources,
                "created_at": created_at,
                "embedding": _serialize_embedding(embedding),
            },
        )


def insert_editorial_log(
    agent_id: str,
    candidate: dict,
    decision: str,
    reasoning: str,
) -> None:
    logged_at = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        conn.execute(
            text(
                """
                INSERT INTO editorial_log (
                    agent_id, topic_id, decision, reasoning, logged_at
                )
                VALUES (
                    :agent_id, :topic_id, :decision, :reasoning, :logged_at
                )
                """
            ),
            {
                "agent_id": agent_id,
                "topic_id": candidate.get("topic_id"),
                "decision": decision,
                "reasoning": reasoning,
                "logged_at": logged_at,
            },
        )


def get_posts_for_feed(agent_id):
    with get_db() as conn:
        result = conn.execute(
            text(
                """
                SELECT id, agent_id, topic_id, text, rationale, sources, created_at, embedding
                FROM posts
                WHERE agent_id = :agent_id
                ORDER BY created_at DESC
                """
            ),
            {"agent_id": agent_id},
        )
        return [_row_with_embedding(row) for row in result]


def get_recent_posts(agent_id, limit=20):
    with get_db() as conn:
        result = conn.execute(
            text(
                """
                SELECT id, agent_id, topic_id, text, rationale, sources, created_at, embedding
                FROM posts
                WHERE agent_id = :agent_id
                ORDER BY created_at DESC
                LIMIT :limit
                """
            ),
            {"agent_id": agent_id, "limit": limit},
        )
        return [_row_with_embedding(row) for row in result]


def get_recent_topics(agent_id, limit=20):
    with get_db() as conn:
        result = conn.execute(
            text(
                """
                SELECT
                    topic_id, agent_id, title, summary, source_url,
                    discovered_at, status, rejection_reason, embedding
                FROM topics
                WHERE agent_id = :agent_id
                ORDER BY discovered_at DESC
                LIMIT :limit
                """
            ),
            {"agent_id": agent_id, "limit": limit},
        )
        return [_row_with_embedding(row) for row in result]
