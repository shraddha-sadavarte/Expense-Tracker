"""Shared fixtures. Default URLs point at the Docker Compose services on localhost."""

import os
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://expense:change-me@localhost:5432/expense"
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.main import create_app


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c
