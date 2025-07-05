from celery import shared_task
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Issue, DailyStats, IssueStatus
from datetime import datetime, date
import os
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def update_daily_stats(self):
    """
    Background task to update daily statistics.
    Runs every 30 minutes to aggregate issue counts by status.
    """
    try:
        # Get database session
        db = next(get_db())
        
        today = date.today()
        
        # Count issues by status
        open_count = db.query(Issue).filter(Issue.status == IssueStatus.OPEN).count()
        triaged_count = db.query(Issue).filter(Issue.status == IssueStatus.TRIAGED).count()
        in_progress_count = db.query(Issue).filter(Issue.status == IssueStatus.IN_PROGRESS).count()
        done_count = db.query(Issue).filter(Issue.status == IssueStatus.DONE).count()
        
        # Check if stats for today already exist
        existing_stats = db.query(DailyStats).filter(DailyStats.date == today).first()
        
        if existing_stats:
            # Update existing record
            existing_stats.open_count = open_count
            existing_stats.triaged_count = triaged_count
            existing_stats.in_progress_count = in_progress_count
            existing_stats.done_count = done_count
            logger.info(f"Updated daily stats for {today}")
        else:
            # Create new record
            new_stats = DailyStats(
                date=today,
                open_count=open_count,
                triaged_count=triaged_count,
                in_progress_count=in_progress_count,
                done_count=done_count
            )
            db.add(new_stats)
            logger.info(f"Created new daily stats for {today}")
        
        db.commit()
        db.close()
        
        return {
            "status": "success",
            "date": str(today),
            "open_count": open_count,
            "triaged_count": triaged_count,
            "in_progress_count": in_progress_count,
            "done_count": done_count
        }
        
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@shared_task(bind=True)
def cleanup_old_files(self):
    """
    Background task to cleanup old uploaded files.
    Runs daily to remove files older than 30 days.
    """
    try:
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            return {"status": "success", "message": "No uploads directory found"}
        
        current_time = datetime.now()
        deleted_files = []
        
        for filename in os.listdir(uploads_dir):
            file_path = os.path.join(uploads_dir, filename)
            if os.path.isfile(file_path):
                # Get file modification time
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                # Delete files older than 30 days
                if (current_time - file_time).days > 30:
                    try:
                        os.remove(file_path)
                        deleted_files.append(filename)
                        logger.info(f"Deleted old file: {filename}")
                    except OSError as e:
                        logger.error(f"Error deleting file {filename}: {e}")
        
        return {
            "status": "success",
            "deleted_files": deleted_files,
            "count": len(deleted_files)
        }
        
    except Exception as exc:
        logger.error(f"Cleanup task failed: {exc}")
        raise self.retry(exc=exc, countdown=300, max_retries=3)
