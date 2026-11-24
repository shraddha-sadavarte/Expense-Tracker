"""JSON log lines carry the request ID and extra fields."""

import json
import logging

from app.core.logging import JsonFormatter
from app.core.request_context import request_id_var


def test_json_formatter_includes_request_id_and_extras() -> None:
    record = logging.makeLogRecord(
        {"name": "t", "levelname": "INFO", "msg": "hello", "status": 200}
    )
    token = request_id_var.set("rid-123")
    try:
        line = json.loads(JsonFormatter().format(record))
    finally:
        request_id_var.reset(token)
    assert line["message"] == "hello"
    assert line["request_id"] == "rid-123"
    assert line["status"] == 200
    assert line["level"] == "INFO"
