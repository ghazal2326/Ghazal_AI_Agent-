"""
Quick test — verify all API endpoints respond correctly.
Run: python3 test_agents.py
"""
import json, sys, time
try:
    import requests
except ImportError:
    print("Run: pip3 install requests"); sys.exit(1)

BASE = "http://localhost:8765"
PASS = "✅"; FAIL = "❌"

def test(label, method, path, body=None):
    try:
        if method == "GET":
            r = requests.get(BASE + path, timeout=5)
        else:
            r = requests.post(BASE + path, json=body, timeout=10)
        ok = r.status_code == 200
        data = r.json()
        print(f"  {PASS if ok else FAIL}  {label:40s} [{r.status_code}]")
        return ok
    except Exception as e:
        print(f"  {FAIL}  {label:40s} [ERROR: {e}]")
        return False

print("\n🤖 Personal AI Agent System — Endpoint Tests\n" + "="*60)

results = [
    test("Health Check",              "GET",  "/api/status"),
    test("Email Inbox (mock)",         "GET",  "/api/agents/email/inbox"),
    test("Email Draft",                "POST", "/api/agents/email/draft",
         {"context": "Thank Sarah at Google for the interview", "type": "thank you"}),
    test("Email Reply",                "POST", "/api/agents/email/reply",
         {"original_email": "Hi, we'd like to schedule an interview.", "instructions": "Accept enthusiastically"}),
    test("Job List",                   "GET",  "/api/agents/jobs/applications"),
    test("Job Stats",                  "GET",  "/api/agents/jobs/stats"),
    test("Cover Letter",               "POST", "/api/agents/jobs/cover-letter",
         {"company": "DeepMind", "role": "Research Engineer", "job_description": "ML research role"}),
    test("Interview Prep",             "POST", "/api/agents/jobs/interview-prep",
         {"company": "OpenAI", "role": "Research Engineer", "focus": "ML"}),
    test("Recruiter Respond",          "POST", "/api/agents/recruiter/respond",
         {"message": "Hi, I have an ML role at Google.", "response_type": "interested"}),
    test("Recruiter Evaluate",         "POST", "/api/agents/recruiter/evaluate",
         {"message": "Exciting role at startup, 2 years experience needed"}),
    test("Salary Negotiation",         "POST", "/api/agents/recruiter/salary-negotiation",
         {"role": "ML Engineer", "offered_salary": "$180k", "target_salary": "$210k"}),
    test("LinkedIn Connect",           "POST", "/api/agents/linkedin/connect",
         {"name": "John", "role": "Manager", "company": "Google", "reason": "networking"}),
    test("LinkedIn Message",           "POST", "/api/agents/linkedin/message",
         {"recipient": "Sarah", "purpose": "Inquire about job opening"}),
    test("LinkedIn Post",              "POST", "/api/agents/linkedin/post",
         {"topic": "Transformer architectures in 2026", "tone": "professional"}),
    test("Follow-up List",             "GET",  "/api/agents/followups"),
    test("Follow-up Draft",            "POST", "/api/agents/followups/draft",
         {"contact": "Sarah", "context": "Interview follow-up", "days_since": 7, "type": "email"}),
    test("Task List",                  "GET",  "/api/agents/tasks"),
    test("Plan Day",                   "POST", "/api/agents/tasks/plan-day",
         {"goals": "job search and LinkedIn"}),
    test("Chat",                       "POST", "/api/chat",
         {"message": "Help me write a follow-up email"}),
]

passed = sum(results)
total = len(results)
print(f"\n{'='*60}")
print(f"Results: {passed}/{total} tests passed {'🎉' if passed==total else '⚠️'}")
if passed < total:
    print("\nMake sure the server is running: bash start.sh")
print()
