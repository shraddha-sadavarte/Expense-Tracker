"""Application error type and the Doc 5.1 error envelope.

Shape: {"error": {"code", "message", "details", "request_id"}}
"""

from typing import Any

from app.core.request_context import get_request_id

# Doc 5.1 common error codes by HTTP status.
STATUS_TO_CODE: dict[int, str] = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHENTICATED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "BUSINESS_RULE_VIOLATION",
    429: "RATE_LIMITED",
    500: "INTERNAL",
    503: "SERVICE_UNAVAILABLE",
}


class AppError(Exception):
    """Raise from services; the API layer turns it into the error envelope."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 422,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppError):
    """Also used for objects owned by another user, so existence is never leaked."""

    def __init__(self, message: str = "Not found") -> None:
        super().__init__("NOT_FOUND", message, status_code=404)


def error_body(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "request_id": get_request_id(),
        }
    }
