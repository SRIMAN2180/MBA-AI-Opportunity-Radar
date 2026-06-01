from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

PingTier = Literal["hot", "warm", "cool"]


Category = Literal[
    "business_competitions",
    "mba_webinars_events",
    "ai_courses",
    "ai_certifications",
    "ai_hackathons",
    "ai_industry_updates",
]


class SourceMetadata(BaseModel):
    source_name: str
    category: Category
    scrape_type: Literal["rss", "html", "api", "manual"]
    url: str
    parsing_strategy: str


class EventItem(BaseModel):
    title: str
    category: Category
    provider: str
    url: str
    summary: str = ""
    published_at: str = ""
    tags: list[str] = Field(default_factory=list)
    mba_relevance_score: int = 0
    mba_ping: PingTier = "cool"
    mba_relevance_reason: str = ""
    scraped_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CourseItem(BaseModel):
    course_title: str
    provider: str
    difficulty_level: str = "Unknown"
    duration: str = "Unknown"
    enrollment_link: str
    release_date: str = ""
    tags: list[str] = Field(default_factory=list)
    category: Category = "ai_courses"
    summary: str = ""
    scraped_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class DigestPayload(BaseModel):
    generated_at: str
    events_count: int
    courses_count: int
    digest_text: str
    digest_html: str


class ApprovalState(BaseModel):
    user_approved: bool = False
    approved_at: str = ""
