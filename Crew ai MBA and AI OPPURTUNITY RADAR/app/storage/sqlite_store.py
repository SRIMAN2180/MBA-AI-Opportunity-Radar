from __future__ import annotations

import sqlite3
from pathlib import Path

from app.config import settings
from app.models import CourseItem, EventItem


class SQLiteStore:
    """Optional lightweight persistence for querying history."""

    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = Path(db_path or settings.sqlite_file)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    category TEXT,
                    provider TEXT,
                    url TEXT UNIQUE,
                    summary TEXT,
                    published_at TEXT,
                    tags TEXT,
                    scraped_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_title TEXT,
                    provider TEXT,
                    difficulty_level TEXT,
                    duration TEXT,
                    enrollment_link TEXT UNIQUE,
                    release_date TEXT,
                    tags TEXT,
                    category TEXT,
                    scraped_at TEXT
                )
                """
            )

    def upsert_events(self, events: list[EventItem]) -> None:
        with self._connect() as conn:
            for item in events:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO events
                    (title, category, provider, url, summary, published_at, tags, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item.title,
                        item.category,
                        item.provider,
                        item.url,
                        item.summary,
                        item.published_at,
                        ",".join(item.tags),
                        item.scraped_at,
                    ),
                )

    def upsert_courses(self, courses: list[CourseItem]) -> None:
        with self._connect() as conn:
            for item in courses:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO courses
                    (course_title, provider, difficulty_level, duration, enrollment_link, release_date, tags, category, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item.course_title,
                        item.provider,
                        item.difficulty_level,
                        item.duration,
                        item.enrollment_link,
                        item.release_date,
                        ",".join(item.tags),
                        item.category,
                        item.scraped_at,
                    ),
                )
