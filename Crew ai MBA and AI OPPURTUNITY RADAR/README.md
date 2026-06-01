
```
 MBA + AI Opportunity Radar
Lightweight local Python app that scrapes opportunities/courses/news, stores results in `bcom_ai_events.json`, and generates approval-gated weekly email digests.

## Features
* **FastAPI backend** with required endpoints:
  * `/events`
  * `/courses`
  * `/refresh`
  * `/preview-email`
  * `/approve-send`
* **APScheduler** weekly job for automated refresh + digest generation
* **CrewAI-compatible dual agent structure:**
  * Researcher (Web Agent)
  * Coder (Dev Agent)
* **Local JSON persistence** (`bcom_ai_events.json`) + optional SQLite persistence
* **Streamlit local frontend** for viewing/filtering/refreshing and email approval/send
* **Email safety gate:**
  ```python
  if not user_approved:
      print("Email sending cancelled until approval.")
      return

```

## Project Structure

```text
app/
  agents/
  api/
  emailer/
  scheduler/
  scraper/
  storage/
frontend/

```

## First-time setup (only if not done yet)

Open your terminal, navigate to the project directory, and run the following commands:

```powershell
cd path/to/mba-ai-opportunity-radar
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env

```

Note: Open your new `.env` file and fill in the SMTP fields if real email sending is needed.
OPENAI_API_KEY=
OPENROUTER_API_KEY=
EXA_API_KEY=

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SENDER_EMAIL=
RECIPIENT_EMAIL=


## Run Locally

This application requires running the backend and frontend simultaneously.

### Terminal 1 — Backend (FastAPI + Swagger)

```powershell
cd path/to/mba-ai-opportunity-radar
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload

```

You should see: `Uvicorn running on http://127.0.0.1:8000`

*Open in browser:*

* API docs (Swagger): https://www.google.com/search?q=http://127.0.0.1:8000/docs
* Health check: https://www.google.com/search?q=http://127.0.0.1:8000
*(Leave this terminal running)*

### Terminal 2 — Frontend (Streamlit)

Open a *new* PowerShell window:

```powershell
cd path/to/mba-ai-opportunity-radar
.\.venv\Scripts\Activate.ps1
streamlit run frontend/app.py

```

Streamlit will open in your browser (usually http://localhost:8501).
*(Leave this terminal running too)*

## Typical Workflow

1. Start **backend** first (Terminal 1).
2. Start **frontend** second (Terminal 2).
3. In Streamlit, click **Refresh Scrape**.
4. View **Events** / **Courses** tabs.
5. Use **Preview Weekly Email** → **Approve + Send** when ready.

## API Flow

* Weekly scheduler triggers scrape (`/refresh` logic).
* JSON file `bcom_ai_events.json` is generated/updated.
* Email preview available via `/preview-email`.
* User approval required using `/approve-send` with `approved=true`.
* Only after approval, the email send function runs.

```

```
