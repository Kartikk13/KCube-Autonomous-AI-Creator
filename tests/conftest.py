import importlib
import sys

import pytest
from fastapi.testclient import TestClient


def _reload_app_modules() -> None:
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)

    _reload_app_modules()

    from app.agent import persona
    from app.api import init_route
    from app.db.database import init_db
    from app.main import app

    
    monkeypatch.setattr(init_route, "start_scheduler", lambda agent_id: None)

    init_db()

    with TestClient(app) as test_client:
        yield test_client
