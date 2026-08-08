import os
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DEFAULT_DATABASE_URL = "sqlite:///./data/agent.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def _ensure_sqlite_directory(url: str) -> None:
    if not url.startswith("sqlite"):
        return

    db_path = url.split("///", 1)[-1]
    if db_path == ":memory:":
        return

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    _ensure_sqlite_directory(DATABASE_URL)

    schema_path = Path(__file__).parent / "schema.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")

    with engine.begin() as conn:
        raw_conn = conn.connection.dbapi_connection
        raw_conn.executescript(schema_sql)


@contextmanager
def get_db():
    conn = engine.connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
