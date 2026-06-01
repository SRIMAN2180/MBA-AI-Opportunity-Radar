from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.emailer.digest import build_digest, send_digest_email
from app.scoring.mba_relevance import rank_events
from app.scraper.pipeline import run_full_scrape
from app.storage.json_store import JsonStore
from app.storage.sqlite_store import SQLiteStore

router = APIRouter()
store = JsonStore()
sqlite_store = SQLiteStore()


class ApproveRequest(BaseModel):
    approved: bool
    send_now: bool = False


@router.get("/events")
def get_events():
    events = rank_events(store.load_dataset().get("events", []))
    return {"events": events}


@router.get("/courses")
def get_courses():
    return {"courses": store.load_dataset().get("courses", [])}


@router.get("/scrape-health")
def scrape_health():
    data = store.load_dataset()
    health = data.get("scrape_health", {})
    return {
        "generated_at": data.get("generated_at", ""),
        **health,
    }


@router.post("/refresh")
def refresh():
    events, courses, scrape_health = run_full_scrape()
    dataset = store.save_dataset(events, courses, scrape_health)
    sqlite_store.upsert_events(events)
    sqlite_store.upsert_courses(courses)
    return {
        "message": "Refresh completed",
        "events_count": len(events),
        "courses_count": len(courses),
        "generated_at": dataset.get("generated_at"),
        **scrape_health,
    }


@router.get("/preview-email")
def preview_email():
    digest = build_digest(store.load_dataset())
    return digest.model_dump()


@router.post("/approve-send")
def approve_and_send(payload: ApproveRequest):
    state = store.save_approval(payload.approved)
    result = {"approval": state.model_dump(), "sent": False}

    if payload.send_now and payload.approved:
        digest = build_digest(store.load_dataset())
        send_result = send_digest_email(
            subject="Weekly MBA + AI Opportunity Radar",
            digest_html=digest.digest_html,
            user_approved=True,
        )
        result["sent"] = send_result.get("sent", False)
        result["send_result"] = send_result
        store.save_approval(False)

    if payload.send_now and not payload.approved:
        result["send_result"] = {"sent": False, "reason": "Approval required"}

    return result
