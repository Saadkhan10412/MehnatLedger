"""Tests for Supabase access token verification.

These exercise the real verification code. Only the network JWKS fetch is
replaced, so signature checking, expiry, issuer handling and the algorithm
allow-list are genuinely tested. Nothing contacts the live Supabase project.
"""

from __future__ import annotations

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.config import Settings
from app.security.supabase_jwt import AuthenticationError, SupabaseTokenVerifier
from tests.helpers import (
    SUBJECT_A,
    TEST_SHARED_SECRET,
    StubJwksProvider,
    build_jwks,
    mint_token,
    unsigned_token,
)

# --- The happy path ----------------------------------------------------------


def test_valid_token_yields_the_verified_identity(
    verifier: SupabaseTokenVerifier, rsa_private_key: rsa.RSAPrivateKey
) -> None:
    token = mint_token(rsa_private_key, subject=SUBJECT_A)

    identity = verifier.verify(token)

    assert str(identity.subject) == SUBJECT_A
    assert identity.role == "authenticated"
    assert identity.expires_at is not None


# --- Tampering and forgery ---------------------------------------------------


def test_expired_token_is_rejected(
    verifier: SupabaseTokenVerifier, rsa_private_key: rsa.RSAPrivateKey
) -> None:
    token = mint_token(rsa_private_key, subject=SUBJECT_A, expires_in=-60)

    with pytest.raises(AuthenticationError, match="expired"):
        verifier.verify(token)


def test_token_signed_by_an_unknown_key_is_rejected(
    verifier: SupabaseTokenVerifier, other_rsa_private_key: rsa.RSAPrivateKey
) -> None:
    token = mint_token(other_rsa_private_key, subject=SUBJECT_A)

    with pytest.raises(AuthenticationError, match="signature is invalid"):
        verifier.verify(token)


def test_token_from_another_issuer_is_rejected(
    verifier: SupabaseTokenVerifier, rsa_private_key: rsa.RSAPrivateKey
) -> None:
    token = mint_token(
        rsa_private_key, subject=SUBJECT_A, issuer="https://attacker.example.com/auth/v1"
    )

    with pytest.raises(AuthenticationError, match="different provider"):
        verifier.verify(token)


def test_unsigned_alg_none_token_is_rejected(verifier: SupabaseTokenVerifier) -> None:
    with pytest.raises(AuthenticationError, match="algorithm is not accepted"):
        verifier.verify(unsigned_token(SUBJECT_A))


def test_shared_secret_token_rejected_when_only_public_keys_are_configured(
    verifier: SupabaseTokenVerifier,
) -> None:
    """Algorithm-confusion defence.

    An attacker who knows the public key must not be able to sign an HS256 token
    using that public key as the HMAC secret. Because this verifier has no shared
    secret configured, the token is rejected outright.
    """
    token = mint_token(TEST_SHARED_SECRET, subject=SUBJECT_A, algorithm="HS256")

    with pytest.raises(AuthenticationError, match="not configured with a shared secret"):
        verifier.verify(token)


def test_jwks_entry_declaring_a_symmetric_algorithm_is_rejected(
    configured_settings: Settings, rsa_private_key: rsa.RSAPrivateKey
) -> None:
    document = build_jwks(rsa_private_key)
    document["keys"][0]["alg"] = "HS256"
    verifier = SupabaseTokenVerifier(
        issuer=configured_settings.resolved_issuer,
        jwks_provider=StubJwksProvider(document),
    )
    token = mint_token(rsa_private_key, subject=SUBJECT_A)

    with pytest.raises(AuthenticationError, match="unsupported algorithm"):
        verifier.verify(token)


def test_malformed_and_empty_tokens_are_rejected(verifier: SupabaseTokenVerifier) -> None:
    with pytest.raises(AuthenticationError, match="not a well-formed JWT"):
        verifier.verify("this-is-not-a-jwt")

    with pytest.raises(AuthenticationError, match="missing or too long"):
        verifier.verify("")

    with pytest.raises(AuthenticationError, match="missing or too long"):
        verifier.verify("x" * 9000)


def test_subject_that_is_not_a_uuid_is_rejected(
    verifier: SupabaseTokenVerifier, rsa_private_key: rsa.RSAPrivateKey
) -> None:
    token = mint_token(rsa_private_key, subject="not-a-uuid")

    with pytest.raises(AuthenticationError, match="not a valid identifier"):
        verifier.verify(token)


# --- Supabase-specific configuration paths -----------------------------------


def test_empty_jwks_reports_the_actual_supabase_cause(
    configured_settings: Settings, rsa_private_key: rsa.RSAPrivateKey
) -> None:
    """Supabase publishes no keys unless the project uses asymmetric signing keys.

    Operators need to be told that, rather than being sent looking for a bad
    token.
    """
    verifier = SupabaseTokenVerifier(
        issuer=configured_settings.resolved_issuer,
        jwks_provider=StubJwksProvider({"keys": []}),
    )
    token = mint_token(rsa_private_key, subject=SUBJECT_A)

    with pytest.raises(AuthenticationError, match="asymmetric JWT signing keys"):
        verifier.verify(token)


def test_unknown_key_id_is_reported_as_a_key_mismatch(
    configured_settings: Settings,
    rsa_private_key: rsa.RSAPrivateKey,
    jwks_provider: StubJwksProvider,
) -> None:
    verifier = SupabaseTokenVerifier(
        issuer=configured_settings.resolved_issuer, jwks_provider=jwks_provider
    )
    token = mint_token(rsa_private_key, subject=SUBJECT_A, kid="a-rotated-away-key")

    with pytest.raises(AuthenticationError, match="No published signing key matches"):
        verifier.verify(token)


def test_asymmetric_token_rejected_when_no_jwks_source_is_configured(
    configured_settings: Settings, rsa_private_key: rsa.RSAPrivateKey
) -> None:
    verifier = SupabaseTokenVerifier(
        issuer=configured_settings.resolved_issuer,
        shared_secret=TEST_SHARED_SECRET,
    )
    token = mint_token(rsa_private_key, subject=SUBJECT_A)

    with pytest.raises(AuthenticationError, match="no JWKS source is configured"):
        verifier.verify(token)


def test_legacy_shared_secret_path_accepts_a_correctly_signed_token(
    configured_settings: Settings,
) -> None:
    verifier = SupabaseTokenVerifier(
        issuer=configured_settings.resolved_issuer,
        shared_secret=TEST_SHARED_SECRET,
    )
    token = mint_token(TEST_SHARED_SECRET, subject=SUBJECT_A, algorithm="HS256")

    assert str(verifier.verify(token).subject) == SUBJECT_A


def test_legacy_shared_secret_path_rejects_a_wrong_secret(
    configured_settings: Settings,
) -> None:
    verifier = SupabaseTokenVerifier(
        issuer=configured_settings.resolved_issuer,
        shared_secret=TEST_SHARED_SECRET,
    )
    token = mint_token("a-completely-different-secret", subject=SUBJECT_A, algorithm="HS256")

    with pytest.raises(AuthenticationError, match="signature is invalid"):
        verifier.verify(token)


# --- Audience handling -------------------------------------------------------


def test_audience_is_not_enforced_when_unconfigured(
    configured_settings: Settings,
    rsa_private_key: rsa.RSAPrivateKey,
    jwks_provider: StubJwksProvider,
) -> None:
    """Supabase's documented payload has no ``aud`` claim.

    Enforcing an invented audience would reject every genuine token, so it is
    skipped until the real value is confirmed.
    """
    verifier = SupabaseTokenVerifier(
        issuer=configured_settings.resolved_issuer,
        audience=None,
        jwks_provider=jwks_provider,
    )
    token = mint_token(rsa_private_key, subject=SUBJECT_A)

    assert str(verifier.verify(token).subject) == SUBJECT_A


def test_audience_is_enforced_once_configured(
    configured_settings: Settings,
    rsa_private_key: rsa.RSAPrivateKey,
    jwks_provider: StubJwksProvider,
) -> None:
    verifier = SupabaseTokenVerifier(
        issuer=configured_settings.resolved_issuer,
        audience="authenticated",
        jwks_provider=jwks_provider,
    )

    accepted = mint_token(rsa_private_key, subject=SUBJECT_A, audience="authenticated")
    assert str(verifier.verify(accepted).subject) == SUBJECT_A

    rejected = mint_token(rsa_private_key, subject=SUBJECT_A, audience="another-app")
    with pytest.raises(AuthenticationError, match="different audience"):
        verifier.verify(rejected)


def test_derived_urls_follow_supabase_documentation(configured_settings: Settings) -> None:
    """The JWKS URL is the issuer plus the documented discovery path."""
    assert configured_settings.resolved_issuer == "https://project-ref.supabase.co/auth/v1"
    assert (
        configured_settings.resolved_jwks_url
        == "https://project-ref.supabase.co/auth/v1/.well-known/jwks.json"
    )
    assert configured_settings.auth_mode == "jwks"
