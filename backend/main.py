# backend/main.py
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, shutil, json, random, time

# --------------------
# Simple LifePilot demo backend (FastAPI)
# - /ask         -> returns mock AI responses (or plug an LLM here)
# - /ping        -> healthcheck
# - /upload      -> saves uploaded files to uploads/
# - /report      -> accepts a simple JSON report
# --------------------

app = FastAPI(title="LifePilot Demo Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class Report(BaseModel):
    title: str
    description: str

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "LifePilot backend is up"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"filename": file.filename, "status": "uploaded"}

@app.post("/report")
async def create_report(report: Report):
    # For demo: just echo back
    return {"title": report.title, "description": report.description, "status": "saved"}

# Mock AI responder: replace with real LLM call later
def mock_ai_response(user_input: str):
    text = user_input.lower()
    # detect intents
    if "schedule" in text or "meeting" in text:
        # simulated calendar result
        return {
            "type": "schedule",
            "message": "Plan: Schedule a 30-min meeting tomorrow at 10:00 AM with 'John'. Dry-run complete. Press CONFIRM to create event.",
            "dry_run": True,
            "data": {"summary": "Meeting with John", "start": "2025-09-20T10:00:00+05:30", "end": "2025-09-20T10:30:00+05:30"}
        }
    if "email" in text or "draft" in text:
        # simulated email draft
        return {
            "type": "email",
            "message": "Drafted email (preview):\nSubject: Quick update on the project\nBody: Hi John, I wanted to share a quick update on the project. ...\n(Press CONFIRM to send from demo account)",
            "dry_run": True,
            "data": {"subject": "Quick update on the project", "body": "Hi John,\n\nI wanted to share a quick update..."}
        }
    if "travel" in text or "trip" in text or "book" in text:
        # simulated trip planner
        return {
            "type": "trip",
            "message": "Trip plan (simulated): 2-day Jaipur trip with mock booking refs. Check itinerary and press CONFIRM to add to calendar.",
            "dry_run": True,
            "data": {"itinerary": ["Day1: Amber Fort", "Day2: City Palace"], "mock_refs": ["LP-12345"]}
        }
    # default reply
    small = [
        "I can help you schedule meetings, draft emails, and plan trips. Try: 'Schedule a meeting tomorrow at 3pm.'",
        "Tell me what to do: schedule, email, or trip planning.",
        "Working on that — what would you like to automate?"
    ]
    return {"type": "chat", "message": random.choice(small), "dry_run": True}

@app.post("/ask")
async def ask_endpoint(req: Request):
    body = await req.json()
    query = body.get("query", "")
    # Replace this with a real LLM call (OpenAI/HuggingFace) when ready.
    resp = mock_ai_response(query)
    return resp

# Simple confirm endpoint (simulate execution)
@app.post("/confirm")
async def confirm_action(req: Request):
    body = await req.json()
    action_type = body.get("type")
    data = body.get("data", {})
    # Simulate action execution and return success
    now = int(time.time())
    if action_type == "schedule":
        # simulate created event id
        return {"status": "success", "message": "Calendar event created (SIMULATED)", "event_id": f"evt-{now}"}
    if action_type == "email":
        return {"status": "success", "message": "Email sent (SIMULATED)", "message_id": f"msg-{now}"}
    if action_type == "trip":
        return {"status": "success", "message": "Trip bookings created (SIMULATED)", "booking_refs": [f"LP-{now}"]}
    return {"status": "error", "message": "Unknown action type"}
