"""Dependency checks used by GET /ready (Doc 9.1: database and Redis reachable)."""

import asyncio
from collections.abc import Awaitable, Callable

from redis.asyncio import Redis
from sqlalchemy import text

from app.core.config import get_settings
from app.core.db import get_engine

Check = Callable[[], Awaitable[None]]


async def check_database() -> None:
    async with get_engine().connect() as conn:
        await conn.execute(text("SELECT 1"))


async def check_redis() -> None:
    client: Redis = Redis.from_url(get_settings().redis_url)
    try:
        await client.ping()
    finally:
        await client.aclose()


DEFAULT_CHECKS: dict[str, Check] = {"database": check_database, "redis": check_redis}


async def run_checks(checks: dict[str, Check], timeout_s: float) -> dict[str, str]:
    """Return {"database": "ok" | "error", ...}. Never raises."""

    async def one(check: Check) -> str:
        try:
            await asyncio.wait_for(check(), timeout=timeout_s)
        except Exception:
            return "error"
        return "ok"

    results = await asyncio.gather(*(one(c) for c in checks.values()))
    return dict(zip(checks.keys(), results, strict=True))
