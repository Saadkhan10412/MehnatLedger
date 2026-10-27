#!/usr/bin/env python3
"""Live verification of the Supabase sign-in path.

Run after configuring ``backend/.env``:

    uv run python scripts/verify_supabase.py

    # Against a real access token (the token is never printed):
    ML_VERIFY_ACCESS_TOKEN="<access token>" uv run python scripts/verify_supabase.py
    uv run python scripts/verify_supabase.py --token-file /path/to/token.txt

Checks performed:

1. Configuration state (reports presence only, never a value).
2. A real HTTPS fetch of the project's JWKS discovery document.
3. The project's OpenID configuration, when published, for an authoritative issuer.
4. Verification of a real access token, when one is supplied, using the
   application's own verifier rather than a re-implementation.
5. Database reachability when a PostgreSQL URL is configured.

Exit codes:
    0  every required check passed
    1  a required check failed
    2  a required input was missing, so the check could not be performed
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx
import jwt as pyjwt

# Make `app` importable when invoked as `python scripts/verify_supabase.py`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import Settings  # noqa: E402
from app.security.supabase_jwt import (  # noqa: E402
    AuthenticationError,
    build_token_verifier,
)

REQUEST_TIMEOUT = 10.0


@dataclass
class Check:
    name: str
    status: str  # "pass" | "fail" | "skip"
    detail: str

    @property
    def ok(self) -> bool:
        return self.status in ("pass", "skip")


def _short(text: str) -> str:
    return text if len(text) <= 160 else text[:157] + "..."


def check_configuration(settings: Settings) -> Check:
    lines = [
        f"auth_mode={settings.auth_mode}",
        f"issuer={settings.resolved_issuer or 'not derived'}",
        f"jwks_url={settings.resolved_jwks_url or 'not derived'}",
        f"shared_secret_set={settings.shared_secret_value is not None}",
        f"audience_enforced={'yes' if settings.resolved_audience else 'no'}",
    ]
    for warning in settings.configuration_warnings():
        lines.append(f"warning: {warning}")

    if settings.auth_mode == "unconfigured":
        return Check("configuration", "fail", "No Supabase project configured.")
    return Check("configuration", "pass", "; ".join(lines))


def _fetch_json(url: str) -> tuple[int | None, object | None, str | None]:
    try:
        response = httpx.get(url, timeout=REQUEST_TIMEOUT, follow_redirects=True)
    except httpx.HTTPError as exc:
        return None, None, f"{type(exc).__name__}: {exc}"
    try:
        return response.status_code, response.json(), None
    except ValueError:
        return response.status_code, None, "response was not JSON"


def check_jwks(settings: Settings) -> tuple[Check, list[dict]]:
    url = settings.resolved_jwks_url
    if not url:
        return Check("jwks fetch", "fail", "No JWKS URL derived."), []

    status, body, error = _fetch_json(url)
    if error and status is None:
        return Check("jwks fetch", "fail", f"{url} -> {error}"), []
    if status != 200:
        return Check("jwks fetch", "fail", f"{url} -> HTTP {status}. {_short(str(body))}"), []

    keys = body.get("keys") if isinstance(body, dict) else None
    if not isinstance(keys, list) or not keys:
        # Supabase returns no keys unless the project uses asymmetric signing keys.
        return (
            Check(
                "jwks fetch",
                "fail",
                "HTTP 200 but 0 keys published. Supabase publishes no keys unless the "
                "project uses asymmetric JWT signing keys, so the JWKS path cannot work; "
                "this project must be using the legacy shared JWT secret.",
            ),
            [],
        )

    usable = [
        key
        for key in keys
        if isinstance(key, dict)
        and key.get("alg")
        in (
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
        )
    ]
    summary = [
        {
            "kid": key.get("kid"),
            "alg": key.get("alg"),
            "kty": key.get("kty"),
            "use": key.get("use"),
            "key_ops": key.get("key_ops"),
        }
        for key in keys
        if isinstance(key, dict)
    ]
    if not usable:
        return (
            Check("jwks fetch", "fail", f"No usable asymmetric key. Keys: {summary}"),
            keys,
        )

    return (
        Check(
            "jwks fetch",
            "pass",
            f"HTTP 200, {len(keys)} key(s) published: {json.dumps(summary, default=str)}",
        ),
        keys,
    )


def check_openid_configuration(settings: Settings) -> Check:
    """Query the project's OIDC document, which states the issuer authoritatively."""
    if not settings.resolved_issuer:
        return Check("openid configuration", "fail", "No issuer configured.")
    url = f"{settings.resolved_issuer}/.well-known/openid-configuration"
    status, body, error = _fetch_json(url)
    if status != 200:
        return Check(
            "openid configuration",
            "skip",
            f"{url} -> {f'HTTP {status}' if status else error}. "
            "Not published for this project, so the issuer cannot be confirmed here.",
        )

    issuer = body.get("issuer") if isinstance(body, dict) else None
    if issuer is None:
        return Check("openid configuration", "skip", "Document present but no 'issuer' claim.")
    if issuer == settings.resolved_issuer:
        return Check("openid configuration", "pass", f"issuer matches settings: {issuer}")
    return Check(
        "openid configuration",
        "fail",
        f"Issuer mismatch. Document says {issuer}, settings expect {settings.resolved_issuer}.",
    )


def check_token(settings: Settings, token: str) -> Check:
    fingerprint = hashlib.sha256(token.encode()).hexdigest()[:12]

    try:
        header = pyjwt.get_unverified_header(token)
        unverified = pyjwt.decode(token, options={"verify_signature": False, "verify_exp": False})
    except Exception as exc:  # noqa: BLE001 - report, do not crash
        return Check("token", "fail", f"Token is not a readable JWT ({type(exc).__name__}).")

    lines = [
        f"token_sha256={fingerprint} (never printed)",
        f"header.alg={header.get('alg')}",
        f"header.kid={header.get('kid')}",
        f"claim.iss={unverified.get('iss')}",
        f"claim.aud={unverified.get('aud', '<absent>')}",
        f"claim.role={unverified.get('role')}",
        f"claim.exp={unverified.get('exp')}",
    ]

    verifier = build_token_verifier(settings)
    if verifier is None:
        return Check("token", "fail", "No verifier configured.")

    try:
        identity = verifier.verify(token)
    except AuthenticationError as exc:
        return Check("token", "fail", f"REJECTED: {exc}. {'; '.join(lines)}")

    lines.append(f"verified.subject={identity.subject}")
    lines.append(f"verified.role={identity.role}")

    if settings.resolved_audience is None and "aud" in unverified:
        lines.append(
            f"action: set ML_SUPABASE_JWT_AUDIENCE={unverified['aud']!r} to enforce the audience"
        )
    elif settings.resolved_audience is None:
        lines.append(
            "action: token carries no `aud` claim, so leaving the audience unenforced is correct"
        )

    return Check("token", "pass", "; ".join(lines))


def check_database(settings: Settings) -> Check:
    if settings.database_url.startswith("sqlite"):
        return Check(
            "database",
            "skip",
            "Local SQLite in use. PostgreSQL remains unverified.",
        )

    from sqlalchemy import inspect, text

    from app.core.db import create_db_engine

    engine = create_db_engine(settings)
    try:
        with engine.connect() as connection:
            version = connection.execute(text("select version()")).scalar_one()
            tables = inspect(connection).get_table_names()
    except Exception as exc:  # noqa: BLE001
        return Check("database", "fail", f"Could not connect: {type(exc).__name__}: {exc}")
    finally:
        engine.dispose()

    has_profiles = "profiles" in tables
    return Check(
        "database",
        "pass",
        f"Connected. {version.split(' on')[0]}. "
        f"profiles table present={has_profiles}. "
        f"tables={len(tables)}.",
    )


def _read_token(args: argparse.Namespace) -> str | None:
    if args.token_file:
        path = Path(args.token_file).expanduser()
        if not path.is_file():
            raise SystemExit(f"Token file not found: {path}")
        return path.read_text(encoding="utf-8").strip()
    return os.environ.get("ML_VERIFY_ACCESS_TOKEN") or None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--token-file",
        help="Path to a file containing a real Supabase access token.",
    )
    args = parser.parse_args()

    settings = Settings()
    checks: list[Check] = []

    configuration = check_configuration(settings)
    checks.append(configuration)
    if configuration.status == "fail":
        _print(checks)
        return 1

    checks.append(check_openid_configuration(settings))
    jwks_check, _keys = check_jwks(settings)
    checks.append(jwks_check)

    token = _read_token(args)
    if token:
        checks.append(check_token(settings, token))
    else:
        checks.append(
            Check(
                "token",
                "skip",
                "No access token supplied, so issuer/audience could not be confirmed "
                "against a real token. Supply ML_VERIFY_ACCESS_TOKEN or --token-file.",
            )
        )

    checks.append(check_database(settings))
    exit_code = _print(checks)
    return exit_code


def _print(checks: list[Check]) -> int:
    print("\nSupabase sign-in path verification")
    print("=" * 60)
    for check in checks:
        mark = {"pass": "PASS", "fail": "FAIL", "skip": "SKIP"}[check.status]
        print(f"[{mark}] {check.name}")
        print(f"       {check.detail}")
    print("=" * 60)

    if any(check.status == "fail" for check in checks):
        print("Result: FAILED - a required check did not pass.")
        return 1
    if any(check.status == "skip" for check in checks):
        print("Result: INCOMPLETE - one or more checks could not be performed.")
        return 2
    print("Result: PASSED - every check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
