from __future__ import annotations

from urllib.parse import urljoin

from app.scraper.fetchers import fetch_html


def _item(title: str, url: str, summary: str = "", published_at: str = "") -> dict:
    return {
        "title": title[:180],
        "url": url,
        "summary": summary[:300],
        "published_at": published_at,
        "tags": [],
    }


def parse_reskilll(base_url: str, max_items: int = 30) -> list[dict]:
    soup = fetch_html(base_url)
    results: list[dict] = []
    seen: set[str] = set()
    for anchor in soup.select("a[href*='/hack/']"):
        href = anchor.get("href", "").strip()
        title = anchor.get_text(" ", strip=True)
        if not href or not title or len(title) < 4:
            continue
        full_url = urljoin(base_url, href)
        if full_url in seen:
            continue
        seen.add(full_url)
        card = anchor.find_parent(["div", "article", "li"])
        summary = ""
        if card:
            meta = card.select_one("p, .description, span")
            if meta:
                summary = meta.get_text(" ", strip=True)
        results.append(_item(title, full_url, summary))
        if len(results) >= max_items:
            break
    return results


def parse_scaler(base_url: str, max_items: int = 30) -> list[dict]:
    soup = fetch_html(base_url)
    results: list[dict] = []
    seen: set[str] = set()
    selectors = "a[href*='/event'], a[href*='/events/'], .event-card a, article a"
    for anchor in soup.select(selectors):
        href = anchor.get("href", "").strip()
        title = anchor.get_text(" ", strip=True)
        if not href or not title or len(title) < 8:
            continue
        if title.lower() in {"events", "view all", "register now"}:
            continue
        full_url = urljoin(base_url, href)
        if full_url in seen or full_url.rstrip("/") == base_url.rstrip("/"):
            continue
        seen.add(full_url)
        results.append(_item(title, full_url))
        if len(results) >= max_items:
            break
    return results


def parse_unstop(base_url: str, max_items: int = 30) -> list[dict]:
    soup = fetch_html(base_url)
    results: list[dict] = []
    seen: set[str] = set()
    for anchor in soup.select("a[href*='unstop.com']"):
        href = anchor.get("href", "").strip()
        title = anchor.get_text(" ", strip=True)
        if not href or not title or len(title) < 8:
            continue
        full_url = urljoin(base_url, href)
        if "all-opportunities" in full_url and full_url.count("/") <= 4:
            continue
        if full_url in seen:
            continue
        seen.add(full_url)
        results.append(_item(title, full_url))
        if len(results) >= max_items:
            break
    return results


def parse_deeplearning_ai(base_url: str, max_items: int = 30) -> list[dict]:
    soup = fetch_html(base_url)
    results: list[dict] = []
    seen: set[str] = set()
    for anchor in soup.select("a[href*='deeplearning.ai']"):
        href = anchor.get("href", "").strip()
        title = anchor.get_text(" ", strip=True)
        if not href or not title or len(title) < 8:
            continue
        full_url = urljoin(base_url, href)
        if full_url in seen or full_url.rstrip("/") == base_url.rstrip("/"):
            continue
        if "/courses/" not in full_url and "/short-courses/" not in full_url and "learn." not in full_url:
            if not any(k in full_url for k in ("/course", "/specialization", "skills")):
                continue
        seen.add(full_url)
        results.append(_item(title, full_url))
        if len(results) >= max_items:
            break
    return results


def parse_devpost(base_url: str, max_items: int = 30) -> list[dict]:
    soup = fetch_html(base_url)
    results: list[dict] = []
    seen: set[str] = set()
    for anchor in soup.select("a[href*='devpost.com']"):
        href = anchor.get("href", "").strip()
        title = anchor.get_text(" ", strip=True)
        if not href or not title or len(title) < 8:
            continue
        full_url = urljoin(base_url, href)
        if "/software/" not in full_url and "/hackathons/" not in full_url:
            continue
        if full_url in seen:
            continue
        seen.add(full_url)
        results.append(_item(title, full_url))
        if len(results) >= max_items:
            break
    return results
