from __future__ import annotations

import requests

from app.config import settings


def exa_search(query: str, num_results: int = 10) -> list[dict]:
    if not settings.exa_api_key:
        return []

    response = requests.post(
        "https://api.exa.ai/search",
        headers={"x-api-key": settings.exa_api_key, "Content-Type": "application/json"},
        json={
            "query": query,
            "numResults": num_results,
            "type": "auto",
            "contents": {"text": {"maxCharacters": 300}},
        },
        timeout=30,
    )
    if response.status_code != 200:
        return []

    items: list[dict] = []
    for result in response.json().get("results", []):
        title = result.get("title", "").strip()
        url = result.get("url", "").strip()
        if not title or not url:
            continue
        summary = ""
        text = result.get("text") or (result.get("contents") or {}).get("text", "")
        if isinstance(text, str):
            summary = text[:300]
        items.append(
            {
                "title": title[:180],
                "url": url,
                "summary": summary,
                "published_at": result.get("publishedDate", ""),
                "tags": ["exa-fallback"],
            }
        )
    return items


EXA_QUERIES = {
    "Kaggle Competitions": "site:kaggle.com active machine learning competitions 2026",
    "Coursera ML Browse": "site:coursera.org machine learning courses specializations",
    "Udemy AI Courses": "site:udemy.com artificial intelligence courses bestseller",
}
