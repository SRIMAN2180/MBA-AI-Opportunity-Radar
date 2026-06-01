from __future__ import annotations

from app.scraper.sources import get_source_catalog

try:
    from crewai import Agent
except Exception:  # pragma: no cover - optional dependency fallback
    Agent = None


def build_researcher_agent():
    """CrewAI-compatible Researcher(Web Agent) definition."""
    if Agent is None:
        return {
            "role": "Researcher (Web Agent)",
            "goal": "Discover scrape-friendly AI/MBA opportunity sources.",
            "backstory": "Specialist in RSS/API/structured HTML source discovery.",
        }

    return Agent(
        role="Researcher (Web Agent)",
        goal="Discover reliable scrape-friendly sources for MBA and AI opportunities.",
        backstory="Finds structured sources and recommends robust parsing strategies.",
        verbose=False,
    )


def researcher_source_metadata():
    return [item.model_dump() for item in get_source_catalog()]
