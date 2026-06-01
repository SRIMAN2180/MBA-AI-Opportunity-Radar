from __future__ import annotations

from app.agents.coder_agent import build_coder_agent
from app.agents.researcher_agent import build_researcher_agent, researcher_source_metadata

try:
    from crewai import Crew, Task
except Exception:  # pragma: no cover
    Crew = None
    Task = None


def build_parallel_crew():
    researcher = build_researcher_agent()
    coder = build_coder_agent()

    if Crew is None or Task is None or isinstance(researcher, dict) or isinstance(coder, dict):
        return {
            "researcher": researcher,
            "coder": coder,
            "mode": "fallback",
            "source_metadata": researcher_source_metadata(),
        }

    research_task = Task(
        description="Discover scrape-friendly sources and return normalized source metadata.",
        expected_output="JSON list with source_name, category, scrape_type, url, parsing_strategy",
        agent=researcher,
        async_execution=True,
    )
    code_task = Task(
        description="Build and maintain lightweight local Python backend/frontend pipeline.",
        expected_output="Implementation steps and system checks.",
        agent=coder,
        async_execution=True,
    )
    return Crew(
        agents=[researcher, coder],
        tasks=[research_task, code_task],
        verbose=False,
    )
