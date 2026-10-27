"""Endpoints for the authenticated caller's own account."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.api.deps import get_current_profile
from app.models.profile import Profile
from app.schemas.me import MeResponse

router = APIRouter()


@router.get(
    "/me",
    response_model=MeResponse,
    summary="The current authenticated profile",
    description=(
        "Returns the profile belonging to the bearer token's subject. The subject is "
        "read from the verified token only; no request parameter can select a different "
        "account. Anonymous or invalid requests are rejected with 401."
    ),
)
def read_current_profile(
    response: Response,
    profile: Annotated[Profile, Depends(get_current_profile)],
) -> MeResponse:
    # Personalised data must not be stored by browsers or shared caches.
    response.headers["Cache-Control"] = "no-store"
    return MeResponse(
        id=profile.id,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )
