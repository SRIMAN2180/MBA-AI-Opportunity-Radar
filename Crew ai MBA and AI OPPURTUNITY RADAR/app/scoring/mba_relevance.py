from __future__ import annotations

import re

CATEGORY_BASE_SCORES = {
    "mba_webinars_events": 78,
    "business_competitions": 72,
    "ai_hackathons": 38,
    "ai_industry_updates": 18,
}

HIGH_MBA_KEYWORDS = (
    "mba",
    "b-school",
    "business school",
    "case study",
    "case competition",
    "consulting",
    "finance",
    "marketing",
    "entrepreneurship",
    "leadership",
    "management",
    "strategy",
    "gmat",
    "cat exam",
    "webinar",
    "masterclass",
    "business plan",
    "startup pitch",
)

MEDIUM_MBA_KEYWORDS = (
    "business",
    "competition",
    "workshop",
    "internship",
    "networking",
    "summit",
    "conference",
    "panel",
    "seminar",
    "corporate",
    "product management",
    "analytics",
    "placement",
    "career",
)

LOW_RELEVANCE_KEYWORDS = (
    "crypto",
    "vape",
    "gaming",
    "sports",
    "celebrity",
)

GENERIC_TITLE_PENALTIES = (
    r"^all\s*\(\d+\)$",
    r"^participate",
    r"^register",
    r"^learn$",
    r"^network$",
    r"^contribute$",
    r"^earn\s",
    r"^\d+\s+registered",
)


def _text_blob(event: dict) -> str:
    parts = [
        event.get("title", ""),
        event.get("summary", ""),
        event.get("provider", ""),
        " ".join(event.get("tags", [])),
    ]
    return " ".join(parts).lower()


def _title_quality_penalty(title: str) -> int:
    normalized = title.strip().lower()
    penalty = 0
    if len(normalized) < 10:
        penalty += 15
    for pattern in GENERIC_TITLE_PENALTIES:
        if re.search(pattern, normalized):
            penalty += 35
    if normalized in {"events", "learn", "network", "contribute", "participate now", "install app"}:
        penalty += 40
    if "install app" in normalized or normalized.startswith("install "):
        penalty += 35
    return penalty


def calculate_mba_relevance(event: dict) -> tuple[int, str, str]:
    """Return score (0-100), ping tier, and human-readable reason."""
    category = event.get("category", "")
    title = event.get("title", "")
    provider = event.get("provider", "")
    score = CATEGORY_BASE_SCORES.get(category, 20)
    text = _text_blob(event)
    reasons: list[str] = []

    keyword_boost = 0
    for keyword in HIGH_MBA_KEYWORDS:
        if keyword in text:
            keyword_boost += 8
            if len(reasons) < 2:
                reasons.append(keyword)
    keyword_boost = min(keyword_boost, 24)
    score += keyword_boost

    medium_boost = 0
    for keyword in MEDIUM_MBA_KEYWORDS:
        if keyword in text:
            medium_boost += 4
    medium_boost = min(medium_boost, 16)
    score += medium_boost

    for keyword in LOW_RELEVANCE_KEYWORDS:
        if keyword in text:
            score -= 10
            reasons.append(f"off-topic:{keyword}")

    if re.search(r"\bmba\b", text):
        score += 15
        reasons.insert(0, "MBA keyword")
    if "case comp" in text or "case study" in text:
        score += 10
        reasons.insert(0, "case competition")
    if re.search(r"\b20\d{2}\b", title):
        score += 4
    if category == "ai_hackathons" and any(k in text for k in ("business", "startup", "social impact")):
        score += 8

    score -= _title_quality_penalty(title)

    score = max(0, min(100, score))
    ping = "hot" if score >= 75 else "warm" if score >= 45 else "cool"

    if not reasons:
        reasons.append(category.replace("_", " "))
    reason_text = f"{provider}: {', '.join(reasons[:3])}" if reasons else f"{provider} opportunity"
    return score, ping, reason_text


def rank_events(events: list[dict]) -> list[dict]:
    enriched: list[dict] = []
    for event in events:
        score, ping, reason = calculate_mba_relevance(event)
        updated = {
            **event,
            "mba_relevance_score": score,
            "mba_ping": ping,
            "mba_relevance_reason": reason,
        }
        enriched.append(updated)
    return sorted(enriched, key=lambda item: item["mba_relevance_score"], reverse=True)
