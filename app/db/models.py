from datetime import datetime, timezone

from sqlalchemy import text

from app.db.database import get_db


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
    topic_id,
    agent_id,
    title,
    summary,
    source_url,
    discovered_at,
    status,
    rejection_reason=None,
):
    with get_db() as conn:
        conn.execute(
            text(
                """
                INSERT INTO topics (
                    topic_id, agent_id, title, summary, source_url,
                    discovered_at, status, rejection_reason
                )
                VALUES (
                    :topic_id, :agent_id, :title, :summary, :source_url,
                    :discovered_at, :status, :rejection_reason
                )
                """
            ),
            {
                "topic_id": topic_id,
                "agent_id": agent_id,
                "title": title,
                "summary": summary,
                "source_url": source_url,
                "discovered_at": discovered_at,
                "status": status,
                "rejection_reason": rejection_reason,
            },
        )


def insert_post(id, agent_id, topic_id, text_content, rationale, sources, created_at):
    with get_db() as conn:
        conn.execute(
            text(
                """
                INSERT INTO posts (id, agent_id, topic_id, text, rationale, sources, created_at)
                VALUES (:id, :agent_id, :topic_id, :text, :rationale, :sources, :created_at)
                """
            ),
            {
                "id": id,
                "agent_id": agent_id,
                "topic_id": topic_id,
                "text": text_content,
                "rationale": rationale,
                "sources": sources,
                "created_at": created_at,
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
        return [dict(row._mapping) for row in result]


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
        return [dict(row._mapping) for row in result]
