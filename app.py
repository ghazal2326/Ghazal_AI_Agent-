"""
Personal AI Agent System — Main Flask Backend
Agents: Email, Job Applications, Recruiter, LinkedIn, Follow-ups, Daily Tasks
"""

import os
import json
import base64
import datetime
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-me")
CORS(app)

# ── Data directory (persists agent memory / logs) ─────────────────────────────
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
for sub in ["emails", "jobs", "tasks", "logs", "followups"]:
    (DATA_DIR / sub).mkdir(exist_ok=True)

# ── OpenAI client ─────────────────────────────────────────────────────────────
try:
    from openai import OpenAI
    _api_key = os.getenv("OPENAI_API_KEY", "").strip()
    openai_client = OpenAI(api_key=_api_key) if _api_key else None
    OPENAI_AVAILABLE = bool(_api_key)
except Exception as e:
    print(f"OpenAI init error: {e}")
    openai_client = None
    OPENAI_AVAILABLE = False

# ── Gmail helpers ──────────────────────────────────────────────────────────────
GMAIL_AVAILABLE = False
gmail_service = None

def init_gmail():
    """Attempt to authenticate Gmail using stored token or credentials.json."""
    global gmail_service, GMAIL_AVAILABLE
    creds_file = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
    token_file = DATA_DIR / "gmail_token.json"

    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        SCOPES = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.modify",
        ]

        creds = None
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif Path(creds_file).exists():
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                return False

            token_file.write_text(creds.to_json())

        gmail_service = build("gmail", "v1", credentials=creds)
        GMAIL_AVAILABLE = True
        return True
    except Exception as e:
        print(f"Gmail init failed: {e}")
        return False


# ── AI helper ──────────────────────────────────────────────────────────────────
def ai_respond(system_prompt: str, user_message: str, model: str = "gpt-4o-mini") -> str:
    """Call OpenAI and return the assistant's reply (or a mock if no key)."""
    if not OPENAI_AVAILABLE or not openai_client:
        return mock_ai_response(system_prompt, user_message)
    try:
        resp = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=1500,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ AI error: {str(e)}"


def mock_ai_response(system_prompt: str, user_message: str) -> str:
    """Smart mock responses when no OpenAI key is set."""
    msg = user_message.lower()
    if "email" in msg or "reply" in msg:
        return (
            "Subject: Re: Your Message\n\n"
            "Hi,\n\nThank you for reaching out. I'd be happy to connect and discuss "
            "this opportunity further.\n\nBest regards,\nGhazal"
        )
    if "linkedin" in msg or "connect" in msg:
        return (
            "Hi [Name],\n\nI came across your profile and was impressed by your work "
            "in [field]. I'd love to connect and explore potential synergies.\n\nBest,\nGhazal"
        )
    if "follow" in msg:
        return (
            "Hi [Name],\n\nI wanted to follow up on my previous message regarding "
            "[topic]. I remain very interested and would welcome the chance to chat.\n\nBest,\nGhazal"
        )
    if "cover letter" in msg or "application" in msg:
        return (
            "Dear Hiring Team,\n\nI am excited to apply for this role. With my background "
            "in [field], I am confident I can contribute meaningfully to your team.\n\nSincerely,\nGhazal"
        )
    return (
        "I've analyzed your request and prepared a professional response. "
        "To enable full AI capabilities, please add your OpenAI API key in Settings."
    )


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — Root API Status
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return jsonify({
        "service": "Ghazal's Personal AI Agent System (Backend API)",
        "status": "online",
        "openai": OPENAI_AVAILABLE,
        "gmail": GMAIL_AVAILABLE,
        "proof_report_url": "http://localhost:8765/api/agents/jobs/proof-report",
        "bot_status_url": "http://localhost:8765/api/agents/jobs/bot-status",
    })


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — Health & Status
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/status")
def status():
    return jsonify({
        "status": "online",
        "openai": OPENAI_AVAILABLE,
        "gmail": GMAIL_AVAILABLE,
        "timestamp": datetime.datetime.now().isoformat(),
        "agents": ["email", "jobs", "recruiter", "linkedin", "followups", "tasks"],
    })


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 1 — EMAIL AGENT
# ══════════════════════════════════════════════════════════════════════════════

EMAIL_SYSTEM = """You are Ghazal's personal Email AI Agent. 
You help draft, reply to, summarize, and manage professional emails related to 
job searching, recruiter outreach, networking, and career opportunities.
Always write in a professional, warm, and confident tone.
Sign emails as 'Ghazal'."""

@app.route("/api/agents/email/draft", methods=["POST"])
def email_draft():
    data = request.get_json() or {}
    context = data.get("context", "")
    email_type = data.get("type", "general")  # reply | new | follow-up
    prompt = f"Draft a {email_type} email. Context: {context}"
    draft = ai_respond(EMAIL_SYSTEM, prompt)
    _log("email", {"action": "draft", "type": email_type, "context": context[:200]})
    return jsonify({"draft": draft, "agent": "Email Agent"})


@app.route("/api/agents/email/reply", methods=["POST"])
def email_reply():
    data = request.get_json() or {}
    original = data.get("original_email", "")
    instructions = data.get("instructions", "Reply professionally")
    prompt = f"Original email:\n{original}\n\nInstructions: {instructions}"
    reply = ai_respond(EMAIL_SYSTEM, prompt)
    _log("email", {"action": "reply", "preview": original[:100]})
    return jsonify({"reply": reply, "agent": "Email Agent"})


@app.route("/api/agents/email/summarize", methods=["POST"])
def email_summarize():
    data = request.get_json() or {}
    emails = data.get("emails", "")
    prompt = f"Summarize these emails and highlight action items:\n{emails}"
    summary = ai_respond(EMAIL_SYSTEM, prompt)
    return jsonify({"summary": summary, "agent": "Email Agent"})


@app.route("/api/agents/email/inbox")
def email_inbox():
    """Fetch real Gmail inbox (up to 10 messages)."""
    if not GMAIL_AVAILABLE:
        return jsonify({
            "error": "Gmail not connected",
            "setup": "Add credentials.json and restart the server",
            "emails": _mock_emails()
        }), 200  # still 200 so UI shows mock data

    try:
        results = gmail_service.users().messages().list(
            userId="me", maxResults=10, labelIds=["INBOX"]
        ).execute()
        messages = results.get("messages", [])
        emails = []
        for m in messages:
            msg = gmail_service.users().messages().get(
                userId="me", id=m["id"], format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()
            headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
            emails.append({
                "id": m["id"],
                "from": headers.get("From", "Unknown"),
                "subject": headers.get("Subject", "(no subject)"),
                "date": headers.get("Date", ""),
                "snippet": msg.get("snippet", ""),
            })
        return jsonify({"emails": emails, "source": "gmail"})
    except Exception as e:
        return jsonify({"error": str(e), "emails": _mock_emails()}), 200


def _mock_emails():
    return [
        {"id": "1", "from": "recruiter@techcorp.com", "subject": "Exciting ML Engineer Opportunity",
         "date": "Nov 15, 2026", "snippet": "Hi Ghazal, I came across your profile and..."},
        {"id": "2", "from": "hr@startup.io", "subject": "Re: Software Engineer Application",
         "date": "Nov 14, 2026", "snippet": "Thank you for applying. We'd like to schedule..."},
        {"id": "3", "from": "networking@conf.com", "subject": "NeurIPS 2026 — Your Registration",
         "date": "Nov 13, 2026", "snippet": "Your registration is confirmed..."},
        {"id": "4", "from": "linkedin@linkedin.com", "subject": "3 people viewed your profile",
         "date": "Nov 12, 2026", "snippet": "Your profile was viewed by recruiters at Google..."},
    ]


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 2 — JOB APPLICATION AGENT
# ══════════════════════════════════════════════════════════════════════════════

JOBS_FILE = DATA_DIR / "jobs" / "applications.json"
JOB_SYSTEM = """You are Ghazal's Job Application AI Agent.
Help track applications, write tailored cover letters, prepare interview answers,
and research companies. Ghazal is an AI/ML engineer and researcher.
Be strategic, specific, and results-focused."""

def _load_jobs():
    jobs = []
    if JOBS_FILE.exists():
        jobs = json.loads(JOBS_FILE.read_text())
    # Also merge any auto-applied jobs from data/applications/applied_*.json
    app_dir = DATA_DIR / "applications"
    if app_dir.exists():
        existing_urls = {j.get("url") for j in jobs if j.get("url")}
        changed = False
        for f in sorted(app_dir.glob("applied_*.json")):
            try:
                bot_items = json.loads(f.read_text())
                for b in bot_items:
                    if b.get("url") not in existing_urls:
                        jobs.append({
                            "id": len(jobs) + 1,
                            "company": b.get("company", "Company"),
                            "role": b.get("role", "AI/ML Engineer"),
                            "status": b.get("status", "Applied"),
                            "date_applied": (b.get("timestamp") or "")[:10] or datetime.date.today().isoformat(),
                            "url": b.get("url", ""),
                            "notes": f"Auto-applied via {b.get('platform', 'Bot')}",
                            "salary": "$160k - $200k",
                            "contact": "",
                            "next_step": f"Platform: {b.get('platform', 'Bot')}",
                            "follow_up_date": "",
                        })
                        existing_urls.add(b.get("url"))
                        changed = True
            except Exception:
                pass
        if changed:
            _save_jobs(jobs)
    return jobs

def _save_jobs(jobs):
    JOBS_FILE.write_text(json.dumps(jobs, indent=2))


@app.route("/api/agents/jobs/applications", methods=["GET"])
def jobs_list():
    return jsonify({"applications": _load_jobs()})


@app.route("/api/agents/jobs/applications", methods=["POST"])
def jobs_add():
    data = request.get_json() or {}
    jobs = _load_jobs()
    job = {
        "id": len(jobs) + 1,
        "company": data.get("company", ""),
        "role": data.get("role", ""),
        "status": data.get("status", "Applied"),
        "date_applied": data.get("date_applied", datetime.date.today().isoformat()),
        "url": data.get("url", ""),
        "notes": data.get("notes", ""),
        "salary": data.get("salary", ""),
        "contact": data.get("contact", ""),
        "next_step": data.get("next_step", ""),
        "follow_up_date": data.get("follow_up_date", ""),
    }
    jobs.append(job)
    _save_jobs(jobs)
    return jsonify({"success": True, "job": job})


@app.route("/api/agents/jobs/applications/<int:job_id>", methods=["PUT"])
def jobs_update(job_id):
    data = request.get_json() or {}
    jobs = _load_jobs()
    for j in jobs:
        if j["id"] == job_id:
            j.update(data)
            break
    _save_jobs(jobs)
    return jsonify({"success": True})


@app.route("/api/agents/jobs/applications/<int:job_id>", methods=["DELETE"])
def jobs_delete(job_id):
    jobs = [j for j in _load_jobs() if j["id"] != job_id]
    _save_jobs(jobs)
    return jsonify({"success": True})


@app.route("/api/agents/jobs/cover-letter", methods=["POST"])
def cover_letter():
    data = request.get_json() or {}
    company = data.get("company", "the company")
    role = data.get("role", "the role")
    jd = data.get("job_description", "")
    extra = data.get("extra", "")
    prompt = (
        f"Write a compelling cover letter for Ghazal applying to {role} at {company}.\n"
        f"Job Description:\n{jd}\n"
        f"Extra notes: {extra}\n"
        f"Keep it under 350 words. Focus on AI/ML skills, research background, and impact."
    )
    letter = ai_respond(JOB_SYSTEM, prompt)
    _log("jobs", {"action": "cover-letter", "company": company, "role": role})
    return jsonify({"cover_letter": letter, "agent": "Job Application Agent"})


@app.route("/api/agents/jobs/interview-prep", methods=["POST"])
def interview_prep():
    data = request.get_json() or {}
    company = data.get("company", "")
    role = data.get("role", "")
    focus = data.get("focus", "general")
    prompt = (
        f"Generate 5 strong interview Q&A pairs for {role} at {company}. "
        f"Focus area: {focus}. Include STAR-method answers relevant to AI/ML engineering."
    )
    prep = ai_respond(JOB_SYSTEM, prompt)
    return jsonify({"prep": prep, "agent": "Job Application Agent"})


@app.route("/api/agents/jobs/stats")
def jobs_stats():
    jobs = _load_jobs()
    statuses = {}
    for j in jobs:
        s = j.get("status", "Applied")
        statuses[s] = statuses.get(s, 0) + 1
    return jsonify({
        "total": len(jobs),
        "by_status": statuses,
        "recent": jobs[-3:][::-1] if jobs else [],
    })


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 3 — RECRUITER COMMUNICATION AGENT
# ══════════════════════════════════════════════════════════════════════════════

RECRUITER_SYSTEM = """You are Ghazal's Recruiter Communication AI Agent.
Help craft perfect responses to recruiters — whether accepting, declining, 
negotiating, or requesting more information. 
Ghazal is an experienced AI/ML engineer. Always be professional, concise, and strategic.
Focus on mutual benefit and maintaining long-term relationships."""

@app.route("/api/agents/recruiter/respond", methods=["POST"])
def recruiter_respond():
    data = request.get_json() or {}
    recruiter_msg = data.get("message", "")
    response_type = data.get("response_type", "interested")  # interested | decline | more-info | negotiate
    context = data.get("context", "")
    prompt = (
        f"Recruiter message:\n{recruiter_msg}\n\n"
        f"Response type: {response_type}\n"
        f"Context: {context}\n\n"
        f"Draft a professional response."
    )
    response = ai_respond(RECRUITER_SYSTEM, prompt)
    _log("recruiter", {"action": "respond", "type": response_type})
    return jsonify({"response": response, "agent": "Recruiter Agent"})


@app.route("/api/agents/recruiter/evaluate", methods=["POST"])
def recruiter_evaluate():
    data = request.get_json() or {}
    message = data.get("message", "")
    prompt = (
        f"Analyze this recruiter message and provide:\n"
        f"1. Opportunity score (1-10)\n"
        f"2. Red flags (if any)\n"
        f"3. Key questions to ask\n"
        f"4. Recommended next action\n\n"
        f"Message:\n{message}"
    )
    analysis = ai_respond(RECRUITER_SYSTEM, prompt)
    return jsonify({"analysis": analysis, "agent": "Recruiter Agent"})


@app.route("/api/agents/recruiter/salary-negotiation", methods=["POST"])
def salary_negotiation():
    data = request.get_json() or {}
    offered = data.get("offered_salary", "")
    target = data.get("target_salary", "")
    role = data.get("role", "")
    prompt = (
        f"Help Ghazal negotiate salary for {role}. "
        f"Offered: {offered}. Target: {target}. "
        f"Write a professional counter-offer email."
    )
    negotiation = ai_respond(RECRUITER_SYSTEM, prompt)
    return jsonify({"negotiation": negotiation, "agent": "Recruiter Agent"})


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 4 — LINKEDIN AGENT
# ══════════════════════════════════════════════════════════════════════════════

LINKEDIN_SYSTEM = """You are Ghazal's LinkedIn AI Agent.
Help with connection requests, messages, profile optimization, posts, and networking.
Ghazal is an AI/ML engineer and researcher. 
Make all messages personal, genuine, value-focused, and under 300 characters for 
connection requests (LinkedIn limit). Posts should be engaging and thought-leadership-oriented."""

@app.route("/api/agents/linkedin/connect", methods=["POST"])
def linkedin_connect():
    data = request.get_json() or {}
    name = data.get("name", "")
    role = data.get("role", "")
    company = data.get("company", "")
    reason = data.get("reason", "networking")
    prompt = (
        f"Write a LinkedIn connection request note to {name}, {role} at {company}. "
        f"Reason for connecting: {reason}. Must be under 300 characters. Be genuine."
    )
    note = ai_respond(LINKEDIN_SYSTEM, prompt)
    return jsonify({"note": note, "agent": "LinkedIn Agent", "char_count": len(note)})


@app.route("/api/agents/linkedin/message", methods=["POST"])
def linkedin_message():
    data = request.get_json() or {}
    recipient = data.get("recipient", "")
    purpose = data.get("purpose", "")
    context = data.get("context", "")
    prompt = f"Write a LinkedIn DM to {recipient}. Purpose: {purpose}. Context: {context}"
    message = ai_respond(LINKEDIN_SYSTEM, prompt)
    return jsonify({"message": message, "agent": "LinkedIn Agent"})


@app.route("/api/agents/linkedin/post", methods=["POST"])
def linkedin_post():
    data = request.get_json() or {}
    topic = data.get("topic", "")
    tone = data.get("tone", "professional")  # professional | casual | inspirational
    prompt = (
        f"Write a LinkedIn post about: {topic}. "
        f"Tone: {tone}. Include relevant hashtags. "
        f"Make it engaging and showcase Ghazal's AI/ML expertise. Under 1300 characters."
    )
    post = ai_respond(LINKEDIN_SYSTEM, prompt)
    return jsonify({"post": post, "agent": "LinkedIn Agent"})


@app.route("/api/agents/linkedin/profile-review", methods=["POST"])
def linkedin_profile():
    data = request.get_json() or {}
    section = data.get("section", "summary")
    current = data.get("current_text", "")
    prompt = (
        f"Review and rewrite this LinkedIn {section} section for an AI/ML engineer:\n"
        f"{current}\n\n"
        f"Make it keyword-rich, results-oriented, and compelling to recruiters."
    )
    improved = ai_respond(LINKEDIN_SYSTEM, prompt)
    return jsonify({"improved": improved, "agent": "LinkedIn Agent"})


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 5 — FOLLOW-UP AGENT
# ══════════════════════════════════════════════════════════════════════════════

FOLLOWUPS_FILE = DATA_DIR / "followups" / "followups.json"
FOLLOWUP_SYSTEM = """You are Ghazal's Follow-Up AI Agent.
Track and draft timely, professional follow-up messages for job applications,
recruiter conversations, networking contacts, and interviews.
Make each follow-up feel personal, not generic."""

def _load_followups():
    if FOLLOWUPS_FILE.exists():
        return json.loads(FOLLOWUPS_FILE.read_text())
    return []

def _save_followups(items):
    FOLLOWUPS_FILE.write_text(json.dumps(items, indent=2))


@app.route("/api/agents/followups", methods=["GET"])
def followups_list():
    items = _load_followups()
    today = datetime.date.today().isoformat()
    due = [f for f in items if f.get("due_date", "") <= today and f.get("status") == "pending"]
    return jsonify({"followups": items, "due_today": due})


@app.route("/api/agents/followups", methods=["POST"])
def followups_add():
    data = request.get_json() or {}
    items = _load_followups()
    item = {
        "id": len(items) + 1,
        "contact": data.get("contact", ""),
        "context": data.get("context", ""),
        "type": data.get("type", "email"),  # email | linkedin | phone
        "due_date": data.get("due_date", (datetime.date.today() + datetime.timedelta(days=3)).isoformat()),
        "status": "pending",
        "created_at": datetime.datetime.now().isoformat(),
        "notes": data.get("notes", ""),
    }
    items.append(item)
    _save_followups(items)
    return jsonify({"success": True, "followup": item})


@app.route("/api/agents/followups/<int:fid>/complete", methods=["PUT"])
def followups_complete(fid):
    items = _load_followups()
    for f in items:
        if f["id"] == fid:
            f["status"] = "done"
            f["completed_at"] = datetime.datetime.now().isoformat()
    _save_followups(items)
    return jsonify({"success": True})


@app.route("/api/agents/followups/draft", methods=["POST"])
def followups_draft():
    data = request.get_json() or {}
    contact = data.get("contact", "")
    context = data.get("context", "")
    days_since = data.get("days_since", 5)
    ftype = data.get("type", "email")
    prompt = (
        f"Draft a {ftype} follow-up for {contact}. "
        f"Context: {context}. "
        f"It has been {days_since} days since last contact. "
        f"Be concise, polite, and add value."
    )
    draft = ai_respond(FOLLOWUP_SYSTEM, prompt)
    return jsonify({"draft": draft, "agent": "Follow-Up Agent"})


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 6 — DAILY TASKS AGENT
# ══════════════════════════════════════════════════════════════════════════════

TASKS_FILE = DATA_DIR / "tasks" / "tasks.json"
TASKS_SYSTEM = """You are Ghazal's Daily Task AI Agent.
Help prioritize tasks, create schedules, set reminders, and suggest productivity improvements.
Focus on job search activities, research tasks, and career development goals."""

def _load_tasks():
    if TASKS_FILE.exists():
        return json.loads(TASKS_FILE.read_text())
    return []

def _save_tasks(tasks):
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))


@app.route("/api/agents/tasks", methods=["GET"])
def tasks_list():
    tasks = _load_tasks()
    today = datetime.date.today().isoformat()
    today_tasks = [t for t in tasks if t.get("date") == today and t.get("status") != "done"]
    return jsonify({"tasks": tasks, "today": today_tasks})


@app.route("/api/agents/tasks", methods=["POST"])
def tasks_add():
    data = request.get_json() or {}
    tasks = _load_tasks()
    task = {
        "id": len(tasks) + 1,
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "category": data.get("category", "general"),
        "priority": data.get("priority", "medium"),
        "date": data.get("date", datetime.date.today().isoformat()),
        "status": "pending",
        "created_at": datetime.datetime.now().isoformat(),
    }
    tasks.append(task)
    _save_tasks(tasks)
    return jsonify({"success": True, "task": task})


@app.route("/api/agents/tasks/<int:task_id>/done", methods=["PUT"])
def tasks_done(task_id):
    tasks = _load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "done"
            t["completed_at"] = datetime.datetime.now().isoformat()
    _save_tasks(tasks)
    return jsonify({"success": True})


@app.route("/api/agents/tasks/<int:task_id>", methods=["DELETE"])
def tasks_delete(task_id):
    tasks = [t for t in _load_tasks() if t["id"] != task_id]
    _save_tasks(tasks)
    return jsonify({"success": True})


@app.route("/api/agents/tasks/plan-day", methods=["POST"])
def plan_day():
    data = request.get_json() or {}
    goals = data.get("goals", "job search and coding")
    pending = data.get("pending_tasks", "")
    prompt = (
        f"Create a focused daily schedule for Ghazal. "
        f"Goals: {goals}. Pending tasks: {pending}. "
        f"Include time blocks for: email review, job applications, LinkedIn, "
        f"coding practice, research, and breaks. Output as a structured plan."
    )
    plan = ai_respond(TASKS_SYSTEM, prompt)
    return jsonify({"plan": plan, "agent": "Daily Tasks Agent"})


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 7 — MASTER CHAT AGENT (Orchestrator)
# ══════════════════════════════════════════════════════════════════════════════

MASTER_SYSTEM = """You are Ghazal's Personal AI Assistant — an intelligent orchestrator 
managing Email, Job Applications, Recruiter Communication, LinkedIn, Follow-ups, and Daily Tasks.

Ghazal is an AI/ML engineer and researcher actively seeking opportunities.

When given a task:
1. Identify which agent(s) should handle it
2. Provide a clear, actionable response
3. If drafting content, produce ready-to-use text
4. Be proactive — suggest follow-up actions

Always be: Professional, strategic, concise, and results-focused."""

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    message = data.get("message", "")
    history = data.get("history", [])

    messages = [{"role": "system", "content": MASTER_SYSTEM}]
    for h in history[-6:]:  # keep last 6 turns for context
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": message})

    if not OPENAI_AVAILABLE or not openai_client:
        reply = mock_ai_response(MASTER_SYSTEM, message)
    else:
        try:
            resp = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1500,
            )
            reply = resp.choices[0].message.content.strip()
        except Exception as e:
            reply = f"⚠️ Error: {str(e)}"

    _log("chat", {"message": message[:200], "reply": reply[:200]})
    return jsonify({"reply": reply})


# ══════════════════════════════════════════════════════════════════════════════
# UTILITY
# ══════════════════════════════════════════════════════════════════════════════

def _log(agent: str, data: dict):
    log_file = DATA_DIR / "logs" / f"{agent}.jsonl"
    entry = {"ts": datetime.datetime.now().isoformat(), **data}
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


@app.route("/api/logs/<agent>")
def get_logs(agent):
    log_file = DATA_DIR / "logs" / f"{agent}.jsonl"
    if not log_file.exists():
        return jsonify({"logs": []})
    lines = log_file.read_text().strip().split("\n")
    logs = [json.loads(l) for l in lines if l]
    return jsonify({"logs": logs[-20:]})


@app.route("/api/gmail/connect")
def gmail_connect():
    success = init_gmail()
    return jsonify({"connected": success, "gmail": GMAIL_AVAILABLE})


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 8 — AUTO-APPLY BOT & GMAIL PROOF ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

import subprocess

@app.route("/api/agents/jobs/bot-status")
def bot_status():
    today = datetime.date.today().isoformat()
    log_file = DATA_DIR / "applications" / f"applied_{today}.json"
    applied = json.loads(log_file.read_text()) if log_file.exists() else []
    from job_bot import PROFILE
    return jsonify({
        "profile": PROFILE,
        "today_count": len(applied),
        "target": 50,
        "applied_today": applied,
    })

@app.route("/api/agents/jobs/start-bot", methods=["POST"])
def start_bot():
    subprocess.Popen(["python3", "job_bot.py"], cwd=str(Path(__file__).parent))
    _log("jobs", {"action": "start_bot"})
    return jsonify({"started": True, "message": "Auto-Apply Bot launched in background! Check Chrome window to log in to LinkedIn."})

@app.route("/api/agents/jobs/send-proof", methods=["POST"])
def trigger_proof_email():
    from job_bot import load_log, send_proof_email
    entries = load_log()
    if not entries:
        entries = _load_jobs()
    ok = send_proof_email(entries)
    return jsonify({"sent": ok, "count": len(entries)})

@app.route("/api/agents/jobs/proof-report")
def view_proof_report():
    app_dir = DATA_DIR / "applications"
    reports = sorted(app_dir.glob("proof_report_*.html"), reverse=True) if app_dir.exists() else []
    if reports:
        return reports[0].read_text()
    return "<h2>No proof report generated yet today. Run Auto-Apply Bot first!</h2>"


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 9 — WHATSAPP AGENT (Twilio Webhook + Outbound Proof Notifications)
# ══════════════════════════════════════════════════════════════════════════════

def handle_whatsapp_command(incoming_text: str) -> str:
    """Process a WhatsApp message from Ghazal and return the reply."""
    cmd = (incoming_text or "").strip()
    low = cmd.lower()

    if low in ["status", "report", "jobs", "proof"]:
        today = datetime.date.today().isoformat()
        log_file = DATA_DIR / "applications" / f"applied_{today}.json"
        applied = json.loads(log_file.read_text()) if log_file.exists() else []
        li_applied = [a for a in applied if "linkedin" in (a.get("platform") or "").lower() or "linkedin.com" in (a.get("url") or "").lower()]
        all_jobs = [j for j in _load_jobs() if "linkedin" in (j.get("notes") or "").lower() or "linkedin.com" in (j.get("url") or "").lower()]
        recent_lines = "\n".join(
            [f"• {a.get('company')} — {a.get('role')}" for a in (li_applied[-5:] or all_jobs[-5:])]
        ) or "None yet today"
        return (
            f"🤖 *Ghazal's AI Agent — LinkedIn Job Report*\n"
            f"📅 Date: {today}\n"
            f"✅ LinkedIn Applied Today: {len(li_applied)} / 50\n"
            f"📊 Total LinkedIn Tracked: {len(all_jobs)}\n\n"
            f"*Recent LinkedIn Applications:*\n{recent_lines}"
        )

    if low in ["apply", "start bot", "run bot", "apply jobs", "linkedin"]:
        subprocess.Popen(["python3", "-u", "job_bot.py"], cwd=str(Path(__file__).parent))
        _log("jobs", {"action": "whatsapp_start_bot_linkedin_only"})
        return (
            "🚀 *LinkedIn-Only Auto-Apply Bot Launched!*\n"
            "Applying 100% exclusively to LinkedIn jobs (Easy Apply + LinkedIn Company Forms).\n"
            "Reply *status* anytime to check progress!"
        )

    if low.startswith("apply http") or low.startswith("http://") or low.startswith("https://"):
        url = cmd.split()[-1].strip()
        if "linkedin.com" not in url.lower():
            return "⚠️ *LinkedIn-Only Mode Active:* Please send a LinkedIn job URL (`https://www.linkedin.com/jobs/...`). Other platforms are disabled."
        from job_bot import apply_single_job_url
        entry = apply_single_job_url(url)
        return (
            f"✅ *Applied on LinkedIn via WhatsApp!*\n"
            f"🏢 Company: {entry.get('company')}\n"
            f"💼 Role: {entry.get('role')}\n"
            f"📌 Status: {entry.get('status')}\n"
            f"🔗 {url}"
        )

    if low.startswith("tasks") or low == "todo":
        tasks = _load_tasks()
        pending = [t for t in tasks if t.get("status") != "done"]
        lines = "\n".join([f"• [{t.get('priority','med')}] {t.get('title')}" for t in pending[:8]]) or "No pending tasks 🎉"
        return f"✅ *Pending Tasks ({len(pending)}):*\n{lines}"

    # Otherwise, route to AI Master Assistant (cover letters, recruiter replies, emails, etc.)
    return ai_respond(MASTER_SYSTEM, cmd)


@app.route("/api/whatsapp/webhook", methods=["POST"])
def whatsapp_webhook():
    """Twilio / Meta WhatsApp incoming webhook."""
    incoming_msg = request.values.get("Body", "") or (request.get_json(silent=True) or {}).get("message", "")
    sender = request.values.get("From", "whatsapp")
    reply_text = handle_whatsapp_command(incoming_msg)
    _log("whatsapp", {"from": sender, "in": incoming_msg[:200], "out": reply_text[:200]})

    # If called via JSON API test, return JSON; if called by Twilio, return TwiML XML
    if request.is_json:
        return jsonify({"reply": reply_text})
    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply_text}</Message></Response>'
    return twiml, 200, {"Content-Type": "application/xml"}


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    print(f"\n{'='*55}")
    print(f"  🤖 Personal AI Agent System — Starting Up")
    print(f"{'='*55}")
    print(f"  🌐 URL:    http://localhost:{port}")
    print(f"  🧠 OpenAI: {'✅ Connected' if OPENAI_AVAILABLE else '⚠️  Add OPENAI_API_KEY to .env'}")
    print(f"  📧 Gmail:  {'✅ Connected' if GMAIL_AVAILABLE else '⚠️  Add credentials.json'}")
    print(f"{'='*55}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
