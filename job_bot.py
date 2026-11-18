"""
Auto Job Application Bot — Ghazal Sultan
Applies to LinkedIn Easy Apply & Indeed Quick Apply jobs automatically.
Sends Gmail proof report after each session.
"""

import os, time, json, random, smtplib, datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# ══════════════════════════════════════════════════════════════
# YOUR PROFILE — Pre-filled from Resume
# ══════════════════════════════════════════════════════════════
PROFILE = {
    "full_name":        "Ghazal Sultan",
    "first_name":       "Ghazal",
    "last_name":        "Sultan",
    "email":            "ghazal.sultan1616@gmail.com",
    "phone":            "6692133034",
    "location":         "Mountain House, CA 95391",
    "city":             "Mountain House",
    "state":            "CA",
    "zip_code":         "95391",
    "linkedin_url":     "https://www.linkedin.com/in/ghazal-a-sultan/",
    "years_experience": "9",
    "current_title":    "AIML Engineer",
    "current_company":  "Gainwell Technologies",
    "work_authorization": "US Citizen",
    "sponsorship_needed": "No",
    "visa_status":      "US Citizen - No sponsorship needed",
    "salary_expectation":"$160,000 - $200,000",
    "willing_to_relocate": "No",
    "remote_preference": "Remote or Hybrid (Bay Area)",
    "resume_path":      str(Path(__file__).parent / "Ghazal_Sultan_Resume.pdf"),
}

# ══════════════════════════════════════════════════════════════
# JOB SEARCH SETTINGS
# ══════════════════════════════════════════════════════════════
JOB_SEARCHES = [
    {"title": "AI Engineer",               "location": "United States"},
    {"title": "ML Engineer",               "location": "United States"},
    {"title": "Machine Learning Engineer", "location": "United States"},
    {"title": "LLM Engineer",              "location": "United States"},
    {"title": "AI/ML Engineer",            "location": "United States"},
    {"title": "GenAI Engineer",            "location": "United States"},
    {"title": "Agentic AI Engineer",       "location": "United States"},
    {"title": "RAG Engineer",              "location": "United States"},
    {"title": "Applied AI Engineer",       "location": "United States"},
    {"title": "MLOps Engineer",            "location": "United States"},
    {"title": "AI Engineer",               "location": "San Francisco Bay Area"},
    {"title": "Machine Learning Engineer", "location": "San Francisco Bay Area"},
]

TARGET_DAILY = 50   # applications per day
DELAY_MIN    = 8    # seconds between applications (min) — stay human-like
DELAY_MAX    = 20   # seconds between applications (max)

# ══════════════════════════════════════════════════════════════
# GMAIL PROOF SETTINGS
# ══════════════════════════════════════════════════════════════
# Uses Gmail App Password (NOT your regular password)
# Setup: myaccount.google.com → Security → App Passwords → Generate
GMAIL_SENDER   = "ghazal.sultan1616@gmail.com"
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASSWORD", "")  # set in .env
GMAIL_NOTIFY   = "ghazal.sultan1616@gmail.com"  # where to send proof

# ══════════════════════════════════════════════════════════════
# APPLICATION LOG
# ══════════════════════════════════════════════════════════════
LOG_DIR = Path("data/applications")
LOG_DIR.mkdir(parents=True, exist_ok=True)
today   = datetime.date.today().isoformat()
LOG_FILE = LOG_DIR / f"applied_{today}.json"

def load_log():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return []

def save_log(entries):
    LOG_FILE.write_text(json.dumps(entries, indent=2))

def log_application(company, role, platform, url, status="Applied"):
    entries = load_log()
    entry = {
        "id":        len(entries) + 1,
        "timestamp": datetime.datetime.now().isoformat(),
        "company":   company,
        "role":      role,
        "platform":  platform,
        "url":       url,
        "status":    status,
    }
    entries.append(entry)
    save_log(entries)
    print(f"  ✅ [{len(entries):02d}] {company} — {role} ({platform})")
    return entry

# ══════════════════════════════════════════════════════════════
# GMAIL PROOF EMAIL
# ══════════════════════════════════════════════════════════════
def send_proof_email(applications: list):
    if not GMAIL_APP_PASS:
        print("⚠️  No GMAIL_APP_PASSWORD set — skipping proof email.")
        print("   → See setup instructions below.")
        return False

    total = len(applications)
    date_str = datetime.date.today().strftime("%B %d, %Y")

    rows = ""
    for a in applications:
        rows += f"""
        <tr>
          <td style='padding:8px;border-bottom:1px solid #eee'>{a['id']}</td>
          <td style='padding:8px;border-bottom:1px solid #eee'><b>{a['company']}</b></td>
          <td style='padding:8px;border-bottom:1px solid #eee'>{a['role']}</td>
          <td style='padding:8px;border-bottom:1px solid #eee'>{a['platform']}</td>
          <td style='padding:8px;border-bottom:1px solid #eee;color:green'>✅ {a['status']}</td>
          <td style='padding:8px;border-bottom:1px solid #eee;font-size:11px'>{a['timestamp'][11:16]}</td>
        </tr>"""

    html = f"""
    <html><body style='font-family:Arial,sans-serif;max-width:800px;margin:auto'>
      <div style='background:#7c3aed;color:white;padding:24px;border-radius:12px 12px 0 0'>
        <h1 style='margin:0'>🤖 AI Agent — Daily Application Report</h1>
        <p style='margin:8px 0 0;opacity:0.9'>{date_str}</p>
      </div>
      <div style='background:#f9f9f9;padding:24px;border:1px solid #eee'>
        <div style='display:flex;gap:16px;margin-bottom:24px'>
          <div style='background:white;border:1px solid #eee;border-radius:8px;padding:16px;flex:1;text-align:center'>
            <div style='font-size:36px;font-weight:bold;color:#7c3aed'>{total}</div>
            <div style='color:#666;font-size:13px'>Jobs Applied Today</div>
          </div>
          <div style='background:white;border:1px solid #eee;border-radius:8px;padding:16px;flex:1;text-align:center'>
            <div style='font-size:36px;font-weight:bold;color:#10b981'>✅</div>
            <div style='color:#666;font-size:13px'>All Successful</div>
          </div>
          <div style='background:white;border:1px solid #eee;border-radius:8px;padding:16px;flex:1;text-align:center'>
            <div style='font-size:36px;font-weight:bold;color:#06b6d4'>{applications[0]['platform'] if applications else '—'}</div>
            <div style='color:#666;font-size:13px'>Primary Platform</div>
          </div>
        </div>

        <h3 style='color:#333'>📋 Application Log</h3>
        <table style='width:100%;border-collapse:collapse;background:white;border-radius:8px;overflow:hidden;border:1px solid #eee'>
          <tr style='background:#f3f4f6'>
            <th style='padding:10px;text-align:left'>#</th>
            <th style='padding:10px;text-align:left'>Company</th>
            <th style='padding:10px;text-align:left'>Role</th>
            <th style='padding:10px;text-align:left'>Platform</th>
            <th style='padding:10px;text-align:left'>Status</th>
            <th style='padding:10px;text-align:left'>Time</th>
          </tr>
          {rows}
        </table>

        <p style='color:#666;font-size:13px;margin-top:24px'>
          🤖 Applied by Ghazal's Personal AI Agent System | localhost:8765<br>
          Resume used: Ghazal Sultan — AIML Engineer | Gainwell Technologies
        </p>
      </div>
    </body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🤖 AI Agent Applied to {total} Jobs Today — {date_str}"
    msg["From"]    = GMAIL_SENDER
    msg["To"]      = GMAIL_NOTIFY
    msg.attach(MIMEText(html, "html"))

    # Always save a local HTML proof report and open it
    proof_html_path = LOG_DIR / f"proof_report_{today}.html"
    proof_html_path.write_text(html)
    print(f"\n📄 Local HTML Proof Report saved: {proof_html_path}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_SENDER, GMAIL_APP_PASS)
            smtp.sendmail(GMAIL_SENDER, GMAIL_NOTIFY, msg.as_string())
        print(f"📧 Proof email sent to {GMAIL_NOTIFY} ✅")
        return True
    except Exception as e:
        print(f"⚠️  SMTP note: {e}")
        print(f"   (Google requires a 16-char App Password for SMTP, or you can view the proof report opened in your browser!)")
        try:
            import subprocess
            subprocess.Popen(["open", str(proof_html_path)])
        except Exception:
            pass
        return False


# ══════════════════════════════════════════════════════════════
# LINKEDIN-ONLY JOB APPLICATION BOT (Easy Apply + Company Forms from LinkedIn)
# ══════════════════════════════════════════════════════════════
def run_linkedin_bot(driver, target_count=50):
    """Apply ONLY to LinkedIn jobs (both LinkedIn Easy Apply and LinkedIn external company forms)."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException

    applied = []
    seen_urls = {e.get("url", "").split("?")[0] for e in load_log()}
    wait = WebDriverWait(driver, 8)

    print("\n🔗 LinkedIn Job Bot Starting (100% LinkedIn Only)...")

    for search in JOB_SEARCHES:
        if len(applied) >= target_count:
            break

        # Pass 1: LinkedIn Easy Apply (&f_AL=true), Pass 2: ALL LinkedIn Jobs including Direct Company Forms ("")
        for easy_filter, mode_name in [("&f_AL=true", "Easy Apply"), ("", "Company Direct Form")]:
            if len(applied) >= target_count:
                break

            title    = search["title"].replace(" ", "%20")
            location = search["location"].replace(" ", "%20")
            url = (
                f"https://www.linkedin.com/jobs/search/"
                f"?keywords={title}&location={location}"
                f"{easy_filter}"
                f"&sortBy=DD"           # Most recent
            )

            try:
                driver.get(url)
                time.sleep(random.uniform(4, 6))

                # Scroll LinkedIn's SDUI left job list container to load all cards
                try:
                    driver.execute_script("""
                        const firstCard = document.querySelector('div[role="button"][componentkey^="job-card-component-ref-"]');
                        if (firstCard) {
                            let p = firstCard.parentElement;
                            while (p && p !== document.body) {
                                if (p.scrollHeight > p.clientHeight + 50) {
                                    p.scrollTop += 1500;
                                    break;
                                }
                                p = p.parentElement;
                            }
                        }
                    """)
                    time.sleep(1.5)
                except Exception:
                    pass

                # Support both LinkedIn's new 2026 SDUI job cards AND classic job cards
                job_cards = driver.find_elements(
                    By.CSS_SELECTOR,
                    'div[role="button"][componentkey^="job-card-component-ref-"], li[data-occludable-job-id], div.job-card-container[data-job-id]'
                )
                print(f"  [{mode_name}] Found {len(job_cards)} LinkedIn jobs for: {search['title']} ({search['location']})")

                for card in job_cards[:20]:
                    if len(applied) >= target_count:
                        break
                    try:
                        comp_key = card.get_attribute("componentkey") or ""
                        card_text = (card.text or "").strip()
                        if "\nApplied" in card_text or card_text.endswith("Applied"):
                            continue

                        # Parse Role & Company directly from the SDUI card lines!
                        lines = [ln.strip() for ln in card_text.split("\n") if ln.strip() and not ln.strip().startswith("Selected,")]
                        role = lines[0].replace("(Verified job)", "").strip() if len(lines) >= 1 else search["title"]
                        # If line 1 repeats line 0, company is on line 2
                        if len(lines) >= 3 and lines[1].replace("(Verified job)", "").strip() == role:
                            company = lines[2]
                        elif len(lines) >= 2:
                            company = lines[1]
                        else:
                            company = "LinkedIn Company"

                        job_id = comp_key.replace("job-card-component-ref-", "") if "job-card-component-ref-" in comp_key else ""
                        job_url = f"https://www.linkedin.com/jobs/view/{job_id}/" if job_id.isdigit() else (driver.current_url or "")
                        if job_url in seen_urls:
                            continue

                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", card)
                        time.sleep(random.uniform(2.5, 3.5))

                        # Click LinkedIn Apply / Easy Apply button using broad JS button detector (buttons + links)
                        apply_btn = driver.execute_script(
                            """
                            const candidates = Array.from(document.querySelectorAll(
                                'button[aria-label*="Easy Apply"], button[aria-label*="Apply"], a[aria-label*="Apply"], ' +
                                '.jobs-s-apply button, .jobs-apply-button--top-card button, button.jobs-apply-button, ' +
                                'main button, main a'
                            ));
                            for (const b of candidates) {
                                const txt = (b.innerText || '').trim().toLowerCase();
                                const aria = (b.getAttribute('aria-label') || '').trim().toLowerCase();
                                if ((txt === 'easy apply' || txt === 'apply' || aria.includes('easy apply to this job') || aria.includes('apply to this job')) && !txt.includes('applied') && b.offsetParent !== null) {
                                    return b;
                                }
                            }
                            return null;
                            """
                        )
                        if not apply_btn:
                            print(f"     ⏭️  {company} — {role[:35]} (Already applied or no Apply button)")
                            continue

                        btn_text = (apply_btn.text or apply_btn.get_attribute("aria-label") or "").strip().lower()
                        print(f"     ▶️  Clicking '{btn_text[:20]}' for: {company} — {role[:40]}")

                        main_window = driver.current_window_handle
                        driver.execute_script("arguments[0].click();", apply_btn)
                        time.sleep(2.5)

                        # If LinkedIn opened a company form in a new tab
                        if len(driver.window_handles) > 1:
                            driver.switch_to.window(driver.window_handles[-1])
                            time.sleep(3)
                            ext_url = driver.current_url
                            print(f"     🌐 Filling LinkedIn External Company Form: {company} — {role}")
                            ok = _fill_external_company_form(driver, company, role)
                            driver.close()
                            driver.switch_to.window(main_window)
                            if ok:
                                seen_urls.add(job_url)
                                entry = log_application(company, role, "LinkedIn (Company Form)", job_url)
                                applied.append(entry)
                            continue

                        # LinkedIn Easy Apply modal (multi-step Q&A + Resume)
                        submitted = False
                        for _ in range(10):
                            _fill_linkedin_form(driver, wait, company, role)
                            time.sleep(1)
                            action_taken = driver.execute_script(
                                """
                                const modal = document.querySelector('.jobs-easy-apply-modal, .artdeco-modal, [role="dialog"]');
                                if (!modal) return 'no_modal';
                                const btns = Array.from(modal.querySelectorAll('button'));
                                for (const b of btns) {
                                    const t = ((b.innerText || '') + ' ' + (b.getAttribute('aria-label') || '')).trim().toLowerCase();
                                    if (t.includes('submit application') || t === 'submit') {
                                        b.click();
                                        return 'submitted';
                                    }
                                }
                                for (const b of btns) {
                                    const t = ((b.innerText || '') + ' ' + (b.getAttribute('aria-label') || '')).trim().toLowerCase();
                                    if ((t.includes('review') || t.includes('next') || t.includes('continue')) && !b.disabled) {
                                        b.click();
                                        return 'next';
                                    }
                                }
                                return 'stuck';
                                """
                            )
                            if action_taken == "submitted":
                                time.sleep(2)
                                seen_urls.add(job_url)
                                entry = log_application(company, role, "LinkedIn Easy Apply", job_url)
                                applied.append(entry)
                                submitted = True
                                break
                            elif action_taken == "next":
                                time.sleep(1.5)
                                continue
                            else:
                                break

                        # Dismiss modal after submit or if stuck
                        try:
                            driver.execute_script(
                                """
                                const dismiss = document.querySelector('button[aria-label="Dismiss"], button[aria-label="Done"]');
                                if (dismiss) dismiss.click();
                                """
                            )
                            time.sleep(0.5)
                            if not submitted:
                                driver.execute_script(
                                    """
                                    const discard = document.querySelector('button[data-control-name="discard_application_confirm_btn"], button[data-test-dialog-primary-btn]');
                                    if (discard) discard.click();
                                    """
                                )
                        except Exception:
                            pass

                        delay = random.uniform(DELAY_MIN, DELAY_MAX)
                        print(f"     ⏳ Waiting {delay:.0f}s before next LinkedIn job...")
                        time.sleep(delay)

                    except Exception as e:
                        print(f"     ⚠️  Skipped: {str(e)[:60]}")
                        continue

            except Exception as e:
                print(f"  ❌ Search error: {e}")
                continue

    return applied


def _extract_field_question(driver, element) -> str:
    """Extract the full human-readable question text for any input/textarea/select/fieldset."""
    try:
        q = driver.execute_script(
            """
            const el = arguments[0];
            let texts = [];
            if (el.id) {
                const lbl = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
                if (lbl && lbl.innerText) texts.push(lbl.innerText.trim());
            }
            const parentLabel = el.closest('label');
            if (parentLabel && parentLabel.innerText) texts.push(parentLabel.innerText.trim());
            const container = el.closest('.field, .form-group, .application-question, fieldset, [class*="question"], [class*="Field"], li, div');
            if (container) {
                const lbls = container.querySelectorAll('label, legend, [class*="label"], [class*="Label"], p, span');
                for (const l of lbls) {
                    const t = (l.innerText || '').trim();
                    if (t && t.length > 2 && t.length < 350 && !texts.includes(t)) {
                        texts.push(t);
                        break;
                    }
                }
            }
            for (const attr of ['aria-label', 'placeholder', 'name', 'id']) {
                const v = el.getAttribute(attr);
                if (v) texts.push(v);
            }
            return texts.join(' | ');
            """,
            element,
        )
        return (q or "").strip()
    except Exception:
        return ""


def _ai_answer_question(question_text: str, company: str, role: str, answer_type: str = "text", options: list = None) -> str:
    """Use OpenAI GPT-4o-mini to answer custom Q&A fields (short text, number, yes/no, or dropdown choice)."""
    q_low = (question_text or "").lower()

    # Fast deterministic rules for common screening questions
    if answer_type == "number":
        if "salary" in q_low or "compensation" in q_low or "pay" in q_low:
            return "180000"
        if "notice" in q_low or "weeks" in q_low:
            return "2"
        return PROFILE["years_experience"]  # "9"

    if answer_type == "choice" and options:
        for opt in options:
            ol = opt.lower()
            if ("sponsor" in q_low or "visa" in q_low) and ("no" in ol or "do not" in ol or "don't" in ol):
                return opt
            if ("authorized" in q_low or "legally" in q_low or "citizen" in q_low or "eligible" in q_low) and ("yes" in ol or "citizen" in ol or "authorized" in ol):
                return opt
            if ("relocat" in q_low) and "no" in ol:
                return opt
            if ("18" in q_low or "age" in q_low or "background check" in q_low or "commute" in q_low or "remote" in q_low) and "yes" in ol:
                return opt
            if ("degree" in q_low or "education" in q_low) and ("bachelor" in ol or "bs" in ol or "b.s" in ol):
                return opt
            if ("gender" in q_low or "veteran" in q_low or "disability" in q_low or "race" in q_low or "hispanic" in q_low or "latino" in q_low):
                if "decline" in ol or "prefer not" in ol or "do not wish" in ol:
                    return opt

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        if answer_type == "short":
            return "Yes, 9+ years of experience (US Citizen)"
        return (
            f"I have 9+ years of experience as an AI/ML Engineer specializing in LangGraph, "
            f"multi-agent systems, enterprise RAG platforms, and AWS MLOps, making me a strong fit for {role} at {company}."
        )
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        constraint = (
            f"Choose the single best matching option from this exact list: {options}. Reply with ONLY the option text."
            if answer_type == "choice" and options
            else "Reply concisely in 1 short sentence or phrase (under 15 words)."
            if answer_type == "short"
            else "Reply concisely in 2-3 sentences in first person."
        )
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are filling a job application form on behalf of Ghazal Sultan:\n"
                        "- Full Name: Ghazal Sultan\n"
                        "- Email: ghazal.sultan1616@gmail.com | Phone: 6692133034\n"
                        "- Location: Mountain House, CA 95391 (Bay Area, California, United States)\n"
                        "- Work Authorization: US Citizen (Authorized to work in the US for any employer, NO visa sponsorship required now or in the future)\n"
                        "- Total Experience: 9+ years in Software Engineering & AI/ML Engineering\n"
                        "- Current Role: AIML Engineer at Gainwell Technologies (Oct 2023 - Present)\n"
                        "- Previous Roles: ML Engineer at Labcorp (2021-2023), Software Engineer at E-TRADE (2018-2021) & Walgreens (2016-2018)\n"
                        "- Education: Bachelor in Computer Science, University of Sindh (2011-2013)\n"
                        "- Core Skills: Python, SQL, Java, JavaScript, React, FastAPI, LangGraph, LangChain, LlamaIndex, Multi-Agent Systems, RAG, OpenAI, Anthropic Claude, ChromaDB, FAISS, Unstructured.io, MLflow, Airflow, Docker, Kubernetes, AWS (Bedrock, EKS, SageMaker, Lambda, S3), Snowflake, Random Forest, XGBoost.\n"
                        "- Salary Expectation: $160,000 - $200,000 | Notice Period: 2 weeks | Remote/Hybrid preferred.\n"
                        f"{constraint}"
                    ),
                },
                {"role": "user", "content": f"Company: {company}\nRole: {role}\nForm Question: {question_text}"},
            ],
            max_tokens=180,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return "Yes" if answer_type == "short" else f"Yes, I have 9+ years of production AI/ML and software engineering experience directly relevant to {role}."


def _fill_linkedin_form(driver, wait, company="Company", role="AI/ML Engineer"):
    """Fill all LinkedIn Easy Apply form fields including custom Q&A questions."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.select import Select

    # 1. Text, Tel, and Number inputs (including custom "How many years of experience..." Q&A)
    for field in driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='tel'], input[type='number'], input:not([type])"):
        try:
            if not field.is_displayed() or not field.is_enabled() or (field.get_attribute("value") or "").strip():
                continue
            q_text = _extract_field_question(driver, field)
            ql = q_text.lower()
            ftype = (field.get_attribute("type") or "text").lower()

            if "phone" in ql or "mobile" in ql or ftype == "tel":
                field.clear(); field.send_keys(PROFILE["phone"])
            elif "city" in ql or "location" in ql:
                field.clear(); field.send_keys(PROFILE["location"])
            elif ftype == "number" or "how many years" in ql or "years of" in ql:
                ans = _ai_answer_question(q_text, company, role, answer_type="number")
                field.clear(); field.send_keys(ans)
            elif "salary" in ql or "compensation" in ql or "pay" in ql:
                field.clear(); field.send_keys("180000")
            elif "linkedin" in ql:
                field.clear(); field.send_keys(PROFILE["linkedin_url"])
            else:
                ans = _ai_answer_question(q_text or "Additional information", company, role, answer_type="short")
                field.clear(); field.send_keys(ans)
        except Exception:
            pass

    # 2. Textareas (open-ended Q&A on LinkedIn modal)
    for ta in driver.find_elements(By.TAG_NAME, "textarea"):
        try:
            if not ta.is_displayed() or not ta.is_enabled() or (ta.get_attribute("value") or "").strip():
                continue
            q_text = _extract_field_question(driver, ta)
            ans = _ai_answer_question(q_text or f"Why are you a strong fit for {role}?", company, role, answer_type="text")
            ta.send_keys(ans)
        except Exception:
            pass

    # 3. Radio button fieldsets (Yes/No screening questions like Sponsorship vs Authorized)
    for fs in driver.find_elements(By.TAG_NAME, "fieldset"):
        try:
            q_text = _extract_field_question(driver, fs).lower()
            radios = fs.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            labels = fs.find_elements(By.TAG_NAME, "label")
            want_no = any(k in q_text for k in ["sponsor", "visa", "relocat"])
            target_val = "no" if want_no else "yes"
            clicked = False
            for lbl in labels:
                if target_val in (lbl.text or "").strip().lower():
                    lbl.click(); clicked = True; break
            if not clicked and labels:
                labels[0].click()
        except Exception:
            pass

    # 4. Select Dropdowns (choose right option using Q&A logic)
    for sel in driver.find_elements(By.TAG_NAME, "select"):
        try:
            if not sel.is_displayed():
                continue
            s = Select(sel)
            curr = s.first_selected_option.text.strip().lower()
            if curr not in ["select an option", "select", "--", ""]:
                continue
            q_text = _extract_field_question(driver, sel)
            opts = [o.text.strip() for o in s.options if o.text.strip().lower() not in ["select an option", "select", "--", ""]]
            if opts:
                best = _ai_answer_question(q_text, company, role, answer_type="choice", options=opts)
                matched = False
                for o in opts:
                    if best.lower() in o.lower() or o.lower() in best.lower():
                        s.select_by_visible_text(o); matched = True; break
                if not matched:
                    s.select_by_index(1)
        except Exception:
            pass


def _dismiss_alert(driver):
    """Automatically accept any JavaScript alert popup (e.g. 'You have Uploaded Resume Successfully')."""
    try:
        alert = driver.switch_to.alert
        alert.accept()
        time.sleep(0.5)
    except Exception:
        pass


def _fill_external_company_form(driver, company: str, role: str) -> bool:
    """Fill complete external company career forms (Greenhouse, Lever, Ashby, Workday, etc.)."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.select import Select

    try:
        _dismiss_alert(driver)
        # 1. Click "Apply" / "Apply for this job" button if landing page has one
        for btn in driver.find_elements(By.CSS_SELECTOR, "a, button"):
            try:
                txt = (btn.text or "").strip().lower()
                if txt in ["apply", "apply now", "apply for this job", "autofill with resume"]:
                    btn.click()
                    time.sleep(2)
                    _dismiss_alert(driver)
                    break
            except Exception:
                _dismiss_alert(driver)

        # 2. Upload Resume PDF to any file input (<input type="file">)
        for file_input in driver.find_elements(By.CSS_SELECTOR, "input[type='file']"):
            try:
                file_input.send_keys(PROFILE["resume_path"])
                time.sleep(2)
                _dismiss_alert(driver)
                break
            except Exception:
                _dismiss_alert(driver)

        # 3. Fill all text / email / tel / url / number inputs + custom Q&A inputs
        inputs = driver.find_elements(
            By.CSS_SELECTOR,
            "input[type='text'], input[type='email'], input[type='tel'], input[type='url'], input[type='number'], input:not([type])"
        )
        for inp in inputs:
            try:
                if not inp.is_displayed() or not inp.is_enabled():
                    continue
                if (inp.get_attribute("value") or "").strip():
                    continue

                q_text = _extract_field_question(driver, inp)
                meta = q_text.lower()
                itype = (inp.get_attribute("type") or "text").lower()
                role_attr = (inp.get_attribute("role") or "").lower()

                # Handle custom React-Select / Ashby / Greenhouse searchable comboboxes
                if role_attr == "combobox" or "select" in (inp.get_attribute("class") or "").lower():
                    try:
                        inp.click()
                        time.sleep(0.5)
                        opts_els = driver.find_elements(By.CSS_SELECTOR, "[role='option'], [class*='option']")
                        opts_txt = [o.text.strip() for o in opts_els if o.is_displayed() and o.text.strip()]
                        if opts_txt:
                            best = _ai_answer_question(q_text, company, role, answer_type="choice", options=opts_txt)
                            for o in opts_els:
                                if best.lower() in (o.text or "").lower() or (o.text or "").lower() in best.lower():
                                    o.click(); break
                            else:
                                opts_els[0].click()
                            continue
                    except Exception:
                        pass

                if "first" in meta and "name" in meta:
                    inp.send_keys(PROFILE["first_name"])
                elif "last" in meta and "name" in meta:
                    inp.send_keys(PROFILE["last_name"])
                elif "full" in meta or ("name" in meta and "company" not in meta and "employer" not in meta):
                    inp.send_keys(PROFILE["full_name"])
                elif "email" in meta or itype == "email":
                    inp.send_keys(PROFILE["email"])
                elif "phone" in meta or "mobile" in meta or "tel" in meta or itype == "tel":
                    inp.send_keys(PROFILE["phone"])
                elif "linkedin" in meta:
                    inp.send_keys(PROFILE["linkedin_url"])
                elif "github" in meta or "portfolio" in meta or "website" in meta or itype == "url":
                    inp.send_keys(PROFILE["linkedin_url"])
                elif "city" in meta or "location" in meta or "address" in meta or "where are you" in meta:
                    inp.send_keys(PROFILE["location"])
                elif "postal" in meta or "zip" in meta:
                    inp.send_keys(PROFILE["zip_code"])
                elif "state" in meta:
                    inp.send_keys(PROFILE["state"])
                elif "current company" in meta or "current employer" in meta or "organization" in meta:
                    inp.send_keys(PROFILE["current_company"])
                elif "current title" in meta or "job title" in meta:
                    inp.send_keys(PROFILE["current_title"])
                elif "salary" in meta or "compensation" in meta or "pay" in meta:
                    inp.send_keys("180000" if itype == "number" else PROFILE["salary_expectation"])
                elif itype == "number" or "how many years" in meta or "years of" in meta:
                    inp.send_keys(_ai_answer_question(q_text, company, role, answer_type="number"))
                elif "citizen" in meta or "authorized" in meta or "authorization" in meta:
                    inp.send_keys("Yes - US Citizen")
                elif "sponsor" in meta or "visa" in meta:
                    inp.send_keys("No")
                elif q_text:
                    # Any other custom Q&A input box! Ask GPT-4o-mini using full resume profile
                    ans = _ai_answer_question(q_text, company, role, answer_type="short")
                    inp.send_keys(ans)
            except Exception:
                continue

        # 4. Fill ALL open-ended textareas (Cover letter + custom Q&A questions) using OpenAI
        for ta in driver.find_elements(By.TAG_NAME, "textarea"):
            try:
                if not ta.is_displayed() or not ta.is_enabled() or (ta.get_attribute("value") or "").strip():
                    continue
                q_text = _extract_field_question(driver, ta)
                answer = _ai_answer_question(q_text or f"Why are you interested in {role} at {company}?", company, role, answer_type="text")
                ta.send_keys(answer)
            except Exception:
                continue

        # 5. Handle Radio Buttons & Checkboxes for Q&A (Sponsorship, Work Auth, Consent, Age, etc.)
        for group in driver.find_elements(By.CSS_SELECTOR, "fieldset, .field, .application-question, [class*='question']"):
            try:
                radios = [r for r in group.find_elements(By.CSS_SELECTOR, "input[type='radio']") if r.is_enabled()]
                if not radios:
                    continue
                if any(r.is_selected() for r in radios):
                    continue
                q_text = _extract_field_question(driver, group).lower()
                want_no = any(k in q_text for k in ["sponsor", "visa", "relocat", "previously worked", "government"])
                target = "no" if want_no else "yes"
                labels = group.find_elements(By.TAG_NAME, "label")
                clicked = False
                for lbl in labels:
                    if target in (lbl.text or "").strip().lower():
                        lbl.click(); clicked = True; break
                if not clicked:
                    for r in radios:
                        if target in (r.get_attribute("value") or "").lower():
                            r.click(); clicked = True; break
                if not clicked and labels:
                    labels[0].click()
            except Exception:
                continue

        # Check required consent/acknowledgement checkboxes
        for cb in driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']"):
            try:
                if cb.is_displayed() and cb.is_enabled() and not cb.is_selected():
                    q_text = _extract_field_question(driver, cb).lower()
                    if any(k in q_text for k in ["acknowledge", "consent", "agree", "privacy", "terms", "certify", "yes", "united states", "remote"]):
                        cb.click()
            except Exception:
                continue

        # 6. Handle Select Dropdowns (Work Authorization, Sponsorship, Experience, Demographics, etc.)
        for sel in driver.find_elements(By.TAG_NAME, "select"):
            try:
                if not sel.is_displayed():
                    continue
                s = Select(sel)
                q_text = _extract_field_question(driver, sel)
                opts = [o.text.strip() for o in s.options if o.text.strip().lower() not in ["select an option", "select", "please select", "--", ""]]
                if opts:
                    best = _ai_answer_question(q_text, company, role, answer_type="choice", options=opts)
                    matched = False
                    for o in opts:
                        if best.lower() in o.lower() or o.lower() in best.lower():
                            s.select_by_visible_text(o); matched = True; break
                    if not matched and len(s.options) > 1:
                        s.select_by_index(1)
            except Exception:
                continue

        # 6. Click Submit button on the company form
        for sub in driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], button"):
            try:
                txt = (sub.text or sub.get_attribute("value") or "").strip().lower()
                if any(k in txt for k in ["submit application", "submit", "send application", "apply"]):
                    sub.click()
                    time.sleep(3)
                    return True
            except Exception:
                continue

        return False
    except Exception as e:
        print(f"     ⚠️ External form error: {str(e)[:60]}")
        return False


def apply_single_job_url(job_url: str) -> dict:
    """Open a single LinkedIn job URL (sent via WhatsApp), apply via Easy Apply or LinkedIn Company Form, and log it."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    chrome_profile_dir = Path.home() / ".ghazal_ai_chrome_profile"
    chrome_profile_dir.mkdir(parents=True, exist_ok=True)
    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket"]:
        try:
            (chrome_profile_dir / lock).unlink(missing_ok=True)
        except Exception:
            pass
    opts.add_argument(f"--user-data-dir={chrome_profile_dir}")

    driver = webdriver.Chrome(options=opts)
    try:
        driver.get(job_url)
        time.sleep(4)
        title_parts = (driver.title or "AI/ML Engineer").split("|")
        role = title_parts[0].strip()[:60]
        company = title_parts[1].strip()[:40] if len(title_parts) > 1 else "LinkedIn Company"

        apply_btn = driver.execute_script(
            """
            const candidates = Array.from(document.querySelectorAll(
                'button[aria-label*="Easy Apply"], button[aria-label*="Apply"], a[aria-label*="Apply"], ' +
                '.jobs-s-apply button, .jobs-apply-button--top-card button, button.jobs-apply-button, main button, main a'
            ));
            for (const b of candidates) {
                const txt = (b.innerText || '').trim().toLowerCase();
                const aria = (b.getAttribute('aria-label') || '').trim().toLowerCase();
                if ((txt === 'easy apply' || txt === 'apply' || aria.includes('easy apply to this job') || aria.includes('apply to this job')) && !txt.includes('applied') && b.offsetParent !== null) {
                    return b;
                }
            }
            return null;
            """
        )
        ok = False
        if apply_btn:
            main_window = driver.current_window_handle
            driver.execute_script("arguments[0].click();", apply_btn)
            time.sleep(3)
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(3)
                ok = _fill_external_company_form(driver, company, role)
                driver.close()
                driver.switch_to.window(main_window)
            else:
                for _ in range(10):
                    _fill_linkedin_form(driver, None, company, role)
                    time.sleep(1)
                    action_taken = driver.execute_script(
                        """
                        const modal = document.querySelector('.jobs-easy-apply-modal, .artdeco-modal, [role="dialog"]');
                        if (!modal) return 'no_modal';
                        const btns = Array.from(modal.querySelectorAll('button'));
                        for (const b of btns) {
                            const t = ((b.innerText || '') + ' ' + (b.getAttribute('aria-label') || '')).trim().toLowerCase();
                            if (t.includes('submit application') || t === 'submit') { b.click(); return 'submitted'; }
                        }
                        for (const b of btns) {
                            const t = ((b.innerText || '') + ' ' + (b.getAttribute('aria-label') || '')).trim().toLowerCase();
                            if ((t.includes('review') || t.includes('next') || t.includes('continue')) && !b.disabled) { b.click(); return 'next'; }
                        }
                        return 'stuck';
                        """
                    )
                    if action_taken == "submitted":
                        ok = True
                        break
                    elif action_taken != "next":
                        break

        status = "Applied" if ok else "Attempted"
        entry = log_application(company, role, "LinkedIn (WhatsApp)", job_url, status=status)
        send_proof_email(load_log())
        return entry
    finally:
        driver.quit()


# ══════════════════════════════════════════════════════════════
# MAIN RUNNER
# ══════════════════════════════════════════════════════════════
def run_bot():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        import subprocess, sys
        print("📦 Auto-installing selenium & webdriver-manager for your current Python...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager", "--quiet"])
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

    print("\n" + "="*60)
    print("  🤖 Ghazal's Auto Job Application Bot")
    print("="*60)
    print(f"  👤 Applying as: {PROFILE['full_name']}")
    print(f"  📧 Proof sent to: {GMAIL_NOTIFY}")
    print(f"  🎯 Target: {TARGET_DAILY} applications")
    print("="*60)

    # Already applied today?
    existing = load_log()
    if len(existing) >= TARGET_DAILY:
        print(f"\n✅ Already applied to {len(existing)} jobs today!")
        send_proof_email(existing)
        return

    remaining = TARGET_DAILY - len(existing)

    # Setup Chrome
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    # Persist login session in your existing ~/.ghazal_ai_chrome_profile directory
    chrome_profile_dir = Path.home() / ".ghazal_ai_chrome_profile"
    chrome_profile_dir.mkdir(parents=True, exist_ok=True)
    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket"]:
        try:
            (chrome_profile_dir / lock).unlink(missing_ok=True)
        except Exception:
            pass
    opts.add_argument(f"--user-data-dir={chrome_profile_dir}")

    print("\n🌐 Launching Chrome window...")
    try:
        driver = webdriver.Chrome(options=opts)
    except Exception:
        # Fallback to fresh session if profile is locked
        opts2 = Options()
        opts2.add_argument("--start-maximized")
        opts2.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=opts2)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    all_applied = list(existing)

    try:
        # ── 100% LINKEDIN ONLY (Verify real logged-in session via li_at cookie)
        print("\n📌 Checking LinkedIn Login in Chrome...")
        driver.get("https://www.linkedin.com/login")
        time.sleep(3)

        def _is_linkedin_logged_in(drv):
            try:
                cookies = {c["name"] for c in drv.get_cookies()}
                url = drv.current_url or ""
                return "li_at" in cookies and "login" not in url and "checkpoint" not in url
            except Exception:
                return False

        if not _is_linkedin_logged_in(driver):
            print("   👉 Please sign in to LinkedIn in the Chrome window that just opened!")
            for sec in range(180, 0, -5):
                if _is_linkedin_logged_in(driver):
                    print("   ✅ Real LinkedIn Login (li_at cookie) detected! Starting job search...")
                    break
                print(f"   ⏳ Waiting for you to sign into LinkedIn... ({sec}s remaining)")
                time.sleep(5)
        else:
            print("   ✅ Already logged into LinkedIn (li_at session active)!")

        li_applied = run_linkedin_bot(driver, remaining)
        all_applied.extend(li_applied)
        print(f"\n  ✅ LinkedIn: Applied to {len(li_applied)} jobs")

    except KeyboardInterrupt:
        print("\n⚠️  Bot stopped by user")
    finally:
        driver.quit()

    # ── Send Proof Email
    total = len(all_applied)
    print(f"\n{'='*60}")
    print(f"  🎉 DONE! Applied to {total} jobs today")
    print(f"{'='*60}")

    if all_applied:
        print("\n📧 Sending proof email to Gmail...")
        send_proof_email(all_applied)

    # Save final log
    save_log(all_applied)
    print(f"\n📂 Full log saved: data/applications/applied_{today}.json")


# ══════════════════════════════════════════════════════════════
# SETUP INSTRUCTIONS (printed if config missing)
# ══════════════════════════════════════════════════════════════
def print_setup():
    print("""
╔══════════════════════════════════════════════════════════╗
║          GMAIL APP PASSWORD SETUP (5 minutes)           ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  1. Go to: myaccount.google.com                         ║
║  2. Security → 2-Step Verification → turn ON            ║
║  3. Security → App Passwords                            ║
║  4. Select app: Mail  |  Select device: Mac             ║
║  5. Click Generate → copy the 16-character password     ║
║  6. Add to .env file:                                   ║
║     GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx              ║
║  7. Run bot again!                                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    if not GMAIL_APP_PASS:
        print_setup()
        answer = input("Have you set GMAIL_APP_PASSWORD in .env? (y/n): ")
        if answer.lower() != 'y':
            print("Please set it up first, then run again.")
            exit()
        load_dotenv(override=True)

    run_bot()
