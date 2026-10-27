"""Shared test fixtures.

Isolation rules: settings never read a developer ``.env``; each test gets its own
temporary migrated SQLite database; and no fixture inserts ledger, wage or
payment records. The only rows created are the profile rows the code under test
is expected to create.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.security.supabase_jwt import SupabaseTokenVerifier
from tests.helpers import StubJwksProvider, build_jwks, build_settings, run_migrations

# --- Settings ----------------------------------------------------------------


@pytest.fixture
def settings_factory(tmp_path: Path) -> Callable[..., Settings]:
    def _factory(**overrides: Any) -> Settings:
        return build_settings(tmp_path, **overrides)

    return _factory


@pytest.fixture
def settings(settings_factory: Callable[..., Settings]) -> Settings:
    """Settings with no Supabase project configured."""
    return settings_factory()


@pytest.fixture
def configured_settings(settings_factory: Callable[..., Settings]) -> Settings:
    """Settings pointing at a real-looking but non-existent Supabase project.

    The JWKS endpoint is never contacted: the verifier is given an in-process
    key source instead.
    """
    return settings_factory(supabase_url="https://project-ref.supabase.co")


# --- Signing keys ------------------------------------------------------------


@pytest.fixture(scope="session")
def rsa_private_key() -> rsa.RSAPrivateKey:
    """A keypair generated for this test session only."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="session")
def other_rsa_private_key() -> rsa.RSAPrivateKey:
    """A second keypair, used to sign tokens that must not be trusted."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="session")
def jwks_document(rsa_private_key: rsa.RSAPrivateKey) -> dict[str, Any]:
    return build_jwks(rsa_private_key)


@pytest.fixture
def jwks_provider(jwks_document: dict[str, Any]) -> StubJwksProvider:
    return StubJwksProvider(jwks_document)


@pytest.fixture
def verifier(
    configured_settings: Settings, jwks_provider: StubJwksProvider
) -> SupabaseTokenVerifier:
    """Verifier wired to an in-process key set (no network access)."""
    return SupabaseTokenVerifier(
        issuer=configured_settings.resolved_issuer,
        audience=configured_settings.resolved_audience,
        jwks_provider=jwks_provider,
    )


# --- Applications ------------------------------------------------------------


@pytest.fixture
def client(settings: Settings) -> TestClient:
    """App with no Supabase project configured and no migrated database."""
    with TestClient(create_app(settings)) as test_client:
        yield test_client


@pytest.fixture
def auth_app(configured_settings: Settings, jwks_provider: StubJwksProvider):
    """App whose schema is migrated and whose verifier uses local test keys."""
    run_migrations(configured_settings.database_url)
    app = create_app(configured_settings)
    # Replace only the network key source; the real verification code runs.
    app.state.token_verifier = SupabaseTokenVerifier(
        issuer=configured_settings.resolved_issuer,
        audience=configured_settings.resolved_audience,
        jwks_provider=jwks_provider,
    )
    return app


@pytest.fixture
def auth_client(auth_app) -> TestClient:
    with TestClient(auth_app) as test_client:
        yield test_client
