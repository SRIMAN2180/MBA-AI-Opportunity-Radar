from __future__ import annotations

try:
    from crewai import Agent
except Exception:  # pragma: no cover
    Agent = None


def build_coder_agent():
    """CrewAI-compatible Coder(Dev Agent) definition."""
    if Agent is None:
        return {
            "role": "Coder (Dev Agent)",
            "goal": "Implement and maintain local scraping + digest system.",
            "backstory": "Builds lightweight backend/frontend automation in Python.",
        }

    return Agent(
        role="Coder (Dev Agent)",
        goal="Implement local-hosted backend/frontend for weekly AI/MBA opportunity digest.",
        backstory="Builds FastAPI services, storage pipelines, and approval-safe email workflows.",
        verbose=False,
    )
