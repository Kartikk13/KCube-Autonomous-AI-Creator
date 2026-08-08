import asyncio
import logging
import threading
import uuid

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.agent.editorial import judge_topic
from app.agent.memory import is_duplicate, load_recent
from app.agent.persona import PERSONA
from app.agent.research import research_topic
from app.agent.topic_discovery import discover_topics
from app.agent.writer import write_post
from app.db.models import (
    get_recent_posts,
    insert_editorial_log,
    insert_post,
    insert_topic,
)
from app.services.embeddings import embed

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
_scheduler_start_lock = threading.Lock()


async def _run_agent_tick_async(agent_id: str) -> None:
    persona = PERSONA
    recent_topics = load_recent(agent_id)
    recent_posts = get_recent_posts(agent_id)

    topic_embeddings = [
        topic["embedding"]
        for topic in recent_topics
        if topic.get("embedding")
    ]
    post_embeddings = [
        post["embedding"]
        for post in recent_posts
        if post.get("embedding")
    ]

    candidates = await discover_topics(persona)
    published_this_tick = False

    for candidate in candidates:
        topic_text = (
            f"{candidate.get('title', '')} {candidate.get('summary', '')}"
        ).strip()
        candidate_embedding = embed(topic_text)

        if is_duplicate(candidate_embedding, topic_embeddings):
            continue

        decision = await judge_topic(candidate, persona, recent_topics)
        insert_editorial_log(
            agent_id,
            candidate,
            decision["decision"],
            decision["reasoning"],
        )

        if decision["decision"] != "accept":
            continue

        if published_this_tick:
            continue

        researched = await research_topic(candidate)
        post = await write_post(researched, persona)
        if post is None:
            continue

        post_embedding = embed(post["text"])
        if is_duplicate(post_embedding, post_embeddings):
            continue

        post_id = str(uuid.uuid4())
        topic_id = insert_topic(agent_id, researched, candidate_embedding)
        insert_post(
            agent_id,
            post_id,
            topic_id,
            post["text"],
            post["rationale"],
            post_embedding,
        )
        published_this_tick = True


async def run_agent_tick(agent_id: str) -> None:
    try:
        await _run_agent_tick_async(agent_id)
    except Exception:
        logger.exception("Agent tick failed for agent_id=%s", agent_id)


def _start_scheduler_on_background_loop() -> None:
    started = threading.Event()

    def run() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def bootstrap() -> None:
            scheduler.start()
            started.set()
            await asyncio.Event().wait()

        loop.run_until_complete(bootstrap())

    thread = threading.Thread(
        target=run,
        daemon=True,
        name="apscheduler-asyncio-loop",
    )
    thread.start()
    started.wait()


def start_scheduler(agent_id: str) -> None:
    scheduler.add_job(
        run_agent_tick,
        trigger=IntervalTrigger(minutes=20),
        args=[agent_id],
        max_instances=1,
        coalesce=True,
    )
    if scheduler.running:
        return

    with _scheduler_start_lock:
        if scheduler.running:
            return
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            _start_scheduler_on_background_loop()
        else:
            scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=True)
