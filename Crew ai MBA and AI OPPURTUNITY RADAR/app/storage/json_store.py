from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import settings
from app.models import ApprovalState, CourseItem, EventItem


class JsonStore:
    def __init__(self, data_file: str | None = None, approval_file: str | None = None) -> None:
        self.data_path = Path(data_file or settings.data_file)
        self.approval_path = Path(approval_file or settings.approval_file)

    def save_dataset(
        self,
        events: list[EventItem],
        courses: list[CourseItem],
        scrape_health: dict | None = None,
    ) -> dict[str, Any]:
        payload = {
            "generated_at": datetime.utcnow().isoformat(),
            "events": [e.model_dump() for e in events],
            "courses": [c.model_dump() for c in courses],
            "scrape_health": scrape_health or {},
        }
        self.data_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def load_dataset(self) -> dict[str, Any]:
        if not self.data_path.exists():
            return {"generated_at": "", "events": [], "courses": [], "scrape_health": {}}
        return json.loads(self.data_path.read_text(encoding="utf-8"))

    def load_approval(self) -> ApprovalState:
        if not self.approval_path.exists():
            return ApprovalState()
        data = json.loads(self.approval_path.read_text(encoding="utf-8"))
        return ApprovalState(**data)

    def save_approval(self, user_approved: bool) -> ApprovalState:
        state = ApprovalState(
            user_approved=user_approved,
            approved_at=datetime.utcnow().isoformat() if user_approved else "",
        )
        self.approval_path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        return state
