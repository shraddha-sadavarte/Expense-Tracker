"""/ready against real PostgreSQL and Redis. Run with `make up` first (or in CI)."""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_ready_with_real_services(client: TestClient) -> None:
    response = client.get("/ready")
    assert response.json() == {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}
    assert response.status_code == 200
