"""Liveness and readiness probes (Doc 9.1). Public, outside /api/v1."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api.deps import get_readiness_checks
from app.core.config import get_settings
from app.core.health import Check, run_checks

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"]


class ReadyResponse(BaseModel):
    status: Literal["ok", "unavailable"]
    checks: dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness: the process is up. Touches no dependencies."""
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadyResponse, responses={503: {"model": ReadyResponse}})
async def ready(
    checks: Annotated[dict[str, Check], Depends(get_readiness_checks)],
) -> JSONResponse:
    """Readiness: database and Redis reachable. 503 if any check fails."""
    results = await run_checks(checks, get_settings().readiness_timeout_s)
    healthy = all(v == "ok" for v in results.values())
    body = ReadyResponse(status="ok" if healthy else "unavailable", checks=results)
    return JSONResponse(body.model_dump(), status_code=200 if healthy else 503)
