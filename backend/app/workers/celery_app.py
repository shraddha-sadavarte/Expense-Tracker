"""Celery configuration, queues and routing (Doc 9.1).

Four queues so a slow import or an LLM outage never delays a budget alert:
critical (budget evaluation, notifications), sync (imports, AA), ai, reports.
"""

from celery import Celery
from kombu import Queue

from app.core.config import get_settings
from app.workers.schedules import BEAT_SCHEDULE

QUEUES = ("critical", "sync", "ai", "reports")

settings = get_settings()

celery_app = Celery("expense", broker=settings.redis_url, include=["app.workers.tasks"])
celery_app.conf.update(
    task_queues=[Queue(name) for name in QUEUES],
    task_default_queue="critical",
    task_acks_late=True,  # tasks are idempotent, so redelivery after a crash is safe
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule=BEAT_SCHEDULE,
    broker_connection_retry_on_startup=True,
)
