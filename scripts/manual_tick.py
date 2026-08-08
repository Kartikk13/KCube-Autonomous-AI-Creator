import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.scheduler import run_agent_tick


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one agent tick immediately.")
    parser.add_argument(
        "--agent-id",
        required=True,
        help="Agent ID to run the tick for",
    )
    args = parser.parse_args()
    asyncio.run(run_agent_tick(args.agent_id))
    print("Tick complete.")


if __name__ == "__main__":
    main()
