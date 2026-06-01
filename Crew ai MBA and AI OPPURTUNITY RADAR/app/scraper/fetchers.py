from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse
import feedparser
import requests
from bs4 import BeautifulSoup

NOISE_TITLES = {
    "about",
    "about us",
    "careers",
    "contact",
    "contact us",
    "login",
    "log in",
    "sign in",
    "sign up",
    "signup",
    "register",
    "register now",
    "privacy",
    "privacy policy",
    "terms",
    "terms of service",
    "partners",
    "community",
    "initiative",
    "events",
    "blog",
    "home",
    "pricing",
    "help",
    "support",
    "faq",
    "practice",
    "learn",
    "discussions",
    "jobs",
    "hire",
    "solutions",
    "products",
    "resources",
    "company",
    "newsletter",
    "subscribe",
    "download",
    "get started",
    "explore",
    "view all",
    "see all",
    "read more",
    "learn more",
    "participate now",
    "participate",
    "network",
    "earn certification",
    "contribute",
    "gain cutting-edge",
    "all (",
    "install app",
    "install",
}

GENERIC_TITLE_PATTERNS = (
    r"^all\s*\(\d+\)$",
    r"^participate\s+now$",
    r"^register\s+now$",
    r"^learn$",
    r"^network$",
    r"^contribute$",
    r"^earn\s+certification$",
    r"^\d+\s+registered",
)

NOISE_URL_PARTS = (
    "/login",
    "/signup",
    "/sign-up",
    "/register",
    "/privacy",
    "/terms",
    "/about",
    "/careers",
    "/contact",
    "/help",
    "/faq",
    "/pricing",
    "/jobs",
    "/hire",
    "/practice/",
    "#trusted",
    "#initiatives",
    "#events",
    "#community",
)


def is_noise_item(title: str, url: str) -> bool:
    normalized_title = title.strip().lower()
    if not normalized_title or len(normalized_title) < 4:
        return True
    if normalized_title in NOISE_TITLES:
        return True

    parsed = urlparse(url)
    path = (parsed.path or "").lower()
    fragment = (parsed.fragment or "").lower()

    if fragment and not path.strip("/"):
        return True
    if any(part in path for part in NOISE_URL_PARTS):
        return True
    if path in {"/", ""} and fragment:
        return True
    return False


def is_quality_item(title: str, url: str, category: str = "", scrape_type: str = "html") -> bool:
    """Stricter post-parse gate for real opportunities (not nav/CTA junk)."""
    if is_noise_item(title, url):
        return False

    normalized_title = title.strip().lower()
    if len(normalized_title) < 8 and scrape_type != "rss":
        return False

    for pattern in GENERIC_TITLE_PATTERNS:
        if re.match(pattern, normalized_title):
            return False

    if normalized_title.startswith(("learn ", "network ", "earn ", "gain ", "contribute ")):
        return False

    parsed = urlparse(url)
    path = (parsed.path or "").lower().strip("/")
    segments = [s for s in path.split("/") if s]

    if scrape_type == "html":
        if not segments:
            return False
        if len(segments) == 1 and segments[0] in {"events", "hackathon", "hackathons", "allhacks", "all-opportunities"}:
            return False

    return True


def fetch_html(url: str, timeout: int = 20) -> BeautifulSoup:
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def fetch_rss(url: str, max_items: int = 30) -> list[dict]:
    for candidate in _rss_candidates(url):
        feed = feedparser.parse(candidate)
        if not feed.entries:
            continue

        items: list[dict] = []
        for entry in feed.entries[:max_items]:
            title = getattr(entry, "title", "")
            link = getattr(entry, "link", "")
            if is_noise_item(title, link):
                continue
            if not is_quality_item(title, link, scrape_type="rss"):
                continue
            items.append(
                {
                    "title": title,
                    "url": link,
                    "summary": getattr(entry, "summary", ""),
                    "published_at": getattr(entry, "published", ""),
                    "tags": [t.term for t in getattr(entry, "tags", []) if hasattr(t, "term")],
                }
            )
        if items:
            return items
    return []


def _rss_candidates(url: str) -> list[str]:
    base = url.rstrip("/")
    return list(
        dict.fromkeys(
            [
                url,
                f"{base}/feed",
                f"{base}/feed.xml",
                f"{base}/rss",
                f"{base}/rss.xml",
            ]
        )
    )


def extract_generic_cards(base_url: str, max_items: int = 30) -> list[dict]:
    """Fallback parser for scrape-friendly listing pages."""
    soup = fetch_html(base_url)
    cards = soup.select(
        "article, .card, .event-card, .course-card, .challenge-card, "
        "[class*='hackathon'], [class*='competition'], [class*='course'], [class*='event']"
    )
    if not cards:
        cards = soup.select("main li, main article, .listing li, .list-item")

    results: list[dict] = []
    seen_urls: set[str] = set()
    for card in cards:
        anchor = card.select_one("a[href]")
        if not anchor:
            continue
        title = anchor.get_text(" ", strip=True)
        href = anchor.get("href", "").strip()
        if not title or not href:
            continue

        full_url = urljoin(base_url, href)
        if full_url in seen_urls or is_noise_item(title, full_url):
            continue
        if not is_quality_item(title, full_url, scrape_type="html"):
            continue

        summary = ""
        meta = card.select_one("p, .description, .summary")
        if meta:
            summary = meta.get_text(" ", strip=True)

        seen_urls.add(full_url)
        results.append(
            {
                "title": title[:180],
                "url": full_url,
                "summary": summary[:300],
                "published_at": "",
                "tags": [],
            }
        )
        if len(results) >= max_items:
            break
    return results
