from celery import Celery
from celery.schedules import crontab
import os

# Create Celery instance
celery_app = Celery("issues_tracker")

# Configuration
celery_app.conf.update(
    broker_url=os.getenv("REDIS_URL", "redis://redis:6379"),
    result_backend=os.getenv("REDIS_URL", "redis://redis:6379"),
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.worker.tasks.update_daily_stats": {"queue": "stats"},
        "app.worker.tasks.cleanup_old_files": {"queue": "cleanup"},
    },
    beat_schedule={
        "update-daily-stats": {
            "task": "app.worker.tasks.update_daily_stats",
            "schedule": crontab(minute=0, hour=0),  # Run daily at midnight
        },
        "cleanup-old-files": {
            "task": "app.worker.tasks.cleanup_old_files",
            "schedule": crontab(minute=0, hour=2),  # Run daily at 2 AM
        },
        "stats-every-30-min": {
            "task": "app.worker.tasks.update_daily_stats",
            "schedule": crontab(minute="*/30"),  # Run every 30 minutes as required
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.worker"])
