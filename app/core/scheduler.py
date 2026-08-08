import asyncio
import threading

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()
_scheduler_start_lock = threading.Lock()


def run_agent_tick(agent_id: str) -> None:
    print(f"tick for {agent_id}")


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
