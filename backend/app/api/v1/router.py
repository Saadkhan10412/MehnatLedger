"""Aggregate router for API version 1.

Feature routers (business ledger, worker ledger, shared hisaab, voice) are
added here as each phase lands. Nothing is mounted before it exists.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import system

api_v1_router = APIRouter()
api_v1_router.include_router(system.router, tags=["system"])
