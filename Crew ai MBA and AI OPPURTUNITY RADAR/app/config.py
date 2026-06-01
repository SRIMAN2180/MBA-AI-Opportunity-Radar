from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "MBA + AI Opportunity Radar"
    data_file: str = "bcom_ai_events.json"
    approval_file: str = "approval_state.json"
    sqlite_file: str = "radar.db"
    timezone: str = "Asia/Kolkata"
    scheduler_cron_day: str = "sun"
    scheduler_cron_hour: int = 9
    scheduler_cron_minute: int = 0
    api_base_url: str = "http://127.0.0.1:8000"
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    sender_email: str = os.getenv("SENDER_EMAIL", "")
    recipient_email: str = os.getenv("RECIPIENT_EMAIL", "")

    # API keys (optional in this local-first design).
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    exa_api_key: str = os.getenv("EXA_API_KEY", "")


settings = Settings()
