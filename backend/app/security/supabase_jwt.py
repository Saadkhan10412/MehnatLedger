"""Verification of Supabase-issued access tokens.

Verified against Supabase's official documentation (2026-10-27):

* Access tokens are sent as ``Authorization: Bearer <jwt>``.
* Claims include ``iss`` (``https://<ref>.supabase.co/auth/v1``), ``sub`` (the
  user id), ``role``, and ``exp``.
* Appending ``/.well-known/jwks.json`` to the issuer returns the project's
  **public** signing keys, for asymmetric algorithms (RS256/ES256/...).
* That JWKS endpoint "does not return any keys if you are not using asymmetric
  JWT signing keys", which is reported as a distinct, actionable error here.
* Supabase caches its JWKS at the edge for 10 minutes and warns against caching
  it longer in the application, so the cache TTL is capped accordingly.

Security notes:

* Only asymmetric algorithms are accepted on the JWKS path. Accepting a
  symmetric algorithm there would enable an algorithm-confusion attack in which
  an attacker signs an HS256 token using the *public* key as the HMAC secret.
* ``aud`` is not part of Supabase's documented JWT payload, so it is enforced
  only when explicitly configured. Enforcing an invented value would reject
  every genuine token.
* Error messages never include token contents.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, Protocol

import httpx
import jwt
from jwt import PyJWK

from app.core.config import Settings

logger = logging.getLogger("mehnatledger.auth")

# Asymmetric algorithms permitted when verifying with a public key.
ASYMMETRIC_ALGORITHMS = frozenset(
    {
        "RS256",
        "RS384",
        "RS512",
        "ES256",
        "ES384",
        "ES512",
        "PS256",
        "PS384",
        "PS512",
        "EdDSA",
    }
)

# Supabase caches its JWKS at the edge for 10 minutes and advises against caching
# longer in the application, to keep key revocation effective.
MAX_JWKS_CACHE_SECONDS = 600

# A generous cap that still rejects absurd payloads before parsing.
MAX_TOKEN_LENGTH = 8192


class AuthenticationError(Exception):
    """A token could not be trusted.

    The message is safe to log and safe to return to a client: it never contains
    token contents, claims or key material.
    """


@dataclass(frozen=True)
class VerifiedIdentity:
    """The trusted identity extracted from a verified access token."""

    subject: uuid.UUID
    role: str | None
    expires_at: int | None


class JwksProvider(Protocol):
    """Source of the project's public JWKS document."""

    def get_jwks(self) -> dict[str, Any]: ...


class HttpJwksProvider:
    """Fetches and caches the project's JWKS over HTTPS."""

    def __init__(
        self,
        url: str,
        cache_seconds: int = MAX_JWKS_CACHE_SECONDS,
        timeout_seconds: float = 5.0,
    ) -> None:
        self._url = url
        self._cache_seconds = min(max(cache_seconds, 0), MAX_JWKS_CACHE_SECONDS)
        self._timeout = timeout_seconds
        self._cached: dict[str, Any] | None = None
        self._fetched_at = 0.0

    def get_jwks(self) -> dict[str, Any]:
        now = time.monotonic()
        if self._cached is not None and (now - self._fetched_at) < self._cache_seconds:
            return self._cached

        try:
            response = httpx.get(
                self._url,
                timeout=self._timeout,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            document = response.json()
        except httpx.HTTPError as exc:
            # Log the category only; the URL is configuration, not a secret, but
            # the response body could contain more than we want to store.
            logger.warning("Could not fetch JWKS: %s", type(exc).__name__)
            raise AuthenticationError(
                "Could not reach the identity provider to verify the token."
            ) from exc
        except ValueError as exc:
            raise AuthenticationError(
                "The identity provider returned a malformed JWKS document."
            ) from exc

        if not isinstance(document, dict):
            raise AuthenticationError("The identity provider returned a malformed JWKS document.")

        self._cached = document
        self._fetched_at = now
        return document


class SupabaseTokenVerifier:
    """Verifies Supabase access tokens.

    Exactly one verification path is used, decided by configuration:

    * asymmetric token + ``jwks_provider`` -> verify signature with the public key
    * HS256 token + ``shared_secret``     -> verify with the legacy shared secret
    """

    def __init__(
        self,
        *,
        issuer: str | None,
        audience: str | None = None,
        jwks_provider: JwksProvider | None = None,
        shared_secret: str | None = None,
    ) -> None:
        self._issuer = issuer
        self._audience = audience
        self._jwks_provider = jwks_provider
        self._shared_secret = shared_secret

    # --- public API ---------------------------------------------------------

    def verify(self, token: str) -> VerifiedIdentity:
        if not token or len(token) > MAX_TOKEN_LENGTH:
            raise AuthenticationError("Token is missing or too long.")

        try:
            header = jwt.get_unverified_header(token)
        except jwt.PyJWTError as exc:
            raise AuthenticationError("Token is not a well-formed JWT.") from exc

        algorithm = header.get("alg")
        if not isinstance(algorithm, str) or not algorithm:
            raise AuthenticationError("Token header is missing an algorithm.")

        if algorithm.upper().startswith("HS"):
            claims = self._decode_with_shared_secret(token, algorithm.upper())
        elif algorithm in ASYMMETRIC_ALGORITHMS:
            claims = self._decode_with_jwks(token, header, algorithm)
        else:
            # Includes "none" and any algorithm we do not explicitly allow.
            raise AuthenticationError(f"Token algorithm is not accepted: {algorithm}")

        return self._identity_from_claims(claims)

    # --- verification paths -------------------------------------------------

    def _decode_with_shared_secret(self, token: str, algorithm: str) -> dict[str, Any]:
        if not self._shared_secret:
            raise AuthenticationError(
                "Token uses a shared-secret algorithm, but this server is not configured "
                "with a shared secret."
            )
        if algorithm != "HS256":
            raise AuthenticationError(f"Shared-secret algorithm is not accepted: {algorithm}")

        return self._decode(
            token,
            key=self._shared_secret,
            algorithms=["HS256"],
        )

    def _decode_with_jwks(
        self,
        token: str,
        header: dict[str, Any],
        algorithm: str,
    ) -> dict[str, Any]:
        if self._jwks_provider is None:
            raise AuthenticationError(
                "Token is signed with an asymmetric key, but no JWKS source is configured."
            )

        document = self._jwks_provider.get_jwks()
        keys = document.get("keys")
        if not isinstance(keys, list) or not keys:
            # Supabase returns no keys unless the project uses asymmetric signing
            # keys. Surface that cause rather than a generic "invalid token".
            raise AuthenticationError(
                "The identity provider published no signing keys. Supabase returns no keys "
                "unless the project uses asymmetric JWT signing keys."
            )

        kid = header.get("kid")
        candidate = self._select_key(keys, kid)
        if candidate is None:
            # A key rotation or a wrong project URL both look like this.
            raise AuthenticationError(
                "No published signing key matches this token. The token may be from a "
                "different project, or the signing keys were just rotated."
            )

        declared_algorithm = candidate.get("alg")
        if isinstance(declared_algorithm, str) and declared_algorithm not in ASYMMETRIC_ALGORITHMS:
            # Never trust an asymmetric JWKS entry that claims a symmetric algorithm.
            raise AuthenticationError("A published signing key declared an unsupported algorithm.")

        try:
            public_key = PyJWK.from_dict(candidate, algorithm=algorithm).key
        except (jwt.PyJWTError, ValueError, KeyError) as exc:
            raise AuthenticationError("A published signing key could not be read.") from exc

        return self._decode(token, key=public_key, algorithms=[algorithm])

    @staticmethod
    def _select_key(keys: list[Any], kid: Any) -> dict[str, Any] | None:
        typed = [key for key in keys if isinstance(key, dict)]
        if isinstance(kid, str):
            for key in typed:
                if key.get("kid") == kid:
                    return key
            return None
        # Tokens without a `kid` can only be matched unambiguously.
        return typed[0] if len(typed) == 1 else None

    def _decode(self, token: str, *, key: Any, algorithms: list[str]) -> dict[str, Any]:
        enforce_issuer = self._issuer is not None
        enforce_audience = self._audience is not None

        options: dict[str, Any] = {
            "require": ["exp", "sub"],
            "verify_exp": True,
            "verify_iss": enforce_issuer,
            "verify_aud": enforce_audience,
            "verify_signature": True,
        }

        try:
            return jwt.decode(
                token,
                key=key,
                algorithms=algorithms,
                issuer=self._issuer if enforce_issuer else None,
                audience=self._audience if enforce_audience else None,
                options=options,
            )
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationError("Token has expired. Sign in again.") from exc
        except jwt.InvalidAudienceError as exc:
            raise AuthenticationError("Token was issued for a different audience.") from exc
        except jwt.InvalidIssuerError as exc:
            raise AuthenticationError("Token was issued by a different provider.") from exc
        except jwt.MissingRequiredClaimError as exc:
            raise AuthenticationError("Token is missing a required claim.") from exc
        except jwt.InvalidSignatureError as exc:
            raise AuthenticationError("Token signature is invalid.") from exc
        except jwt.PyJWTError as exc:
            raise AuthenticationError("Token could not be verified.") from exc

    @staticmethod
    def _identity_from_claims(claims: dict[str, Any]) -> VerifiedIdentity:
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise AuthenticationError("Token has no subject claim.")

        try:
            subject_uuid = uuid.UUID(subject)
        except ValueError as exc:
            # Our Profile primary key is a UUID, so an unusable subject is a hard
            # failure here rather than a database error later.
            raise AuthenticationError("Token subject is not a valid identifier.") from exc

        role = claims.get("role")
        expires_at = claims.get("exp")

        return VerifiedIdentity(
            subject=subject_uuid,
            role=role if isinstance(role, str) else None,
            expires_at=expires_at if isinstance(expires_at, int) else None,
        )


def build_token_verifier(
    settings: Settings,
    jwks_provider: JwksProvider | None = None,
) -> SupabaseTokenVerifier | None:
    """Build the verifier for the configured Supabase project.

    Returns ``None`` when no Supabase project is configured, so the caller can
    report authentication as an unmet setup requirement instead of rejecting
    every request as if the token were bad.
    """
    mode = settings.auth_mode

    if mode == "jwks":
        provider = jwks_provider or HttpJwksProvider(
            url=settings.resolved_jwks_url,
            cache_seconds=settings.jwks_cache_seconds,
        )
        return SupabaseTokenVerifier(
            issuer=settings.resolved_issuer,
            audience=settings.resolved_audience,
            jwks_provider=provider,
        )

    if mode == "shared_secret":
        # Use the guarded accessor: a blank configured value must never become
        # an empty HMAC key.
        secret = settings.shared_secret_value
        logger.warning(
            "Verifying Supabase tokens with a shared secret. Supabase documents this "
            "approach as strongly discouraged; migrate to asymmetric signing keys."
        )
        return SupabaseTokenVerifier(
            issuer=settings.resolved_issuer,
            audience=settings.resolved_audience,
            shared_secret=secret,
        )

    return None
