"""Typed application configuration.

Design rules enforced here:

* Every setting is loaded from the environment (optionally a git-ignored
  ``.env`` file) using the ``ML_`` prefix.
* Secrets are held in :class:`pydantic.SecretStr` so that accidental logging,
  ``repr(settings)`` or FastAPI response serialisation shows ``**********``
  instead of the value.
* Nothing in this module infers that a provider is *usable*, only whether a
  credential has been supplied. Provider access, endpoints, supported languages
  and quotas have NOT been verified against official documentation.
* Unsafe production configurations fail fast at startup instead of failing open.
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from typing import Any

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Local development default. Must never be used in production.
DEV_DATABASE_URL = "sqlite+pysqlite:///./mehnatledger_dev.db"

SUPPORTED_DATABASE_SCHEMES = ("sqlite+pysqlite://", "postgresql+psycopg://")


class Environment(StrEnum):
    """Deployment environment."""

    development = "development"
    test = "test"
    production = "production"


class ProviderMode(StrEnum):
    """How a provider-backed capability is wired up.

    These modes are deliberately distinct so that reports and the UI can never
    present a mock as a live integration.
    """

    disabled = "disabled"
    mock = "mock"
    local = "local"
    live = "live"


class Settings(BaseSettings):
    """Application settings loaded from the environment."""

    model_config = SettingsConfigDict(
        env_prefix="ML_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application ---------------------------------------------------------
    app_name: str = "MehnatLedger API"
    environment: Environment = Environment.development
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    # --- Database ------------------------------------------------------------
    database_url: str = DEV_DATABASE_URL

    # --- API access ----------------------------------------------------------
    # Stored as a raw string and exposed through `cors_origin_list` so that a
    # plain comma-separated environment variable works without JSON quoting.
    cors_origins: str = "http://localhost:5173"

    # --- Gnani speech providers (not integrated; access unverified) ----------
    gnani_stt_api_key: SecretStr | None = None
    gnani_stt_base_url: str | None = None
    gnani_tts_api_key: SecretStr | None = None
    gnani_tts_base_url: str | None = None

    # --- Reasoning / extraction provider (not selected) ---------------------
    reasoning_mode: ProviderMode = ProviderMode.disabled
    reasoning_base_url: str | None = None
    reasoning_api_key: SecretStr | None = None

    # --- Voice usage limits (applied once voice endpoints exist) ------------
    voice_max_audio_seconds: int = Field(default=60, ge=1, le=600)
    voice_daily_drafts_per_user: int = Field(default=20, ge=0, le=1000)

    # --- Validators ----------------------------------------------------------

    @field_validator("database_url")
    @classmethod
    def _validate_database_url(cls, value: str) -> str:
        if not value.startswith(SUPPORTED_DATABASE_SCHEMES):
            supported = ", ".join(SUPPORTED_DATABASE_SCHEMES)
            raise ValueError(f"database_url must start with one of: {supported}")
        return value

    @field_validator("log_level")
    @classmethod
    def _validate_log_level(cls, value: str) -> str:
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        normalised = value.upper()
        if normalised not in allowed:
            raise ValueError(f"log_level must be one of: {', '.join(sorted(allowed))}")
        return normalised

    @model_validator(mode="after")
    def _reject_unsafe_production_configuration(self) -> Settings:
        if self.environment is not Environment.production:
            return self

        if self.database_url == DEV_DATABASE_URL:
            raise ValueError(
                "Refusing to start in production with the development default "
                "database_url; configure a real PostgreSQL connection."
            )
        if "*" in self.cors_origin_list:
            raise ValueError(
                "Refusing to start in production with a wildcard CORS origin; "
                "list explicit origins instead."
            )
        return self

    # --- Derived values ------------------------------------------------------

    @property
    def cors_origin_list(self) -> list[str]:
        """CORS origins as a list, parsed from the comma-separated setting."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment is Environment.production

    def provider_status(self) -> dict[str, Any]:
        """Report provider configuration **without** exposing any secret value.

        Only booleans and enumerated modes are returned. ``*_configured`` means
        "a credential string was supplied"; it does not prove the provider
        accepts it or that the integration works.
        """
        stt_key = self.gnani_stt_api_key
        tts_key = self.gnani_tts_api_key
        reasoning_key = self.reasoning_api_key

        return {
            "speech_to_text": {
                "provider": "gnani_prisma",
                "mode": ProviderMode.live.value if stt_key else ProviderMode.disabled.value,
                "api_key_configured": bool(stt_key),
                "base_url_configured": bool(self.gnani_stt_base_url),
                "integration_verified": False,
            },
            "text_to_speech": {
                "provider": "gnani_timbre",
                "mode": ProviderMode.live.value if tts_key else ProviderMode.disabled.value,
                "api_key_configured": bool(tts_key),
                "base_url_configured": bool(self.gnani_tts_base_url),
                "integration_verified": False,
            },
            "reasoning": {
                "provider": "unselected",
                "mode": self.reasoning_mode.value,
                "api_key_configured": bool(reasoning_key),
                "base_url_configured": bool(self.reasoning_base_url),
                "integration_verified": False,
            },
            "voice_enabled": False,
            "manual_entry_available": True,
        }

    def configuration_warnings(self) -> list[str]:
        """Human-readable, secret-free warnings about the current configuration."""
        warnings: list[str] = []

        if self.gnani_stt_api_key and not self.gnani_stt_base_url:
            warnings.append(
                "ML_GNANI_STT_API_KEY is set but ML_GNANI_STT_BASE_URL is empty; "
                "speech-to-text cannot be called."
            )
        if self.gnani_tts_api_key and not self.gnani_tts_base_url:
            warnings.append(
                "ML_GNANI_TTS_API_KEY is set but ML_GNANI_TTS_BASE_URL is empty; "
                "text-to-speech cannot be called."
            )
        if self.reasoning_mode is ProviderMode.live and not self.reasoning_api_key:
            warnings.append(
                "ML_REASONING_MODE=live but no ML_REASONING_API_KEY is set; "
                "reasoning extraction will be unavailable."
            )
        if self.reasoning_mode in (ProviderMode.local, ProviderMode.live):
            warnings.append(
                f"ML_REASONING_MODE={self.reasoning_mode.value} is configured but no reasoning "
                "provider has been approved for this project; treat extraction as non-functional."
            )
        if not self.is_production and self.database_url == DEV_DATABASE_URL:
            warnings.append(
                "Using the local development SQLite database. PostgreSQL is the "
                "production target; see README.md."
            )
        return warnings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""
    return Settings()
