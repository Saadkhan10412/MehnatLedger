"""Helpers shared by the test suite.

Everything here is test-only:

* Signing keys are generated in-process. No real Supabase credential is used.
* Tokens are minted locally, so nothing contacts the live Supabase project.
* ``run_migrations`` creates an isolated database with the real migrations.
"""

from __future__ import annotations

import base64
import json
import time
from pathlib import Path
from typing import Any

import jwt
from alembic.config import Config
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

from alembic import command
from app.core.config import Environment, Settings

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Test-only identifiers. These are fixtures, not real credentials.
TEST_KEY_ID = "test-signing-key-1"
TEST_ISSUER = "https://project-ref.supabase.co/auth/v1"
# At least 32 bytes, so the suite does not trip PyJWT's RFC 7518 key-length
# warning. Still obviously a test value.
TEST_SHARED_SECRET = "test-only-shared-secret-not-a-real-credential-0123456789"

SUBJECT_A = "11111111-1111-4111-8111-111111111111"
SUBJECT_B = "22222222-2222-4222-8222-222222222222"


def build_settings(base_dir: Path, **overrides: Any) -> Settings:
    """Build an isolated Settings object for tests."""
    values: dict[str, Any] = {
        "_env_file": None,
        "environment": Environment.test,
        "database_url": f"sqlite+pysqlite:///{(base_dir / 'test.db').as_posix()}",
    }
    values.update(overrides)
    return Settings(**values)


def alembic_config(database_url: str) -> Config:
    """Alembic config targeting the given database, with no secrets in the ini."""
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def run_migrations(database_url: str) -> None:
    """Apply every migration to the given database.

    Tests therefore run against the migrated schema rather than a schema built
    ad hoc from the models, so a broken migration fails the suite.
    """
    command.upgrade(alembic_config(database_url), "head")


def build_jwks(private_key: rsa.RSAPrivateKey, kid: str = TEST_KEY_ID) -> dict[str, Any]:
    """Build a JWKS document from a public key, shaped like Supabase's."""
    document = json.loads(RSAAlgorithm.to_jwk(private_key.public_key()))
    document.update({"kid": kid, "alg": "RS256", "use": "sig", "key_ops": ["verify"]})
    return {"keys": [document]}


class StubJwksProvider:
    """In-process JWKS source, replacing only the network fetch."""

    def __init__(self, document: dict[str, Any]) -> None:
        self._document = document
        self.calls = 0

    def get_jwks(self) -> dict[str, Any]:
        self.calls += 1
        return self._document


def mint_token(
    private_key: rsa.RSAPrivateKey | str,
    *,
    subject: str,
    kid: str | None = TEST_KEY_ID,
    algorithm: str = "RS256",
    issuer: str = TEST_ISSUER,
    expires_in: int = 3600,
    audience: str | None = None,
    **extra_claims: Any,
) -> str:
    """Create a signed access token for tests."""
    now = int(time.time())
    payload: dict[str, Any] = {
        "iss": issuer,
        "sub": subject,
        "role": "authenticated",
        "iat": now,
        "exp": now + expires_in,
    }
    if audience is not None:
        payload["aud"] = audience
    payload.update(extra_claims)

    headers = {"kid": kid} if kid else None
    return jwt.encode(payload, private_key, algorithm=algorithm, headers=headers)


def unsigned_token(subject: str, issuer: str = TEST_ISSUER) -> str:
    """Craft an ``alg: none`` token, which must never be accepted."""

    def encode(part: dict[str, Any]) -> str:
        raw = json.dumps(part).encode()
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    header = {"alg": "none", "typ": "JWT"}
    payload = {
        "iss": issuer,
        "sub": subject,
        "role": "authenticated",
        "exp": int(time.time()) + 3600,
    }
    return f"{encode(header)}.{encode(payload)}."


def authorization_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
