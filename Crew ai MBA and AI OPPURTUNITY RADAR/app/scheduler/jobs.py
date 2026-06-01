from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.emailer.digest import build_digest, send_digest_email
from app.scraper.pipeline import run_full_scrape
from app.storage.json_store import JsonStore
from app.storage.sqlite_store import SQLiteStore

scheduler = BackgroundScheduler(timezone=settings.timezone)
_store = JsonStore()
_sqlite = SQLiteStore()


def weekly_refresh_job() -> None:
    events, courses, scrape_health = run_full_scrape()
    dataset = _store.save_dataset(events, courses, scrape_health)
    _sqlite.upsert_events(events)
    _sqlite.upsert_courses(courses)
    digest = build_digest(dataset)
    approval = _store.load_approval()
    send_digest_email(
        subject="Weekly MBA + AI Opportunity Radar",
        digest_html=digest.digest_html,
        user_approved=approval.user_approved,
    )
    _store.save_approval(False)


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(
        weekly_refresh_job,
        CronTrigger(
            day_of_week=settings.scheduler_cron_day,
            hour=settings.scheduler_cron_hour,
            minute=settings.scheduler_cron_minute,
        ),
        id="weekly_refresh_job",
        replace_existing=True,
    )
    scheduler.start()
