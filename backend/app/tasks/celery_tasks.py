"""Celery asynchronous tasks for NagarSeva backend."""

from celery import Celery, Task
from app.config import settings
from app.agents.escalation_agent import orchestrate_escalation_check
from app.utils.database import close_mongo_connection, get_database
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Initialize Celery app
celery_app = Celery(
    "nagarseva_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
)


class CallbackTask(Task):
    """Task base class with error callback handling."""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True


@celery_app.task(base=CallbackTask, bind=True)
def escalate_overdue_complaints(self) -> dict:
    """
    Periodic task to check and escalate overdue complaints.

    Runs every hour based on schedule in beat_schedule.

    Returns:
        Dictionary with escalation results
    """
    try:
        print("[CELERY] Starting escalation task")

        # Run async function
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(orchestrate_escalation_check())

        print(f"[CELERY] Escalation task complete: {results}")
        return results

    except Exception as e:
        print(f"[CELERY] Error in escalation task: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60)


@celery_app.task(base=CallbackTask)
def generate_heatmap_snapshot() -> dict:
    """
    Task to generate periodic heatmap snapshots.

    Returns:
        Heatmap generation results
    """
    try:
        print("[CELERY] Starting heatmap snapshot generation")
        from app.agents.heatmap_agent import orchestrate_heatmap_generation

        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            orchestrate_heatmap_generation(
                days_lookback=30,
                ward_id=None,
                eps_meters=500,
            )
        )

        print(f"[CELERY] Heatmap snapshot complete: {len(results)} clusters")
        return {"status": "success", "clusters_generated": len(results)}

    except Exception as e:
        print(f"[CELERY] Error in heatmap task: {e}")
        raise


@celery_app.task(base=CallbackTask)
def send_pending_notifications() -> dict:
    """
    Task to process and send pending notifications.

    Returns:
        Notification processing results
    """
    try:
        print("[CELERY] Processing pending notifications")

        async def process_notifications() -> dict:
            db = await get_database()
            cursor = db["notifications"].find({"status": "pending"}).limit(100)
            sent = 0
            async for notification in cursor:
                await db["notifications"].update_one(
                    {"_id": notification["_id"]},
                    {
                        "$set": {
                            "status": "sent",
                            "sent_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow(),
                        }
                    },
                )
                sent += 1
            await close_mongo_connection()
            return {"status": "success", "notifications_sent": sent}

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(process_notifications())

    except Exception as e:
        print(f"[CELERY] Error in notification task: {e}")
        raise


@celery_app.task(base=CallbackTask)
def cleanup_old_data() -> dict:
    """
    Task to cleanup old complaints and logs.

    Returns:
        Cleanup results
    """
    try:
        print("[CELERY] Starting data cleanup")

        async def cleanup() -> dict:
            db = await get_database()
            cutoff = datetime.utcnow() - timedelta(days=90)
            archive_result = await db["complaints"].update_many(
                {
                    "status": "resolved",
                    "updated_at": {"$lt": cutoff},
                    "archived": {"$ne": True},
                },
                {
                    "$set": {
                        "archived": True,
                        "archived_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                    }
                },
            )

            files_deleted = 0
            upload_root = Path(settings.upload_dir)
            file_cutoff = datetime.utcnow() - timedelta(days=30)
            if upload_root.exists():
                for path in upload_root.rglob("*"):
                    if not path.is_file():
                        continue
                    modified_at = datetime.utcfromtimestamp(path.stat().st_mtime)
                    if modified_at < file_cutoff:
                        path.unlink()
                        files_deleted += 1

            await close_mongo_connection()
            return {
                "status": "success",
                "records_archived": archive_result.modified_count,
                "files_deleted": files_deleted,
            }

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(cleanup())

    except Exception as e:
        print(f"[CELERY] Error in cleanup task: {e}")
        raise


# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "escalate-overdue-complaints": {
        "task": "app.tasks.celery_tasks.escalate_overdue_complaints",
        "schedule": 3600.0,  # Every hour
        "options": {"queue": "default", "expires": 3600},
    },
    "generate-heatmap-snapshot": {
        "task": "app.tasks.celery_tasks.generate_heatmap_snapshot",
        "schedule": 86400.0,  # Every 24 hours
        "options": {"queue": "default", "expires": 86400},
    },
    "send-pending-notifications": {
        "task": "app.tasks.celery_tasks.send_pending_notifications",
        "schedule": 600.0,  # Every 10 minutes
        "options": {"queue": "default", "expires": 600},
    },
    "cleanup-old-data": {
        "task": "app.tasks.celery_tasks.cleanup_old_data",
        "schedule": 604800.0,  # Every 7 days
        "options": {"queue": "default", "expires": 604800},
    },
}
