"""Request ID + access log + last-resort 500 handler (pure ASGI middleware).

- Takes `X-Request-ID` from the client if it is a valid UUID, else generates one.
- Binds it to a context variable so every log line and error body carries it.
- Echoes it back in the `X-Request-ID` response header.
- Turns any unhandled exception into the Doc 5.1 500 envelope (never echoing
  internals), so the request ID is still present on crashes.
"""

import json
import logging
import time
import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.errors import error_body
from app.core.request_context import request_id_var

HEADER = "x-request-id"
logger = logging.getLogger("app.access")


def _incoming_id(scope: Scope) -> str | None:
    for name, value in scope.get("headers", []):
        if name == HEADER.encode():
            try:
                return str(uuid.UUID(value.decode("latin-1")))
            except ValueError:
                return None
    return None


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = _incoming_id(scope) or str(uuid.uuid4())
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        status_code = 500
        response_started = False

        async def send_with_id(message: Message) -> None:
            nonlocal status_code, response_started
            if message["type"] == "http.response.start":
                response_started = True
                status_code = message["status"]
                headers = list(message.get("headers", []))
                headers.append((HEADER.encode(), request_id.encode()))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        except Exception:
            logger.exception("unhandled_error")
            if response_started:
                raise
            body = json.dumps(error_body("INTERNAL", "Internal server error")).encode()
            await send_with_id(
                {
                    "type": "http.response.start",
                    "status": 500,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send({"type": "http.response.body", "body": body})
        finally:
            logger.info(
                "request",
                extra={
                    "method": scope.get("method"),
                    "path": scope.get("path"),  # path only: query strings may hold sensitive data
                    "status": status_code,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                },
            )
            request_id_var.reset(token)
