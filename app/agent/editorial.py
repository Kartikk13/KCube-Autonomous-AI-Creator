from __future__ import annotations

import json
import re

from app.agent.persona import render_system_prompt
from app.services.gemini_client import generate

UNPARSEABLE_DECISION = {
    "decision": "reject",
    "reasoning": "unparseable model output, defaulting to reject",
}

_JSON_OBJECT_RE = re.compile(r"\{[\s\S]*\}")
_FENCE_PREFIX_RE = re.compile(r"^```(?:json)?\s*", re.IGNORECASE)
_FENCE_SUFFIX_RE = re.compile(r"\s*```$")


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    text = _FENCE_PREFIX_RE.sub("", text, count=1)
    text = _FENCE_SUFFIX_RE.sub("", text, count=1)
    return text.strip()


def _build_user_prompt(
    topic: dict,
    persona: dict,
    recent_topics: list[dict],
) -> str:
    standards = persona.get("publishing_standards") or []
    standards_text = "\n".join(f"- {rule}" for rule in standards)

    recent_titles = [
        str(recent_topic.get("title", "")).strip()
        for recent_topic in recent_topics
        if str(recent_topic.get("title", "")).strip()
    ]
    recent_text = (
        "\n".join(f"- {title}" for title in recent_titles)
        if recent_titles
        else "- (none)"
    )

    topic_text = json.dumps(topic, ensure_ascii=False)

    return (
        f"Topic to evaluate:\n{topic_text}\n\n"
        "Decide accept or reject for this topic based on these "
        f"publishing_standards rules:\n{standards_text}\n\n"
        "Check this topic isn't too similar to these recent topics:\n"
        f"{recent_text}\n\n"
        'Reply ONLY with JSON in this exact shape: '
        '{"decision": "accept" or "reject", "reasoning": '
        '"one or two sentences explaining why"}'
    )


def _parse_model_decision(raw_reply: str) -> dict | None:
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

        decision = parsed.get("decision")
        reasoning = parsed.get("reasoning")
        if decision not in {"accept", "reject"}:
            continue
        if not isinstance(reasoning, str) or not reasoning.strip():
            continue

        return {
            "decision": decision,
            "reasoning": reasoning.strip(),
        }

    return None


async def judge_topic(
    topic: dict,
    persona: dict,
    recent_topics: list[dict],
) -> dict:
    try:
        system_prompt = render_system_prompt()
        user_prompt = _build_user_prompt(topic, persona, recent_topics)
        raw_reply = await generate(system_prompt, user_prompt)
        parsed = _parse_model_decision(raw_reply)
        if parsed is None:
            return UNPARSEABLE_DECISION.copy()
        return parsed
    except Exception:
        return UNPARSEABLE_DECISION.copy()
