from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from html import unescape
from xml.etree import ElementTree

import httpx

HN_AI_RSS_URL = "https://hnrss.org/frontpage?q=AI"
ARXIV_CS_AI_RECENT_URL = "https://arxiv.org/list/cs.AI/recent"
MAX_TOPICS = 8
REQUEST_TIMEOUT = 20.0

_ARXIV_ENTRY_RE = re.compile(
    r'<dt>[\s\S]*?href\s*=\s*"/abs/(\d+\.\d+)"[\s\S]*?</dt>\s*'
    r"<dd>\s*<div class='meta'>([\s\S]*?)</div>\s*</dd>",
    re.IGNORECASE,
)
_TAG_RE = re.compile(r"<[^>]+>")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def _strip_html(text: str) -> str:
    cleaned = unescape(_TAG_RE.sub(" ", text or ""))
    return re.sub(r"\s+", " ", cleaned).strip()


def _interest_keywords(persona: dict) -> list[str]:
    keywords: list[str] = []
    for interest in persona.get("stable_interests") or []:
        phrase = str(interest).lower().strip()
        if not phrase:
            continue
        keywords.append(phrase)
        for word in re.split(r"[\s\-/]+", phrase):
            if len(word) >= 3:
                keywords.append(word)
    return list(dict.fromkeys(keywords))


def _interest_score(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword in lowered)


def _parse_hn_rss(xml_text: str, discovered_at: str) -> list[dict]:
    root = ElementTree.fromstring(xml_text)
    items: list[dict] = []

    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = _strip_html(item.findtext("description") or "")

        if not title or not link:
            continue

        items.append(
            {
                "title": title,
                "summary": description or title,
                "source_url": link,
                "discovered_at": discovered_at,
            }
        )

    return items


def _parse_arxiv_recent(html: str, discovered_at: str) -> list[dict]:
    items: list[dict] = []

    for paper_id, meta_block in _ARXIV_ENTRY_RE.findall(html):
        title_match = re.search(
            r"list-title mathjax'>([\s\S]*?)</div>",
            meta_block,
            re.IGNORECASE,
        )
        if not title_match:
            continue

        title = _strip_html(title_match.group(1))
        title = re.sub(r"^Title:\s*", "", title, flags=re.IGNORECASE).strip()
        if not title:
            continue

        authors_match = re.search(
            r"<div class='list-authors'>([\s\S]*?)</div>",
            meta_block,
            re.IGNORECASE,
        )
        subjects_match = re.search(
            r"<div class='list-subjects'>([\s\S]*?)</div>",
            meta_block,
            re.IGNORECASE,
        )

        summary_parts: list[str] = []
        if authors_match:
            authors = _strip_html(authors_match.group(1))
            authors = re.sub(r"^Authors:\s*", "", authors, flags=re.IGNORECASE).strip()
            if authors:
                summary_parts.append(f"Authors: {authors}")
        if subjects_match:
            subjects = _strip_html(subjects_match.group(1))
            subjects = re.sub(r"^Subjects:\s*", "", subjects, flags=re.IGNORECASE).strip()
            if subjects:
                summary_parts.append(f"Subjects: {subjects}")

        items.append(
            {
                "title": title,
                "summary": "; ".join(summary_parts) or title,
                "source_url": f"https://arxiv.org/abs/{paper_id}",
                "discovered_at": discovered_at,
            }
        )

    return items


def _select_topics(items: list[dict], persona: dict) -> list[dict]:
    if not items:
        return []

    keywords = _interest_keywords(persona)
    ranked = sorted(
        items,
        key=lambda item: _interest_score(
            f"{item['title']} {item['summary']}",
            keywords,
        ),
        reverse=True,
    )
    return ranked[:MAX_TOPICS]


async def _fetch_hn_topics(client: httpx.AsyncClient, discovered_at: str) -> list[dict]:
    response = await client.get(HN_AI_RSS_URL)
    response.raise_for_status()
    return _parse_hn_rss(response.text, discovered_at)


async def _fetch_arxiv_topics(client: httpx.AsyncClient, discovered_at: str) -> list[dict]:
    response = await client.get(ARXIV_CS_AI_RECENT_URL)
    response.raise_for_status()
    return _parse_arxiv_recent(response.text, discovered_at)


async def discover_topics(persona: dict) -> list[dict]:
    try:
        discovered_at = _utc_now_iso()
        items: list[dict] = []

        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "KCube-Autonomous-AI-Creator/1.0"},
        ) as client:
            results = await asyncio.gather(
                _fetch_hn_topics(client, discovered_at),
                _fetch_arxiv_topics(client, discovered_at),
                return_exceptions=True,
            )

            for result in results:
                if isinstance(result, Exception):
                    continue
                items.extend(result)

        return _select_topics(items, persona)
    except Exception:
        return []
