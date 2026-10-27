"""Tests for the system endpoints and error-response safety."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

# An obviously fake placeholder. It is a test fixture, not a real credential,
# and is never used to call any provider.
FAKE_GNANI_KEY = "FAKE-GNANI-KEY-NOT-A-REAL-CREDENTIAL"
FAKE_GNANI_BASE_URL = "https://fake-gnani-endpoint.invalid/v1"


def test_health_reports_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["api_version"] == "v1"
    assert body["environment"] == "test"


def test_default_capabilities_report_voice_unavailable(client: TestClient) -> None:
    """With no credentials configured, voice must report as disabled, not ready."""
    response = client.get("/api/v1/system/capabilities")

    assert response.status_code == 200
    body = response.json()
    assert body["speech_to_text"]["api_key_configured"] is False
    assert body["text_to_speech"]["api_key_configured"] is False
    assert body["reasoning"]["mode"] == "disabled"
    assert body["voice_enabled"] is False
    assert body["manual_entry_available"] is True
    assert body["voice_max_audio_seconds"] == 60


def test_capabilities_never_expose_credential_or_base_url(
    settings_factory,
) -> None:
    """A configured key must still never appear in any API response body."""
    settings: Settings = settings_factory(
        gnani_stt_api_key=FAKE_GNANI_KEY,
        gnani_stt_base_url=FAKE_GNANI_BASE_URL,
    )
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/system/capabilities")

    assert response.status_code == 200
    raw = response.text
    assert FAKE_GNANI_KEY not in raw
    assert FAKE_GNANI_BASE_URL not in raw

    body = response.json()
    # It reports only that a value exists...
    assert body["speech_to_text"]["api_key_configured"] is True
    # ...and must never claim the integration is verified.
    assert body["speech_to_text"]["integration_verified"] is False
    assert body["voice_enabled"] is False


def test_capabilities_lists_only_known_fields(settings_factory) -> None:
    """Guard against accidentally widening the unauthenticated payload."""
    settings: Settings = settings_factory(gnani_tts_api_key=FAKE_GNANI_KEY)
    with TestClient(create_app(settings)) as client:
        body = client.get("/api/v1/system/capabilities").json()

    assert set(body) == {
        "service",
        "environment",
        "speech_to_text",
        "text_to_speech",
        "reasoning",
        "voice_enabled",
        "manual_entry_available",
        "voice_max_audio_seconds",
        "voice_daily_drafts_per_user",
        "server_time",
    }


def test_unhandled_errors_do_not_leak_internals(settings: Settings) -> None:
    """An unexpected exception returns a generic message, not a stack trace."""
    app = create_app(settings)
    secret_detail = "internal-detail-that-must-not-leak"

    @app.get("/boom")
    async def boom() -> None:  # pragma: no cover - only reached via the test client
        raise RuntimeError(secret_detail)

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}
    assert secret_detail not in response.text
