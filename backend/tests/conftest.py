"""Shared test fixtures.

Test isolation rules:

* Settings are always built explicitly with ``_env_file=None`` so a developer's
  local ``.env`` cannot change test behaviour.
* The test database is a temporary SQLite file created per test, never the
  development database, and it is never seeded with sample financial records.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.config import Environment, Settings
from app.main import create_app


def build_settings(base_dir: Path, **overrides: Any) -> Settings:
    """Build an isolated Settings object for tests."""
    values: dict[str, Any] = {
        "_env_file": None,
        "environment": Environment.test,
        "database_url": f"sqlite+pysqlite:///{(base_dir / 'test.db').as_posix()}",
    }
    values.update(overrides)
    return Settings(**values)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return build_settings(tmp_path)


@pytest.fixture
def settings_factory(tmp_path: Path) -> Callable[..., Settings]:
    def _factory(**overrides: Any) -> Settings:
        return build_settings(tmp_path, **overrides)

    return _factory


@pytest.fixture
def client(settings: Settings) -> TestClient:
    with TestClient(create_app(settings)) as test_client:
        yield test_client
