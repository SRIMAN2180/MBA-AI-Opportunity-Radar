from __future__ import annotations

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings
from app.models import DigestPayload
from app.scoring.mba_relevance import rank_events


def build_digest(dataset: dict) -> DigestPayload:
    all_events = rank_events(dataset.get("events", []))
    courses = dataset.get("courses", [])

    mba_events = [e for e in all_events if e.get("mba_ping") in {"hot", "warm"}]
    other_events = [e for e in all_events if e.get("mba_ping") == "cool"]

    lines = [
        "Weekly MBA + AI Opportunity Radar",
        "",
        f"Generated: {datetime.utcnow().isoformat()} UTC",
        f"MBA-relevant events: {len(mba_events)}",
        f"Other events: {len(other_events)}",
        f"Courses: {len(courses)}",
        "",
        "MBA Top 10 (Hot & Warm):",
    ]
    for item in mba_events[:10]:
        ping = item.get("mba_ping", "cool").upper()
        score = item.get("mba_relevance_score", 0)
        lines.append(f"- [{ping} {score}] {item.get('title')} ({item.get('provider')})")
        if item.get("summary"):
            lines.append(f"  {item.get('summary')}")
        if item.get("mba_relevance_reason"):
            lines.append(f"  Why: {item.get('mba_relevance_reason')}")
        lines.append(f"  {item.get('url')}")

    if other_events:
        lines.append("")
        lines.append("Other Updates (Cool tier):")
        for item in other_events[:5]:
            lines.append(f"- {item.get('title')} ({item.get('provider')})")

    lines.append("")
    lines.append("Top Courses:")
    for item in courses[:10]:
        summary = item.get("summary", "")
        lines.append(f"- {item.get('course_title')} [{item.get('difficulty_level')}]")
        if summary:
            lines.append(f"  {summary}")
        lines.append(f"  {item.get('enrollment_link')}")

    text = "\n".join(lines)
    html = "<br>".join(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for line in lines)

    return DigestPayload(
        generated_at=datetime.utcnow().isoformat(),
        events_count=len(all_events),
        courses_count=len(courses),
        digest_text=text,
        digest_html=f"<html><body><pre>{html}</pre></body></html>",
    )


def send_digest_email(subject: str, digest_html: str, user_approved: bool) -> dict:
    if not user_approved:
        print("Email sending cancelled until approval.")
        return {"sent": False, "reason": "Approval required"}

    missing = [k for k, v in {
        "SMTP_HOST": settings.smtp_host,
        "SMTP_USER": settings.smtp_user,
        "SMTP_PASSWORD": settings.smtp_password,
        "SENDER_EMAIL": settings.sender_email,
        "RECIPIENT_EMAIL": settings.recipient_email,
    }.items() if not v]
    if missing:
        return {"sent": False, "reason": f"Missing env vars: {', '.join(missing)}"}

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.sender_email
    message["To"] = settings.recipient_email
    message.attach(MIMEText(digest_html, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(message)
    return {"sent": True}
