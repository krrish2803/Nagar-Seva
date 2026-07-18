"""Celery tasks package."""

from .celery_tasks import celery_app, escalate_overdue_complaints

__all__ = ["celery_app", "escalate_overdue_complaints"]
