from __future__ import annotations

import json
import re

from app.services.gemini_client import generate as gemini_generate
from app.services.openrouter_client import generate as openrouter_generate

_JSON_OBJECT_RE = re.compile(r"\{[\s\S]*\}")
_FENCE_PREFIX_RE = re.compile(r"^```(?:json)?\s*", re.IGNORECASE)
_FENCE_SUFFIX_RE = re.compile(r"\s*```$")


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    text = _FENCE_PREFIX_RE.sub("", text, count=1)
    text = _FENCE_SUFFIX_RE.sub("", text, count=1)
    return text.strip()


def _render_system_prompt(persona: dict) -> str:
    voice_rules = "; ".join(persona.get("voice_rules") or [])
    interests = ", ".join(persona.get("stable_interests") or [])
    standards = "; ".join(persona.get("publishing_standards") or [])
    name = persona.get("name", "Agent")
    domain = persona.get("domain", "AI")

    return (
        f"You are {name}, an autonomous agent specializing in "
        f"{domain}. "
        f"Your voice must be {voice_rules}. "
        f"Your stable interests are {interests}. "
        f"When publishing, every piece of content must meet these standards: "
        f"{standards}."
    )


def _build_user_prompt(topic: dict) -> str:
    title = topic.get("title", "")
    source_url = topic.get("source_url", "")
    research_context = topic.get("research_context") or topic.get("summary") or ""

    return (
        f"Topic title: {title}\n"
        f"Source URL: {source_url}\n\n"
        f"Research context:\n{research_context}\n\n"
        "Write a social-media-style post between 150 and 280 words in your "
        "voice. Also write a short rationale (2-3 sentences) explaining "
        "why this topic was picked and why it matters right now.\n\n"
        'Reply ONLY with JSON in this exact shape: '
        '{"text": "the post text", "rationale": "why this topic matters now"}'
    )


def _parse_post(raw_reply: str) -> dict | None:
    text = _strip_markdown_fences(raw_reply or "")
    if not text:
        return None

    candidates = [text]
    object_match = _JSON_OBJECT_RE.search(text)
    if object_match:
        candidates.append(object_match.group(0))

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue

        if not isinstance(parsed, dict):
            continue

        post_text = parsed.get("text")
        rationale = parsed.get("rationale")
        if not isinstance(post_text, str) or not post_text.strip():
            continue
        if not isinstance(rationale, str) or not rationale.strip():
            continue

        return {
            "text": post_text.strip(),
            "rationale": rationale.strip(),
        }

    return None


async def _generate_and_parse(
    generate_fn,
    system_prompt: str,
    user_prompt: str,
) -> dict | None:
    try:
        raw_reply = await generate_fn(system_prompt, user_prompt)
        return _parse_post(raw_reply)
    except Exception:
        return None


async def write_post(topic: dict, persona: dict) -> dict | None:
    system_prompt = _render_system_prompt(persona)
    user_prompt = _build_user_prompt(topic)

    result = await _generate_and_parse(gemini_generate, system_prompt, user_prompt)
    if result is not None:
        return result

    return await _generate_and_parse(openrouter_generate, system_prompt, user_prompt)
