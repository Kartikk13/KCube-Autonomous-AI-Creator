from __future__ import annotations

import re
from html import unescape

import httpx

REQUEST_TIMEOUT = 10.0
MAX_RESEARCH_CHARS = 4000

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    cleaned = unescape(_TAG_RE.sub(" ", text or ""))
    return re.sub(r"\s+", " ", cleaned).strip()


def _truncate_text(text: str, max_chars: int = MAX_RESEARCH_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


async def research_topic(topic: dict) -> dict:
    source_url = topic["source_url"]
    result = {
        **topic,
        "sources": [source_url],
    }

    try:
        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "KCube-Autonomous-AI-Creator/1.0"},
        ) as client:
            response = await client.get(source_url)
            response.raise_for_status()
            plain_text = _strip_html(response.text)
            result["research_context"] = _truncate_text(plain_text)
    except Exception:
        result["research_context"] = topic.get("summary", "")

    return result
