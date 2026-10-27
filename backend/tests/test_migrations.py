"""Tests that the migrations actually build the schema they claim to."""

from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import inspect

from alembic import command
from app.core.config import Settings
from app.core.db import create_db_engine
from tests.helpers import alembic_config, run_migrations


def _table_names(settings: Settings) -> set[str]:
    engine = create_db_engine(settings)
    try:
        with engine.connect() as connection:
            return set(inspect(connection).get_table_names())
    finally:
        engine.dispose()


def test_upgrade_creates_the_profiles_table(settings_factory: Callable[..., Settings]) -> None:
    settings = settings_factory()

    run_migrations(settings.database_url)

    assert "profiles" in _table_names(settings)


def test_downgrade_removes_the_profiles_table(settings_factory: Callable[..., Settings]) -> None:
    """A migration that cannot be reversed is a liability in production."""
    settings = settings_factory()
    run_migrations(settings.database_url)
    assert "profiles" in _table_names(settings)

    command.downgrade(alembic_config(settings.database_url), "base")

    assert "profiles" not in _table_names(settings)


def test_profiles_table_is_empty_after_migration(settings_factory: Callable[..., Settings]) -> None:
    """Migrations must never seed data."""
    settings = settings_factory()
    run_migrations(settings.database_url)

    engine = create_db_engine(settings)
    try:
        with engine.connect() as connection:
            count = connection.exec_driver_sql("select count(*) from profiles").scalar()
    finally:
        engine.dispose()

    assert count == 0
