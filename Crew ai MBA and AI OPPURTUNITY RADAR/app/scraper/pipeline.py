from __future__ import annotations

from dataclasses import dataclass, field

from app.models import CourseItem, EventItem, SourceMetadata
from app.scoring.mba_relevance import calculate_mba_relevance
from app.scraper.exa_fallback import EXA_QUERIES, exa_search
from app.scraper.fetchers import is_quality_item
from app.scraper.parsers import EXA_FALLBACK_SOURCES, get_parser
from app.scraper.sources import get_source_catalog
from app.scraper.summaries import build_course_summary, build_event_summary


@dataclass
class ScrapeReport:
    sources_attempted: int = 0
    sources_succeeded: int = 0
    sources_failed: int = 0
    source_details: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "sources_attempted": self.sources_attempted,
            "sources_succeeded": self.sources_succeeded,
            "sources_failed": self.sources_failed,
            "source_details": self.source_details,
        }


def _filter_items(items: list[dict], source: SourceMetadata) -> list[dict]:
    filtered: list[dict] = []
    for item in items:
        title = item.get("title", "")
        url = item.get("url", "")
        if is_quality_item(title, url, source.category, source.scrape_type):
            filtered.append(item)
    return filtered


def _to_event(source: SourceMetadata, item: dict) -> EventItem:
    title = item.get("title", "").strip() or f"{source.source_name} Listing"
    summary = build_event_summary(
        category=source.category,
        provider=source.source_name,
        title=title,
        raw_summary=item.get("summary", ""),
        published_at=item.get("published_at", ""),
    )
    event = EventItem(
        title=title,
        category=source.category,
        provider=source.source_name,
        url=item.get("url", source.url),
        summary=summary,
        published_at=item.get("published_at", ""),
        tags=item.get("tags", []),
    )
    score, ping, reason = calculate_mba_relevance(event.model_dump())
    return event.model_copy(
        update={
            "mba_relevance_score": score,
            "mba_ping": ping,
            "mba_relevance_reason": reason,
        }
    )


def _to_course(source: SourceMetadata, item: dict) -> CourseItem:
    title = item.get("title", "").strip() or f"{source.source_name} Course"
    text = item.get("summary", "").lower()
    difficulty = "Beginner" if "beginner" in text else "Intermediate" if "intermediate" in text else "Unknown"
    summary = build_course_summary(provider=source.source_name, title=title, raw_summary=item.get("summary", ""))
    return CourseItem(
        course_title=title,
        provider=source.source_name,
        difficulty_level=difficulty,
        duration="Self-paced",
        enrollment_link=item.get("url", source.url),
        release_date=item.get("published_at", ""),
        tags=item.get("tags", []),
        category=source.category,
        summary=summary,
    )


def run_full_scrape() -> tuple[list[EventItem], list[CourseItem], dict]:
    events: list[EventItem] = []
    courses: list[CourseItem] = []
    report = ScrapeReport()
    sources = get_source_catalog()
    report.sources_attempted = len(sources)

    for source in sources:
        detail = {
            "source_name": source.source_name,
            "category": source.category,
            "status": "failed",
            "items_found": 0,
            "error": "",
        }
        try:
            parser = get_parser(source.source_name, source.scrape_type)
            raw_items = parser(source.url, max_items=30)
            raw_items = _filter_items(raw_items, source)

            if not raw_items and source.source_name in EXA_FALLBACK_SOURCES:
                query = EXA_QUERIES.get(source.source_name, source.source_name)
                raw_items = _filter_items(exa_search(query), source)

            detail["items_found"] = len(raw_items)
            if raw_items:
                detail["status"] = "ok"
                report.sources_succeeded += 1
            else:
                report.sources_failed += 1

            if source.category in {"ai_courses", "ai_certifications"}:
                courses.extend(_to_course(source, item) for item in raw_items)
            else:
                events.extend(_to_event(source, item) for item in raw_items)
        except Exception as exc:
            detail["error"] = str(exc)[:200]
            report.sources_failed += 1

        report.source_details.append(detail)

    unique_events = sorted(
        {e.url: e for e in events}.values(),
        key=lambda event: event.mba_relevance_score,
        reverse=True,
    )
    unique_courses = list({c.enrollment_link: c for c in courses}.values())
    return unique_events, unique_courses, report.to_dict()
