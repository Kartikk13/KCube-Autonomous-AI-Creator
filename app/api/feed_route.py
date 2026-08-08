import json
from typing import Optional

from fastapi import APIRouter, Query

from app.db.models import get_posts_for_feed

router = APIRouter()


def _parse_sources(sources_raw) -> list:
    if not sources_raw:
        return []
    try:
        parsed = json.loads(sources_raw)
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


@router.get("/api/agent/feed")
def get_feed(agentId: Optional[str] = Query(default=None)):
    if not agentId:
        return {"posts": []}

    rows = get_posts_for_feed(agentId)
    posts = [
        {
            "id": row["id"],
            "createdAt": row["created_at"],
            "text": row["text"],
            "rationale": row["rationale"],
            "sources": _parse_sources(row["sources"]),
        }
        for row in rows
    ]
    return {"posts": posts}
