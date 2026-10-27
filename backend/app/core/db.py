"""Database engine and session management.

The engine is created once per application and stored on ``app.state`` so tests
can inject their own isolated database.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from fastapi import Request
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings


def create_db_engine(settings: Settings) -> Engine:
    """Build the SQLAlchemy engine for the configured database URL."""
    url = settings.database_url
    kwargs: dict[str, Any] = {"pool_pre_ping": True}

    if url.startswith("sqlite"):
        # FastAPI runs sync endpoints in a threadpool, so a SQLite connection may
        # be used from a different thread than the one that created it.
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        # Stationary server defaults for a shared PostgreSQL instance. Supabase's
        # guidance is to keep pool sizes modest and monitor usage rather than
        # defaulting to a large pool.
        kwargs["pool_size"] = 5
        kwargs["max_overflow"] = 5

    return create_engine(url, **kwargs)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session(request: Request) -> Iterator[Session]:
    """FastAPI dependency yielding a database session."""
    factory: sessionmaker[Session] = request.app.state.session_factory
    session = factory()
    try:
        yield session
    finally:
        session.close()
