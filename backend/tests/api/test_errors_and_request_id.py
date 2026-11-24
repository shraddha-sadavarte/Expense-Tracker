"""Doc 5.1 error envelope and request ID propagation."""

import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.errors import AppError
from tests.conftest import make_client


class _Body(BaseModel):
    amount_paise: int


def _add_probe_routes(app: FastAPI) -> None:
    @app.get("/_probe/app-error")
    async def app_error() -> None:
        raise AppError("BUDGET_LIMIT_EXCEEDED", "Over limit", details={"over_by_paise": 15000})

    @app.get("/_probe/crash")
    async def crash() -> None:
        raise RuntimeError("secret internal detail")

    @app.post("/_probe/validate")
    async def validate(body: _Body) -> _Body:
        return body


def _assert_envelope(body: dict[str, object], code: str) -> None:
    assert set(body) == {"error"}
    error = body["error"]
    assert isinstance(error, dict)
    assert set(error) == {"code", "message", "details", "request_id"}
    assert error["code"] == code
    uuid.UUID(str(error["request_id"]))


def test_unknown_route_returns_not_found_envelope(client: TestClient) -> None:
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    _assert_envelope(response.json(), "NOT_FOUND")


def test_app_error_envelope(app: FastAPI) -> None:
    _add_probe_routes(app)
    with make_client(app) as client:
        response = client.get("/_probe/app-error")
    assert response.status_code == 422
    body = response.json()
    _assert_envelope(body, "BUDGET_LIMIT_EXCEEDED")
    assert body["error"]["details"] == {"over_by_paise": 15000}


def test_validation_error_is_400_and_does_not_echo_input(app: FastAPI) -> None:
    _add_probe_routes(app)
    with make_client(app) as client:
        response = client.post("/_probe/validate", json={"amount_paise": "not-a-number-XYZ"})
    assert response.status_code == 400
    _assert_envelope(response.json(), "VALIDATION_ERROR")
    assert "XYZ" not in response.text


def test_unhandled_error_is_500_without_internals(app: FastAPI) -> None:
    _add_probe_routes(app)
    with make_client(app, raise_server_exceptions=False) as client:
        response = client.get("/_probe/crash")
    assert response.status_code == 500
    _assert_envelope(response.json(), "INTERNAL")
    assert "secret internal detail" not in response.text
    assert response.headers["x-request-id"] == response.json()["error"]["request_id"]


def test_request_id_generated_and_echoed(client: TestClient) -> None:
    response = client.get("/health")
    uuid.UUID(response.headers["x-request-id"])


def test_valid_incoming_request_id_is_kept(client: TestClient) -> None:
    rid = str(uuid.uuid4())
    response = client.get("/does-not-exist", headers={"X-Request-ID": rid})
    assert response.headers["x-request-id"] == rid
    assert response.json()["error"]["request_id"] == rid


def test_invalid_incoming_request_id_is_replaced(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "<script>"})
    assert response.headers["x-request-id"] != "<script>"
    uuid.UUID(response.headers["x-request-id"])
