"""Response schema for the current authenticated profile."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MeResponse(BaseModel):
    """The caller's own profile.

    Deliberately exposes no email, phone, role or token claim: nothing in the
    current scope needs them, so they are not collected or returned. The access
    token itself is never echoed back.
    """

    id: UUID = Field(description="The authenticated user's identifier.")
    created_at: datetime
    updated_at: datetime
