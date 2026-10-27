"""Pydantic response schemas for system endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness payload. Contains no configuration or secret detail."""

    status: Literal["ok"] = "ok"
    service: str
    environment: str
    api_version: str


class ProviderCapability(BaseModel):
    """Configuration state of a single external capability.

    ``api_key_configured`` reports only that a credential string was supplied.
    It does not mean the credential is valid, the provider is reachable or the
    integration has been tested.
    """

    provider: str
    mode: str
    api_key_configured: bool
    base_url_configured: bool
    integration_verified: bool = False


class CapabilitiesResponse(BaseModel):
    """What the running server can actually do right now.

    This endpoint is intentionally unauthenticated and therefore exposes only
    booleans, enum labels and limits -- never URLs, keys or internal details.
    """

    service: str
    environment: str
    speech_to_text: ProviderCapability
    text_to_speech: ProviderCapability
    reasoning: ProviderCapability
    voice_enabled: bool
    manual_entry_available: bool = True
    voice_max_audio_seconds: int
    voice_daily_drafts_per_user: int
    server_time: datetime = Field(description="Server time in UTC (ISO 8601).")
