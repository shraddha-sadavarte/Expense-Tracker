"""Structured JSON logging. Every line carries the current request ID.

Never log OTPs, tokens, full VPAs, account numbers, statement contents or raw
LLM prompts (Doc 8.1).
"""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from app.core.request_context import get_request_id

# Attributes every LogRecord has; anything else was passed via `extra=` and is emitted.
_STANDARD_ATTRS = frozenset(vars(logging.makeLogRecord({})).keys()) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": get_request_id(),
        }
        for key, value in vars(record).items():
            if key not in _STANDARD_ATTRS and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
    # Our middleware writes one access line per request; silence the duplicate.
    logging.getLogger("uvicorn.access").disabled = True
