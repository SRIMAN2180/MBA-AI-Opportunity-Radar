# MBA + AI Opportunity Radar

Lightweight local Python app that scrapes opportunities/courses/news, stores results in `bcom_ai_events.json`, and generates approval-gated weekly email digests.

## Features

- FastAPI backend with required endpoints:
  - `/events`
  - `/courses`
  - `/refresh`
  - `/preview-email`
  - `/approve-send`
- APScheduler weekly job for automated refresh + digest generation
- CrewAI-compatible dual agent structure:
  - `Researcher (Web Agent)`
  - `Coder (Dev Agent)`
- Local JSON persistence (`bcom_ai_events.json`) + optional SQLite persistence
- Streamlit local frontend for viewing/filtering/refreshing and email approval/send
- Email safety gate:

```python
if not user_approved:
    print("Email sending cancelled until approval.")
    return
```

## Project Structure

```
app/
  agents/
  api/
  emailer/
  scheduler/
  scraper/
  storage/
frontend/
```

## Setup

1. Create a virtualenv and install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill SMTP fields if real sending is needed.

## Run Locally

Backend:

```bash
uvicorn app.main:app --reload
```

Frontend:

```bash
streamlit run frontend/app.py
```

## API Flow

1. Weekly scheduler triggers scrape (`/refresh` logic)
2. JSON file `bcom_ai_events.json` generated/updated
3. Email preview available via `/preview-email`
4. User approval required using `/approve-send` with `approved=true`
5. Only after approval, email send function runs
