"""Profile persistence, scoped by authenticated subject."""

from __future__ import annotations

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.profile import Profile


def get_profile_for_subject(session: Session, subject: uuid.UUID) -> Profile | None:
    """Fetch the profile belonging to a verified token subject.

    The primary key *is* the subject, so this lookup cannot be pointed at another
    user's row by passing a different kind of identifier. Callers must pass the
    subject from ``VerifiedIdentity``, never a value read from request input.
    """
    return session.get(Profile, subject)


def get_or_create_profile_for_subject(session: Session, subject: uuid.UUID) -> Profile:
    """Return the caller's profile, creating it on first sight.

    Sign-up happens in Supabase Auth, so the application creates its own profile
    row lazily when an authenticated user first makes a request.

    Two simultaneous first requests could both try to insert. The unique primary
    key makes one of them fail with :class:`~sqlalchemy.exc.IntegrityError`; that
    loser rolls back and reads the winner's row instead. This keeps the operation
    idempotent and free of duplicate rows.
    """
    existing = get_profile_for_subject(session, subject)
    if existing is not None:
        return existing

    profile = Profile(id=subject)
    session.add(profile)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raced = get_profile_for_subject(session, subject)
        if raced is None:
            # Not a duplicate-key race; surface the original failure.
            raise
        return raced

    session.refresh(profile)
    return profile
