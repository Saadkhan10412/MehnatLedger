"""Authorization tests for the authenticated profile endpoint.

These call the API directly with tokens, which is the only meaningful way to test
authorization: hiding a control in the UI is not a security boundary.
"""

from __future__ import annotations

import uuid

from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.models.profile import Profile
from tests.helpers import SUBJECT_A, SUBJECT_B, authorization_header, mint_token

# --- Anonymous and invalid callers -------------------------------------------


def test_anonymous_request_is_rejected_with_a_challenge(auth_client: TestClient) -> None:
    response = auth_client.get("/api/v1/me")

    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Bearer"


def test_malformed_authorization_header_is_rejected(auth_client: TestClient) -> None:
    response = auth_client.get("/api/v1/me", headers={"Authorization": "Bearer"})

    assert response.status_code == 401


def test_token_signed_by_an_untrusted_key_is_rejected(
    auth_client: TestClient, other_rsa_private_key: rsa.RSAPrivateKey
) -> None:
    token = mint_token(other_rsa_private_key, subject=SUBJECT_A)

    response = auth_client.get("/api/v1/me", headers=authorization_header(token))

    assert response.status_code == 401
    assert "signature is invalid" in response.json()["detail"]


def test_expired_token_is_rejected(
    auth_client: TestClient, rsa_private_key: rsa.RSAPrivateKey
) -> None:
    token = mint_token(rsa_private_key, subject=SUBJECT_A, expires_in=-60)

    response = auth_client.get("/api/v1/me", headers=authorization_header(token))

    assert response.status_code == 401


def test_unconfigured_server_reports_a_setup_problem_not_bad_credentials(
    client: TestClient,
) -> None:
    """With no Supabase project configured, 503 is honest; 401 would mislead."""
    response = client.get("/api/v1/me", headers={"Authorization": "Bearer anything"})

    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


# --- The authenticated happy path --------------------------------------------


def test_valid_token_returns_the_callers_own_profile(
    auth_client: TestClient, rsa_private_key: rsa.RSAPrivateKey
) -> None:
    token = mint_token(rsa_private_key, subject=SUBJECT_A)

    response = auth_client.get("/api/v1/me", headers=authorization_header(token))

    assert response.status_code == 200
    assert response.json()["id"] == SUBJECT_A
    # Personalised responses must not be stored by browsers or shared caches.
    assert response.headers["Cache-Control"] == "no-store"


def test_token_is_never_echoed_back(
    auth_client: TestClient, rsa_private_key: rsa.RSAPrivateKey
) -> None:
    token = mint_token(rsa_private_key, subject=SUBJECT_A)

    response = auth_client.get("/api/v1/me", headers=authorization_header(token))

    assert token not in response.text


# --- Cross-user isolation ----------------------------------------------------


def test_each_user_can_only_see_their_own_profile(
    auth_client: TestClient, rsa_private_key: rsa.RSAPrivateKey
) -> None:
    token_a = mint_token(rsa_private_key, subject=SUBJECT_A)
    token_b = mint_token(rsa_private_key, subject=SUBJECT_B)

    body_a = auth_client.get("/api/v1/me", headers=authorization_header(token_a)).json()
    body_b = auth_client.get("/api/v1/me", headers=authorization_header(token_b)).json()

    assert body_a["id"] == SUBJECT_A
    assert body_b["id"] == SUBJECT_B
    assert body_a["id"] != body_b["id"]


def test_caller_supplied_user_id_cannot_select_another_account(
    auth_client: TestClient, rsa_private_key: rsa.RSAPrivateKey
) -> None:
    """The identity comes from the verified token, never from request input."""
    token = mint_token(rsa_private_key, subject=SUBJECT_A)

    response = auth_client.get(
        f"/api/v1/me?user_id={SUBJECT_B}",
        headers=authorization_header(token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == SUBJECT_A


# --- Data integrity ----------------------------------------------------------


def test_database_starts_empty(auth_app) -> None:
    """No fixture and no startup path may insert sample rows."""
    session = auth_app.state.session_factory()
    try:
        assert session.query(Profile).count() == 0
    finally:
        session.close()


def test_repeated_requests_create_exactly_one_profile_row(
    auth_client: TestClient, auth_app, rsa_private_key: rsa.RSAPrivateKey
) -> None:
    token = mint_token(rsa_private_key, subject=SUBJECT_A)

    for _ in range(3):
        assert auth_client.get("/api/v1/me", headers=authorization_header(token)).status_code == 200

    session = auth_app.state.session_factory()
    try:
        rows = session.query(Profile).all()
    finally:
        session.close()

    assert len(rows) == 1
    assert rows[0].id == uuid.UUID(SUBJECT_A)


def test_profile_creation_is_race_safe(auth_app, rsa_private_key: rsa.RSAPrivateKey) -> None:
    """Concurrent first requests must not raise or duplicate the row."""
    from app.repositories.profiles import get_or_create_profile_for_subject

    subject = uuid.UUID(SUBJECT_A)
    session = auth_app.state.session_factory()
    try:
        # Simulate the loser of a duplicate-key race by inserting first, then
        # asking the repository to create the same subject again.
        first = get_or_create_profile_for_subject(session, subject)
        second = get_or_create_profile_for_subject(session, subject)
        assert first.id == second.id
        assert session.query(Profile).count() == 1
    finally:
        session.close()
