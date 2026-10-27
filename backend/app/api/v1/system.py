"""System endpoints: liveness and capability reporting.

Nothing here mutates data, and nothing here returns a credential value.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Request

from app.core.config import Settings
from app.schemas.system import CapabilitiesResponse, HealthResponse, ProviderCapability

router = APIRouter()


def _settings(request: Request) -> Settings:
    return request.app.state.settings


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness check",
    description="Returns a static liveness payload. Contains no configuration detail.",
)
async def health(request: Request) -> HealthResponse:
    settings = _settings(request)
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.environment.value,
        api_version="v1",
    )


@router.get(
    "/system/capabilities",
    response_model=CapabilitiesResponse,
    summary="Report which capabilities are actually configured",
    description=(
        "Reports booleans and enum labels only. No API key, base URL or other "
        "credential value is included. `api_key_configured` means a credential "
        "string was supplied; it does NOT mean the provider is reachable or that "
        "the integration has been verified."
    ),
)
async def capabilities(request: Request) -> CapabilitiesResponse:
    settings = _settings(request)
    status = settings.provider_status()

    return CapabilitiesResponse(
        service=settings.app_name,
        environment=settings.environment.value,
        speech_to_text=ProviderCapability(**status["speech_to_text"]),
        text_to_speech=ProviderCapability(**status["text_to_speech"]),
        reasoning=ProviderCapability(**status["reasoning"]),
        voice_enabled=status["voice_enabled"],
        manual_entry_available=status["manual_entry_available"],
        voice_max_audio_seconds=settings.voice_max_audio_seconds,
        voice_daily_drafts_per_user=settings.voice_daily_drafts_per_user,
        server_time=datetime.now(UTC),
    )
