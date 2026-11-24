"""Celery Beat schedule (Doc 8.5). Beat runs as exactly one instance. Empty until features exist."""

from typing import Any

BEAT_SCHEDULE: dict[str, dict[str, Any]] = {}
