"""Exception handlers that render every error in the Doc 5.1 envelope."""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import STATUS_TO_CODE, AppError, error_body


async def _app_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)  # noqa: S101 - registered for AppError only
    return JSONResponse(error_body(exc.code, exc.message, exc.details), status_code=exc.status_code)


async def _validation_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)  # noqa: S101
    # Never echo the submitted input back (Doc 8.3): keep only location, message, type.
    fields: list[dict[str, Any]] = [
        {"loc": list(err.get("loc", ())), "msg": err.get("msg"), "type": err.get("type")}
        for err in exc.errors()
    ]
    return JSONResponse(
        error_body("VALIDATION_ERROR", "Request validation failed", {"fields": fields}),
        status_code=400,
    )


async def _http_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)  # noqa: S101
    code = STATUS_TO_CODE.get(exc.status_code, "HTTP_ERROR")
    message = exc.detail if isinstance(exc.detail, str) else code
    return JSONResponse(error_body(code, message), status_code=exc.status_code, headers=exc.headers)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
