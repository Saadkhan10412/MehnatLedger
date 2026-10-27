"""Declarative base for all ORM models."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base.

    Import every model module before calling ``Base.metadata.create_all`` or
    running an Alembic autogenerate, so the metadata is complete.
    """
