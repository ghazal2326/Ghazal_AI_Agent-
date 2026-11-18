# 🤖 Ghazal's Personal AI Agent System (Pure Backend + LinkedIn Auto-Apply + WhatsApp)

A production-grade, pure-Python Multi-Agent System built with **Flask, OpenAI (`gpt-4o-mini`), and Selenium**.
Manages **100% LinkedIn Job Applications (Easy Apply + LinkedIn External Company Forms), AI Q&A Form Filling, Email, Recruiter Communication, LinkedIn Networking, Follow-ups, Daily Tasks, and WhatsApp Remote Control** — with zero frontend bloat.

---

## 💼 1. How to Apply to Jobs (100% LinkedIn-Only Auto-Apply Bot)

The Auto-Apply Bot (`job_bot.py`) applies **exclusively on LinkedIn** (both **LinkedIn Easy Apply** and **LinkedIn Company Direct Forms** opened from LinkedIn job cards).

### What the Bot Does Automatically:
1. **Verifies Real LinkedIn Login (`li_at` cookie):** Uses your persistent Chrome profile (`~/.ghazal_ai_chrome_profile`) so you stay logged into LinkedIn across runs.
2. **Dual-Mode LinkedIn Search (12 AI/ML Queries × 2 Passes):**
   * Searches *AI Engineer, ML Engineer, Machine Learning Engineer, LLM Engineer, AI/ML Engineer, GenAI Engineer, Agentic AI Engineer, RAG Engineer, Applied AI Engineer, and MLOps Engineer* across the **United States** and **San Francisco Bay Area**.
   * **Pass 1 (`Easy Apply`):** Completes multi-step LinkedIn Easy Apply modals directly inside LinkedIn.
   * **Pass 2 (`Company Direct Form`):** Clicks LinkedIn `Apply ↗` buttons that open the company's direct form in a new tab, uploads `Ghazal_Sultan_Resume.pdf`, fills out all fields, answers custom screening Q&A using OpenAI `gpt-4o-mini`, submits, and returns to LinkedIn.
3. **4-Mode AI Q&A Form Engine:**
   * Extracts questions from labels, fieldsets, and React containers (`_extract_field_question`).
   * Enforces deterministic legal truth (**US Citizen**, **No Visa Sponsorship Needed**, **9+ Years Experience**, **$160,000–$200,000** salary expectation, **Mountain House, CA 95391**) and uses `gpt-4o-mini` + your full resume history (Gainwell Technologies, Labcorp, E-TRADE, Walgreens) for custom technical/essay questions.

### Run the LinkedIn Auto-Apply Bot from Terminal
Open **Terminal** and run:
```bash
cd "/Users/ghazal/Desktop/Ghazal AI Agent/Ghazal AI Agent"
python3 -u job_bot.py
```
* **Stop Early Anytime:** Press `Ctrl + C` in Terminal — the bot will still save all completed applications and generate your Proof Report.

---

## 📄 2. How to Check Your Job Application Proof Report

Every LinkedIn application the bot submits is recorded with the **Company Name, Role, Platform (`LinkedIn Easy Apply` or `LinkedIn (Company Form)`), Timestamp, and Direct LinkedIn Job URL (`https://www.linkedin.com/jobs/view/<job_id>/`)**.

### Way 1: Open the Visual HTML Proof Report in Browser (Recommended)
After every bot run, a formatted HTML report is saved in `data/applications/proof_report_YYYY-MM-DD.html` (and pops open automatically when the run finishes).
To open your saved proof reports anytime from Terminal, run:
```bash
open "/Users/ghazal/Desktop/Ghazal AI Agent/Ghazal AI Agent/data/applications/"proof_report_*.html
```

### Way 2: View the JSON Application Log in Terminal
All application records are saved by date in `data/applications/applied_YYYY-MM-DD.json`.
To view today's JSON log in Terminal:
```bash
cat "/Users/ghazal/Desktop/Ghazal AI Agent/Ghazal AI Agent/data/applications/applied_$(date +%F).json"
```

### Way 3: Check via Backend API or Gmail (`ghazal.sultan1616@gmail.com`)
1. **Via Backend API:** When the backend server is running, view your latest HTML proof report at **http://localhost:8765/api/agents/jobs/proof-report** or check live JSON status via:
   ```bash
   curl -s http://localhost:8765/api/agents/jobs/bot-status | python3 -m json.tool
   ```
2. **LinkedIn & Company Confirmations in Gmail:** Every LinkedIn Easy Apply and LinkedIn Company Form submission sends an automatic confirmation email directly to `ghazal.sultan1616@gmail.com`.
3. **Daily Summary Email from Bot:** To have the bot email the full HTML summary table to `ghazal.sultan1616@gmail.com`, generate a 16-character **Google App Password** at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) and set it in `.env`:
   ```env
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

---

## 🚀 3. How to Start & Restart the Backend API Server

### Start the Backend Server
Open **Terminal** and run:
```bash
cd "/Users/ghazal/Desktop/Ghazal AI Agent/Ghazal AI Agent"
bash start.sh
```
This starts the pure Flask backend API at **http://localhost:8765**.

### Restart the Backend Server (After Editing `.env` or Code)
```bash
lsof -ti:8765 | xargs kill -9 2>/dev/null; cd "/Users/ghazal/Desktop/Ghazal AI Agent/Ghazal AI Agent" && bash start.sh
```

---

## 📱 4. How to Apply to Jobs & Check Reports via WhatsApp (`+1 669-213-3034`)

You can control your LinkedIn Auto-Apply Bot and check your Proof Reports directly from your phone on **WhatsApp**:

### Step 1: Start the WhatsApp Agent on Your Mac
Open **Terminal** and run:
```bash
cd "/Users/ghazal/Desktop/Ghazal AI Agent/Ghazal AI Agent"
python3 -u whatsapp_agent.py
```
1. Chrome will open **https://web.whatsapp.com**.
2. Scan the QR code once using your phone (**WhatsApp → Settings → Linked Devices → Link a Device**). Your login session is saved in `~/.ghazal_wa_bot/DefaultProfile`.
3. In that Chrome WhatsApp window on your Mac, **click on your own `"Ghazal (You)"` ("Message Yourself") chat** so it is open on the right side of the screen.

### Step 2: Send Commands from Your Phone's WhatsApp
Open your **`"Ghazal (You)"`** chat on your phone and send any of these messages:

* **Run the LinkedIn Auto-Apply Bot (50/day):**
  ```text
  apply
  ```
  → Remotely launches `job_bot.py` on your Mac to apply to LinkedIn Easy Apply & LinkedIn Company Form jobs.

* **Apply to One Specific Job URL:**
  ```text
  apply https://www.linkedin.com/jobs/view/4484762372/
  ```
  → Opens that exact job link, uploads `Ghazal_Sultan_Resume.pdf`, answers all custom Q&A questions using OpenAI `gpt-4o-mini`, submits the form, and replies on WhatsApp with confirmation!

* **Check Your Live Job Application Proof Report:**
  ```text
  status
  ```
  *(or `report` / `proof`)*
  → Replies on WhatsApp with your live daily application count and the list of recent companies & roles applied to.

* **Check Your Pending Daily Tasks:**
  ```text
  tasks
  ```
  → Lists your pending tasks and priorities.

* **Ask the AI Assistant Anything (Recruiter Replies, Follow-ups, Cover Letters):**
  ```text
  !write a reply to a Google recruiter saying I am available Tuesday at 2pm
  ```
  → Any message starting with `!` is answered by OpenAI `gpt-4o-mini` using your full resume profile!

---

## 📁 5. Complete File Structure & Exact Paths

```text
/Users/ghazal/Desktop/Ghazal AI Agent/Ghazal AI Agent/
├── job_bot.py                                  ← 100% LinkedIn Auto-Apply Bot + Universal AI Q&A Form Engine
├── whatsapp_agent.py                           ← WhatsApp Web Remote Control & Proof Report Agent
├── app.py                                      ← Pure Flask Backend API Server (port 8765, 35+ routes)
├── Ghazal_Sultan_Resume.pdf                    ← Your 3-page resume uploaded automatically to forms
├── Ghazal_AI_Agent_Architecture_and_Plan.pdf   ← 6-Page Master Technical Reference & Architecture Blueprint
├── start.sh                                    ← Backend server launcher script
├── test_agents.py                              ← Automated test suite for all 19 API endpoints
├── requirements.txt                            ← Python dependencies
├── .env                                        ← API keys (OpenAI key + Gmail App Password)
└── data/
    ├── applications/
    │   ├── applied_YYYY-MM-DD.json             ← Daily auto-apply JSON logs (with LinkedIn job URLs)
    │   └── proof_report_YYYY-MM-DD.html        ← Daily visual HTML proof reports
    ├── jobs/applications.json                  ← Master synced job tracker database
    ├── followups/followups.json                ← Follow-up tracker database
    ├── tasks/tasks.json                        ← Daily tasks database
    └── logs/*.jsonl                            ← Append-only agent audit logs
```

---

## 🧪 6. Test All Backend Endpoints Anytime

While the backend server is running, open a second Terminal window and run:
```bash
cd "/Users/ghazal/Desktop/Ghazal AI Agent/Ghazal AI Agent"
python3 test_agents.py
```
Expected output: **`19/19 tests passed 🎉`**
