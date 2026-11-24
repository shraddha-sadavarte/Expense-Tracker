"""Application factory: settings, logging, middleware, error handlers, routers."""

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.middleware.error_mapping import register_error_handlers
from app.api.middleware.request_id import RequestIdMiddleware
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="Expense Tracker API",
        version="0.1.0",
        docs_url="/docs" if settings.app_env != "production" else None,
        redoc_url=None,
    )
    register_error_handlers(app)
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health_router)
    app.include_router(api_router)
    return app
