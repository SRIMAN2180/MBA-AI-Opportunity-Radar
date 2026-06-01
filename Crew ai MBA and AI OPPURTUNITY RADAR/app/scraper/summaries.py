from __future__ import annotations

import re

from bs4 import BeautifulSoup

CATEGORY_PHRASES = {
    "business_competitions": "Business competition",
    "mba_webinars_events": "MBA or webinar event",
    "ai_hackathons": "AI hackathon",
    "ai_industry_updates": "AI industry update",
}


def clean_text(text: str) -> str:
    if not text:
        return ""
    plain = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
    plain = re.sub(r"\s+", " ", plain)
    plain = re.sub(r"\[\s*\.\.\.\s*\]", "", plain)
    return plain.strip()


def first_sentence(text: str, max_len: int = 180) -> str:
    if not text:
        return ""

    parts = re.split(r"(?<=[.!?])\s+", text)
    sentence = parts[0].strip()
    if len(sentence) > max_len:
        sentence = sentence[: max_len - 3].rstrip() + "..."
    if sentence and sentence[-1] not in ".!?":
        sentence += "."
    return sentence


def build_course_summary(*, provider: str, title: str, raw_summary: str = "") -> str:
    cleaned = clean_text(raw_summary)
    if cleaned and len(cleaned) >= 24:
        return first_sentence(cleaned)
    safe_title = title.strip().rstrip(".")
    return f"AI course from {provider}: {safe_title}."


def build_event_summary(
    *,
    category: str,
    provider: str,
    title: str,
    raw_summary: str = "",
    published_at: str = "",
) -> str:
    """Return a single readable sentence describing the event."""
    cleaned = clean_text(raw_summary)
    if cleaned and len(cleaned) >= 24 and cleaned.lower() != title.lower():
        return first_sentence(cleaned)

    kind = CATEGORY_PHRASES.get(category, "Opportunity")
    safe_title = title.strip().rstrip(".")
    date_part = f" on {published_at[:16]}" if published_at else ""
    return f"{kind} from {provider}{date_part}: {safe_title}."
