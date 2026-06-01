from __future__ import annotations

import os
from collections import defaultdict
from urllib.parse import urlparse

import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000").rstrip("/")

CATEGORY_LABELS = {
    "business_competitions": "Business Competitions",
    "mba_webinars_events": "MBA Webinars & Events",
    "ai_courses": "AI Courses",
    "ai_certifications": "AI Certifications",
    "ai_hackathons": "AI Hackathons",
    "ai_industry_updates": "AI Industry Updates",
}

CATEGORY_COLORS = {
    "business_competitions": "#2563eb",
    "mba_webinars_events": "#7c3aed",
    "ai_courses": "#059669",
    "ai_certifications": "#0d9488",
    "ai_hackathons": "#ea580c",
    "ai_industry_updates": "#db2777",
}

PING_META = {
    "hot": {"color": "#16a34a", "label": "High MBA relevance"},
    "warm": {"color": "#ea580c", "label": "Medium MBA relevance"},
    "cool": {"color": "#94a3b8", "label": "Low MBA relevance"},
}

PING_FILTER = {
    "Hot only": {"hot"},
    "Warm+": {"hot", "warm"},
    "All": {"hot", "warm", "cool"},
}


def fetch_json(path: str) -> dict:
    response = requests.get(f"{API_BASE}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


def group_by_provider(items: list[dict], provider_key: str = "provider") -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        grouped[item.get(provider_key, "Unknown Source")].append(item)
    return dict(sorted(grouped.items(), key=lambda pair: pair[0].lower()))


def sort_events_by_mba(events: list[dict]) -> list[dict]:
    return sorted(events, key=lambda item: item.get("mba_relevance_score", 0), reverse=True)


def category_badge(category: str) -> str:
    label = CATEGORY_LABELS.get(category, category.replace("_", " ").title())
    color = CATEGORY_COLORS.get(category, "#475569")
    return (
        f"<span style='background:{color};color:white;padding:2px 8px;"
        f"border-radius:999px;font-size:11px;font-weight:600;'>{label}</span>"
    )


def ping_dot(ping: str) -> str:
    color = PING_META.get(ping, PING_META["cool"])["color"]
    pulse = "animation:ping-pulse 1.6s ease-in-out infinite;" if ping == "hot" else ""
    return f"<span style='width:10px;height:10px;border-radius:50%;background:{color};display:inline-block;{pulse}'></span>"


def render_compact_event(event: dict, key_prefix: str, idx: int) -> None:
    score = event.get("mba_relevance_score", 0)
    ping = event.get("mba_ping", "cool")
    meta = PING_META.get(ping, PING_META["cool"])
    summary = event.get("summary", "")
    reason = event.get("mba_relevance_reason", "")

    col_a, col_b = st.columns([5, 1])
    with col_a:
        st.markdown(
            f"{ping_dot(ping)} **{event.get('title', 'Untitled')}** "
            f"<span style='color:{meta['color']};font-size:12px;font-weight:700;'>"
            f"Ping {score}</span> {category_badge(event.get('category', ''))}",
            unsafe_allow_html=True,
        )
        st.caption(f"{event.get('provider')} · {meta['label']}")
        if summary:
            with st.expander("Summary", expanded=False):
                st.write(summary)
                if reason:
                    st.caption(f"Why ranked here: {reason}")
        elif reason:
            st.caption(f"Why ranked here: {reason}")
    with col_b:
        st.link_button("Open", event.get("url", "#"), key=f"{key_prefix}-{idx}")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .block-container { padding-top: 1rem; max-width: 1180px; }
            div[data-testid="stMetric"] {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 10px;
            }
            .hero-box {
                background: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%);
                border: 1px solid #dbeafe;
                border-radius: 14px;
                padding: 16px 20px;
                margin-bottom: 16px;
            }
            @keyframes ping-pulse {
                0% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.55); }
                70% { box-shadow: 0 0 0 10px rgba(22, 163, 74, 0); }
                100% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def provider_domain(items: list[dict], url_key: str = "url") -> str:
    for item in items:
        url = item.get(url_key, "")
        if url:
            parsed = urlparse(url)
            if parsed.netloc:
                return parsed.netloc.replace("www.", "")
    return ""


st.set_page_config(page_title="MBA + AI Opportunity Radar", layout="wide")
inject_styles()

st.markdown("# MBA + AI Opportunity Radar")

with st.sidebar:
    st.header("Controls")
    if st.button("Refresh Scrape", use_container_width=True, type="primary"):
        with st.spinner("Scraping all sources..."):
            try:
                resp = requests.post(f"{API_BASE}/refresh", timeout=180)
                resp.raise_for_status()
                data = resp.json()
                ok = data.get("sources_succeeded", 0)
                total = data.get("sources_attempted", 0)
                st.success(f"Refresh done — {ok}/{total} sources OK")
                st.session_state["last_refresh"] = data
            except requests.RequestException as exc:
                st.error(f"Refresh failed: {exc}")
        st.rerun()

    last = st.session_state.get("last_refresh")
    if last:
        st.caption(
            f"Last refresh: {last.get('generated_at', '')[:19]} | "
            f"{last.get('sources_succeeded', 0)}/{last.get('sources_attempted', 0)} sources OK"
        )

    st.divider()
    st.subheader("Filters")
    view_mode = st.radio("View", ["MBA Ranked", "By Website", "Flat List"], horizontal=True)
    ping_filter = st.selectbox("Min MBA ping tier", list(PING_FILTER.keys()), index=1)
    search_query = st.text_input("Search", placeholder="hackathon, MBA, coursera...")
    event_categories = st.multiselect(
        "Event categories",
        options=["business_competitions", "mba_webinars_events", "ai_hackathons", "ai_industry_updates"],
        default=["business_competitions", "mba_webinars_events", "ai_hackathons", "ai_industry_updates"],
    )

    st.divider()
    st.subheader("Email Digest")
    if st.button("Preview Weekly Email", use_container_width=True):
        with st.spinner("Building digest..."):
            preview = fetch_json("/preview-email")
            st.text_area("Digest preview", preview.get("digest_text", ""), height=220)

    approved = st.checkbox("Approve sending email now")
    if st.button("Approve + Send", use_container_width=True):
        resp = requests.post(
            f"{API_BASE}/approve-send",
            json={"approved": approved, "send_now": True},
            timeout=30,
        )
        st.json(resp.json())

try:
    with st.spinner("Loading data..."):
        events_payload = fetch_json("/events")
        courses_payload = fetch_json("/courses")
        try:
            health = fetch_json("/scrape-health")
        except requests.RequestException:
            health = {}
except requests.RequestException:
    st.error(
        f"Backend not reachable at `{API_BASE}`. "
        "Start it with: `python -m uvicorn app.main:app --reload`"
    )
    st.stop()

events = events_payload.get("events", [])
courses = courses_payload.get("courses", [])

if search_query:
    q = search_query.lower()
    events = [e for e in events if q in e.get("title", "").lower() or q in e.get("provider", "").lower()]
    courses = [
        c for c in courses if q in c.get("course_title", "").lower() or q in c.get("provider", "").lower()
    ]

events = [e for e in events if e.get("category") in event_categories]
events = [e for e in events if e.get("mba_ping", "cool") in PING_FILTER[ping_filter]]
events = sort_events_by_mba(events)

generated_at = health.get("generated_at", "")[:19] if health else ""
sources_ok = health.get("sources_succeeded", 0)
sources_total = health.get("sources_attempted", 0)

st.markdown(
    f"""
    <div class="hero-box">
        <strong>Dashboard</strong> · Last refresh: {generated_at or "Not yet refreshed"}
        · Sources: {sources_ok}/{sources_total} OK
        · Showing {len(events)} MBA-filtered events and {len(courses)} courses
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Events shown", len(events))
m2.metric("Hot pings", len([e for e in events if e.get("mba_ping") == "hot"]))
m3.metric("Courses", len(courses))
m4.metric("Sources OK", f"{sources_ok}/{sources_total}")

top_tab, all_tab, courses_tab = st.tabs(["MBA Top Picks", "All Events", "Courses"])

with top_tab:
    top = events[:15]
    if not top:
        st.info("No events match your filters. Try **Refresh Scrape** or broaden ping tier.")
    else:
        for idx, event in enumerate(top):
            with st.container(border=True):
                render_compact_event(event, "top", idx)

with all_tab:
    if not events:
        st.info("No events to show.")
    elif view_mode == "By Website":
        grouped = group_by_provider(events)
        for provider, provider_events in grouped.items():
            provider_events = sort_events_by_mba(provider_events)
            domain = provider_domain(provider_events)
            hot_count = len([e for e in provider_events if e.get("mba_ping") == "hot"])
            with st.expander(f"{provider} ({len(provider_events)} items · {hot_count} hot)", expanded=False):
                if domain:
                    st.caption(domain)
                for idx, event in enumerate(provider_events):
                    render_compact_event(event, f"prov-{provider}", idx)
    else:
        for idx, event in enumerate(events):
            with st.container(border=True):
                render_compact_event(event, "all", idx)

with courses_tab:
    if not courses:
        st.info("No courses yet. Click **Refresh Scrape**.")
    else:
        grouped_courses = group_by_provider(courses, "provider")
        for provider, provider_courses in grouped_courses.items():
            with st.expander(f"{provider} ({len(provider_courses)} courses)", expanded=False):
                for idx, course in enumerate(provider_courses):
                    st.markdown(f"**{course.get('course_title', 'Untitled')}**")
                    if course.get("summary"):
                        st.caption(course.get("summary"))
                    st.caption(
                        f"{course.get('difficulty_level', 'Unknown')} · {course.get('duration', 'Unknown')}"
                    )
                    st.link_button(
                        "Enroll",
                        course.get("enrollment_link", "#"),
                        key=f"course-{provider}-{idx}",
                    )
