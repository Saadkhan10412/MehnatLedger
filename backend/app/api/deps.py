"""Shared FastAPI dependencies for authentication and authorization."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.models.profile import Profile
from app.repositories.profiles import get_or_create_profile_for_subject
from app.security.supabase_jwt import (
    AuthenticationError,
    SupabaseTokenVerifier,
    VerifiedIdentity,
)

# auto_error=False so a missing header produces a correct 401 with a
# WWW-Authenticate challenge instead of FastAPI's default 403.
bearer_scheme = HTTPBearer(auto_error=False, description="Supabase access token")

_UNAUTHORIZED_HEADERS = {"WWW-Authenticate": "Bearer"}


def get_token_verifier(request: Request) -> SupabaseTokenVerifier:
    """Return the configured verifier, or fail loudly if none is configured.

    503 (not 401) is deliberate: if the server has no Supabase project
    configured, that is a setup problem, and reporting it as an authentication
    failure would send users chasing a problem with their sign-in.
    """
    verifier: SupabaseTokenVerifier | None = request.app.state.token_verifier
    if verifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Authentication is not configured on this server. An administrator must "
                "set ML_SUPABASE_URL (and, if the project uses the legacy shared secret, "
                "ML_SUPABASE_JWT_SECRET) in the backend environment."
            ),
        )
    return verifier


def get_current_identity(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    verifier: Annotated[SupabaseTokenVerifier, Depends(get_token_verifier)],
) -> VerifiedIdentity:
    """Resolve the caller's identity from the bearer token.

    The identity is derived only from a verified token signature. No request
    body, query parameter or header other than the token can influence it.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sign in to continue.",
            headers=_UNAUTHORIZED_HEADERS,
        )

    try:
        return verifier.verify(credentials.credentials)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers=_UNAUTHORIZED_HEADERS,
        ) from exc


def get_current_profile(
    identity: Annotated[VerifiedIdentity, Depends(get_current_identity)],
    session: Annotated[Session, Depends(get_session)],
) -> Profile:
    """Return the caller's own profile, creating it on first authenticated use.

    Ownership is structural: the subject comes from the verified token, so there
    is no parameter a caller could supply to reach someone else's profile.
    """
    return get_or_create_profile_for_subject(session, identity.subject)
