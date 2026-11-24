"""/health and /ready endpoints (Doc 9.1)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_readiness_checks
from app.core.health import Check


async def _ok() -> None:
    return None


async def _fail() -> None:
    raise ConnectionError("down")


def _with_checks(app: FastAPI, checks: dict[str, Check]) -> TestClient:
    app.dependency_overrides[get_readiness_checks] = lambda: checks
    return TestClient(app)


def test_health_is_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_ok_when_all_checks_pass(app: FastAPI) -> None:
    with _with_checks(app, {"database": _ok, "redis": _ok}) as client:
        response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}


def test_ready_503_when_a_check_fails(app: FastAPI) -> None:
    with _with_checks(app, {"database": _ok, "redis": _fail}) as client:
        response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "checks": {"database": "ok", "redis": "error"},
    }
