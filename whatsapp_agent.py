"""
WhatsApp Personal AI Agent — Ghazal Sultan
Control your AI Agents & Auto-Apply Job Bot directly from WhatsApp!
Supports two modes:
  1. Direct WhatsApp Web Bot (Scan QR code — 100% Free, no Twilio needed)
  2. Outbound WhatsApp Proof Report Sender (sends daily job summary to +1 669-213-3034)
"""

import os
import time
import json
import datetime
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MY_WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+16692133034")


def format_whatsapp_proof_summary() -> str:
    """Create a clean WhatsApp message summarizing today's job applications."""
    today = datetime.date.today().isoformat()
    log_file = Path("data/applications") / f"applied_{today}.json"
    if not log_file.exists():
        # Check latest applied file
        files = sorted(Path("data/applications").glob("applied_*.json"), reverse=True)
        log_file = files[0] if files else log_file

    entries = json.loads(log_file.read_text()) if log_file.exists() else []
    lines = [
        f"🤖 *Ghazal's AI Agent — Job Application Report*",
        f"📅 Date: {today}",
        f"✅ Total Applied: {len(entries)} jobs",
        "",
        "*Recent Applications:*",
    ]
    for e in entries[-10:]:
        lines.append(f"• *{e.get('company')}* — {e.get('role')} ({e.get('platform')})")
    return "\n".join(lines)


def send_whatsapp_via_twilio(message_text: str) -> bool:
    """Send WhatsApp message via Twilio API if TWILIO_ACCOUNT_SID is configured in .env."""
    sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    from_whatsapp = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
    to_whatsapp = f"whatsapp:{MY_WHATSAPP_NUMBER}"

    if not sid or not token:
        return False

    try:
        import requests
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
        resp = requests.post(
            url,
            data={"From": from_whatsapp, "To": to_whatsapp, "Body": message_text},
            auth=(sid, token),
            timeout=10,
        )
        return resp.status_code in [200, 201]
    except Exception as e:
        print(f"Twilio WhatsApp error: {e}")
        return False


def run_whatsapp_web_agent():
    """
    Launch WhatsApp Web in Chrome using your persistent profile (~/.ghazal_ai_chrome_profile).
    Listens to your 'Message Yourself' chat for commands:
      - 'status' or 'report' -> replies with your job application proof report
      - 'apply'              -> launches job_bot.py (50 jobs/day)
      - 'tasks'              -> lists your daily tasks
      - Any question         -> answers with GPT-4o-mini!
    """
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.chrome.options import Options
    from app import handle_whatsapp_command

    print("\n" + "=" * 60)
    print("  📱 Ghazal's WhatsApp AI Agent — Starting")
    print("=" * 60)
    print("  1. Chrome will open https://web.whatsapp.com")
    print("  2. Scan the QR code once with your WhatsApp phone app")
    print("     (Settings -> Linked Devices -> Link a Device)")
    print("  3. Open your 'Message Yourself' (or saved messages) chat")
    print("  4. Type commands like:  status | apply | tasks | draft email...")
    print("=" * 60 + "\n")

    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    chrome_profile = Path.home() / ".ghazal_wa_bot" / "DefaultProfile"
    chrome_profile.mkdir(parents=True, exist_ok=True)
    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket"]:
        (chrome_profile / lock).unlink(missing_ok=True)
        (chrome_profile.parent / lock).unlink(missing_ok=True)
    opts.add_argument(f"--user-data-dir={chrome_profile}")

    driver = webdriver.Chrome(options=opts)
    driver.get("https://web.whatsapp.com")

    print("⏳ Waiting 7 seconds for WhatsApp Web to load...")
    time.sleep(7)
    last_msg_count = 0
    chat_opened = False

    def _strip_non_bmp(text: str) -> str:
        """Keep BMP characters so ChromeDriver send_keys never throws an emoji error."""
        return "".join(c for c in text if ord(c) <= 0xFFFF)

    try:
        while True:
            time.sleep(2.5)
            try:
                # 1. Open 'Ghazal' chat using real mouse ActionChains click!
                boxes = driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")
                if not boxes:
                    try:
                        ghazal_span = driver.find_element(By.CSS_SELECTOR, "span[title='Ghazal']")
                        ActionChains(driver).move_to_element(ghazal_span).click().perform()
                        if not chat_opened:
                            print("✅ Opened your 'Ghazal' chat in WhatsApp Web!")
                            chat_opened = True
                        time.sleep(2)
                        boxes = driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")
                    except Exception:
                        continue

                if not boxes:
                    continue

                # 2. Read all message bubbles in the open 'Ghazal' chat
                msg_els = driver.find_elements(By.CSS_SELECTOR, "span.selectable-text, div.copyable-text")
                texts = [(el.text or "").strip() for el in msg_els if (el.text or "").strip()]
                if not texts:
                    continue

                latest = texts[-1]
                # Skip if the latest message on screen is already our own bot reply!
                if latest.startswith("[AI Agent]") or "Ghazal's AI Agent" in latest or "Auto-Apply Bot Launched" in latest or "Applied via WhatsApp" in latest or "Pending Tasks" in latest:
                    last_msg_count = len(texts)
                    continue

                # Trigger if a new message arrived OR if the last message in chat is an unanswered command!
                low = latest.lower()
                is_job_link = (
                    low.startswith("apply https://www.linkedin.com")
                    or low.startswith("https://www.linkedin.com/jobs")
                )
                if low in ["status", "report", "apply", "linkedin", "tasks", "proof", "jobs"] or is_job_link or latest.startswith("!"):
                    query = latest[1:].strip() if latest.startswith("!") else latest
                    print(f"📩 WhatsApp Command Received: {query}")
                    reply = handle_whatsapp_command(query)
                    clean_reply = _strip_non_bmp(f"[AI Agent] {reply}")

                    box = boxes[-1]
                    ActionChains(driver).move_to_element(box).click().perform()
                    time.sleep(0.3)
                    lines = clean_reply.split("\n")
                    for idx_line, line in enumerate(lines):
                        if line:
                            box.send_keys(line)
                        if idx_line < len(lines) - 1:
                            ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
                    time.sleep(0.3)
                    box.send_keys(Keys.ENTER)
                    print("✅ Replied on WhatsApp!")
                    time.sleep(3)
            except Exception as e:
                print(f"⚠️ Loop note: {e}")
                continue
    except KeyboardInterrupt:
        print("\n👋 WhatsApp Agent stopped.")
    finally:
        driver.quit()


if __name__ == "__main__":
    run_whatsapp_web_agent()
