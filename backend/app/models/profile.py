"""The application's own user profile record."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Profile(Base):
    """One row per authenticated identity.

    ``id`` is the verified subject (``sub``) claim of the caller's Supabase access
    token. It is never taken from request input.

    Deliberately minimal (prd.md FR-01: store only profile fields the service
    needs). No name, Aadhaar, bank detail, address, email or phone number is
    stored, because nothing in the current scope requires them. A display name
    or language preference should only be added once a feature actually needs it.

    The table is named ``profiles`` rather than ``users`` to avoid any confusion
    with Supabase's own ``auth.users`` table, which this application never writes
    to.
    """

    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Profile(id={self.id!r})"
