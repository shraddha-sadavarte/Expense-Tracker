"""Shared fixtures. Default URLs point at the Docker Compose services on this machine.

127.0.0.1 (not "localhost"): on Windows, "localhost" tries IPv6 ::1 first and
only falls back after ~2 s, which is longer than the /ready check timeout.
"""

import asyncio
import os
import sys
from collections.abc import Iterator
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://expense:change-me@127.0.0.1:5433/expense"
)
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6379/0")

from app.main import create_app

# psycopg's async mode cannot run on Windows' default Proactor event loop.
# Production and CI run on Linux, where this is not needed.
BACKEND_OPTIONS: dict[str, Any] = (
    {"loop_factory": asyncio.SelectorEventLoop} if sys.platform == "win32" else {}
)


def make_client(app: FastAPI, **kwargs: Any) -> TestClient:
    return TestClient(app, backend_options=BACKEND_OPTIONS, **kwargs)


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with make_client(app) as c:
        yield c
