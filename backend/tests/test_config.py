"""Tests for configuration validation and secret handling."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import DEV_DATABASE_URL, Environment, ProviderMode, Settings

# Test-only placeholder values. Not real credentials.
FAKE_KEY = "FAKE-REASONING-KEY-NOT-A-REAL-CREDENTIAL"

POSTGRES_URL = "postgresql+psycopg://user:password@localhost:5432/mehnatledger"


def _settings(**overrides) -> Settings:
    values = {"_env_file": None}
    values.update(overrides)
    return Settings(**values)


def test_unsupported_database_scheme_is_rejected() -> None:
    with pytest.raises(ValidationError, match="database_url must start with"):
        _settings(database_url="mysql+pymysql://user@localhost/db")


def test_supported_database_schemes_are_accepted() -> None:
    assert _settings(database_url=DEV_DATABASE_URL).database_url == DEV_DATABASE_URL
    assert _settings(database_url=POSTGRES_URL).database_url == POSTGRES_URL


def test_invalid_log_level_is_rejected() -> None:
    with pytest.raises(ValidationError, match="log_level must be one of"):
        _settings(log_level="verbose")


def test_production_rejects_development_database() -> None:
    with pytest.raises(ValidationError, match="development default"):
        _settings(environment=Environment.production, database_url=DEV_DATABASE_URL)


def test_production_rejects_wildcard_cors_origin() -> None:
    with pytest.raises(ValidationError, match="wildcard CORS origin"):
        _settings(
            environment=Environment.production,
            database_url=POSTGRES_URL,
            cors_origins="https://app.example.com,*",
        )


def test_production_accepts_explicit_configuration() -> None:
    settings = _settings(
        environment=Environment.production,
        database_url=POSTGRES_URL,
        cors_origins="https://app.example.com",
    )
    assert settings.is_production is True
    assert settings.cors_origin_list == ["https://app.example.com"]


def test_cors_origins_are_parsed_and_trimmed() -> None:
    settings = _settings(cors_origins=" http://localhost:5173 , https://a.example.com ,, ")
    assert settings.cors_origin_list == ["http://localhost:5173", "https://a.example.com"]


def test_secret_value_is_masked_in_repr_and_dump() -> None:
    """SecretStr must mask the value in the representations we might log."""
    settings = _settings(reasoning_api_key=FAKE_KEY)

    assert FAKE_KEY not in repr(settings)
    assert FAKE_KEY not in str(settings.model_dump())
    assert FAKE_KEY not in repr(settings.model_dump())
    # The value is still reachable deliberately, on the server only.
    assert settings.reasoning_api_key is not None
    assert settings.reasoning_api_key.get_secret_value() == FAKE_KEY


def test_provider_status_reports_configuration_without_values() -> None:
    settings = _settings(
        gnani_stt_api_key=FAKE_KEY,
        reasoning_mode=ProviderMode.mock,
    )
    status = settings.provider_status()

    assert status["speech_to_text"]["api_key_configured"] is True
    assert status["speech_to_text"]["mode"] == "live"
    assert status["text_to_speech"]["api_key_configured"] is False
    assert status["reasoning"]["mode"] == "mock"
    # Never claim unverified work as verified.
    assert status["speech_to_text"]["integration_verified"] is False
    assert status["voice_enabled"] is False
    assert FAKE_KEY not in str(status)


def test_warning_when_key_present_without_base_url() -> None:
    warnings = _settings(gnani_stt_api_key=FAKE_KEY).configuration_warnings()
    assert any("ML_GNANI_STT_BASE_URL is empty" in w for w in warnings)


def test_warning_when_live_reasoning_has_no_key() -> None:
    warnings = _settings(reasoning_mode=ProviderMode.live).configuration_warnings()
    assert any("no ML_REASONING_API_KEY" in w for w in warnings)


def test_warning_when_reasoning_provider_not_approved() -> None:
    """No reasoning provider has been approved, so local/live must warn."""
    warnings = _settings(
        reasoning_mode=ProviderMode.local,
        reasoning_api_key=FAKE_KEY,
    ).configuration_warnings()
    assert any("no reasoning provider has been approved" in w for w in warnings)


def test_default_environment_is_development() -> None:
    settings = _settings()
    assert settings.environment is Environment.development
    assert settings.reasoning_mode is ProviderMode.disabled
