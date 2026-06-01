from __future__ import annotations

from app.scraper.fetchers import extract_generic_cards, fetch_rss
from app.scraper.parsers.site_parsers import (
    parse_deeplearning_ai,
    parse_devpost,
    parse_reskilll,
    parse_scaler,
    parse_unstop,
)

PARSER_REGISTRY: dict[str, callable] = {
    "Reskilll Hacks": parse_reskilll,
    "Scaler Events": parse_scaler,
    "Unstop Opportunities": parse_unstop,
    "DeepLearning.AI Short Courses": parse_deeplearning_ai,
    "Devpost Hackathons": parse_devpost,
}

EXA_FALLBACK_SOURCES = {
    "Kaggle Competitions",
    "Coursera ML Browse",
    "Udemy AI Courses",
}


def get_parser(source_name: str, scrape_type: str):
    if scrape_type == "rss":
        return fetch_rss
    return PARSER_REGISTRY.get(source_name, extract_generic_cards)
