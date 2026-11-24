"""Request dependencies. Current-user and idempotency dependencies arrive with auth."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import session_scope
from app.core.health import DEFAULT_CHECKS, Check


async def get_session() -> AsyncIterator[AsyncSession]:
    async for session in session_scope():
        yield session


def get_readiness_checks() -> dict[str, Check]:
    return DEFAULT_CHECKS
