"""FastAPI application factory."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.v1.router import api_v1_router
from app.core.config import Settings, get_settings
from app.core.db import create_db_engine, create_session_factory
from app.core.logging import configure_logging, log_startup_diagnostics
from app.security.supabase_jwt import build_token_verifier

logger = logging.getLogger("mehnatledger.error")


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    log_startup_diagnostics(settings)
    yield
    app.state.db_engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the ASGI application.

    A settings object may be injected for tests; otherwise the process-wide
    environment-derived singleton is used.
    """
    resolved = settings or get_settings()
    configure_logging(resolved)

    app = FastAPI(
        title=resolved.app_name,
        version=__version__,
        lifespan=_lifespan,
        # Interactive docs are a convenience in development and an avoidable
        # surface in production.
        docs_url=None if resolved.is_production else "/docs",
        redoc_url=None,
        openapi_url=None if resolved.is_production else "/openapi.json",
    )
    app.state.settings = resolved

    # The engine connects lazily, so building it here does not require the
    # database to be reachable at import time.
    engine = create_db_engine(resolved)
    app.state.db_engine = engine
    app.state.session_factory = create_session_factory(engine)
    # None when no Supabase project is configured; protected routes then report a
    # setup problem (503) rather than a bad credential (401).
    app.state.token_verifier = build_token_verifier(resolved)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved.cors_origin_list,
        # The API authenticates with bearer tokens, not cookies, so cross-origin
        # credentials are not needed.
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        # Log the exception server-side but return a generic message so that
        # stack traces and internal detail never reach the client.
        logger.exception("Unhandled server error: %s", type(exc).__name__)
        return JSONResponse(status_code=500, content={"detail": "Internal server error."})

    app.include_router(api_v1_router, prefix=resolved.api_v1_prefix)
    return app


app = create_app()
