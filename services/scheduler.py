"""APScheduler configuration for periodic tasks."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from typing import List, Optional

from services.tasks import periodic_option_collection_task

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the global scheduler instance."""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
    return scheduler


def start_scheduler(symbols: Optional[List[str]] = None):
    """
    Start the scheduler with default periodic tasks.
    
    Args:
        symbols: List of symbols to collect. If None, uses default watchlist.
    """
    sched = get_scheduler()
    
    # Schedule option chain collection every 15 minutes during market hours
    # Market hours: 9:30 AM - 4:00 PM ET (14:30 - 21:00 UTC)
    sched.add_job(
        periodic_option_collection_task,
        trigger=CronTrigger(
            minute='*/15',  # Every 15 minutes
            hour='14-21',   # 9:30 AM - 4:00 PM ET
            day_of_week='mon-fri'  # Weekdays only
        ),
        id='periodic_option_collection',
        name='Periodic Option Chain Collection',
        replace_existing=True,
        kwargs={'symbols': symbols},
    )
    
    sched.start()
    logger.info("Scheduler started with periodic option collection task")


def stop_scheduler():
    """Stop the scheduler."""
    sched = get_scheduler()
    if sched.running:
        sched.shutdown()
        logger.info("Scheduler stopped")

