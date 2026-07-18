import json
import os
import re
import sys
import time
from datetime import datetime

import requests

BASE = os.environ.get("TEST_BASE_URL", "https://responder-registry.preview.emergentagent.com").rstrip("/")
ADMIN_EMAIL = "admin@kfr.org"
ADMIN_PASSWORD = "Kfr@2026"
ML_RE = re.compile(r"[\u0D00-\u0D7F]")

session = requests.Session()
results = {"base": BASE, "steps": [], "created_candidate_ids": [], "tokens": {}}

def step(name, ok, details=None):
    entry = {"name": name, "ok": bool(ok), "details": details or {}}
    results["steps"].append(entry)
    print(("PASS" if ok else "FAIL") + f" - {name}: {details if details is not None else ''}")
    if not ok:
        raise AssertionError(f"{name} failed: {details}")

def req(method, path, **kwargs):
    url = BASE + path
    resp = session.request(method, url, timeout=30, **kwargs)
    return resp

def login():
    resp = req("POST", "/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    step("admin login", resp.status_code == 200, {"status": resp.status_code, "body": resp.text[:200]})
    token = resp.json()["token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    return token

def get_event_id():
    resp = req("GET", "/api/events")
    step("list events", resp.status_code == 200 and len(resp.json()) > 0, {"status": resp.status_code, "count": len(resp.json()) if resp.ok else None})
    return resp.json()[0]["id"]

def register_candidate(event_id, label):
    unique = f"qa_{label}_{int(time.time()*1000)}@example.com"
    payload = {
        "name": f"QA {label} Candidate",
        "phone": "9999999999",
        "email": unique,
        "dob": "1990-01-01",
        "district": "Ernakulam",
        "category": "Volunteer",
        "organisation": "Aster Medcity",
        "event_id": event_id,
    }
    # candidate registration is public; remove auth header just for this call to mimic real flow
    auth = session.headers.pop("Authorization", None)
    try:
        resp = req("POST", "/api/candidates/register", json=payload)
    finally:
        if auth:
            session.headers["Authorization"] = auth
    step(f"register candidate {label}", resp.status_code == 200 and resp.json().get("ok"), {"status": resp.status_code, "body": resp.text[:200]})
    cid = resp.json()["candidate_id"]
    results["created_candidate_ids"].append(cid)
    return cid, unique

def generate_token(cid):
    resp = req("POST", "/api/admin/generate-test", json={"candidate_ids": [cid]})
    # email may fail in preview; endpoint should still set token and return total=1
    step("generate test token", resp.status_code == 200 and resp.json().get("total") == 1, {"status": resp.status_code, "body": resp.text[:200]})
    resp2 = req("GET", "/api/candidates")
    step("list candidates for token", resp2.status_code == 200, {"status": resp2.status_code})
    candidate = next((c for c in resp2.json() if c.get("id") == cid), None)
    token = candidate and candidate.get("test_token")
    step("candidate has pending token", bool(token) and candidate.get("test_status") == "pending", {"token_present": bool(token), "status": candidate.get("test_status") if candidate else None})
    return token

def assert_questions_seeded():
    resp = req("GET", "/api/questions")
    questions = resp.json() if resp.ok else []
    en = [q for q in questions if q.get("language") == "en"]
    ml = [q for q in questions if q.get("language") == "ml"]
    missing_lang = [q.get("id") for q in questions if not q.get("language")]
    step("questions have required language counts", resp.status_code == 200 and len(en) >= 15 and len(ml) >= 12 and not missing_lang,
         {"status": resp.status_code, "en": len(en), "ml": len(ml), "missing_lang_count": len(missing_lang)})
    return {q["id"]: q for q in questions}

def verify_language_required(token):
    resp = req("GET", f"/api/test/{token}")
    data = resp.json() if resp.ok else {}
    leaked = "questions" in data or "active_question_ids" in data
    step("test without lang requires language and leaks no questions", resp.status_code == 200 and data.get("status") == "language_required" and data.get("candidate_name") and not leaked,
         {"status": resp.status_code, "keys": list(data.keys())})

def get_test_questions(token, lang):
    resp = req("GET", f"/api/test/{token}", params={"lang": lang})
    data = resp.json() if resp.ok else {}
    qs = data.get("questions") or []
    if lang == "en":
        lang_ok = all(not ML_RE.search(q.get("text", "")) and all(not ML_RE.search(o.get("text", "")) for o in q.get("options", [])) for q in qs)
    else:
        lang_ok = all(ML_RE.search(q.get("text", "")) or any(ML_RE.search(o.get("text", "")) for o in q.get("options", [])) for q in qs)
    step(f"get active {lang} test returns exactly 10 isolated-language questions",
         resp.status_code == 200 and data.get("status") == "active" and data.get("language") == lang and len(qs) == 10 and lang_ok,
         {"status": resp.status_code, "api_language": data.get("language"), "count": len(qs), "lang_ok": lang_ok, "sample": qs[0].get("text") if qs else None})
    return data

def submit_answers(token, questions, all_questions, mode):
    answers = {}
    for q in questions:
        correct = all_questions[q["id"]]["correct_key"]
        if mode == "correct":
            answers[q["id"]] = correct
        else:
            keys = [o["key"] for o in q["options"]]
            answers[q["id"]] = next(k for k in keys if k != correct)
    resp = req("POST", f"/api/test/{token}/submit", json={"answers": answers})
    data = resp.json() if resp.ok else {}
    expected_pass = mode == "correct"
    expected_score = 10 if mode == "correct" else 0
    step(f"submit {mode} answers scores and sets {'passed' if expected_pass else 'failed'}",
         resp.status_code == 200 and data.get("score") == expected_score and data.get("passed") is expected_pass and data.get("total") == 10 and (bool(data.get("certificate_id")) == expected_pass),
         {"status": resp.status_code, "score": data.get("score"), "passed": data.get("passed"), "cert_present": bool(data.get("certificate_id"))})
    return data

def verify_candidate_status(cid, status, score):
    resp = req("GET", "/api/candidates")
    candidate = next((c for c in resp.json() if c.get("id") == cid), None) if resp.ok else None
    step(f"candidate persisted as {status}", bool(candidate) and candidate.get("test_status") == status and candidate.get("test_score") == score,
         {"status": candidate.get("test_status") if candidate else None, "score": candidate.get("test_score") if candidate else None, "language": candidate.get("test_language") if candidate else None})
    return candidate

def verify_pdf(token):
    # remove bearer header so this mimics public certificate download
    auth = session.headers.pop("Authorization", None)
    try:
        resp = req("GET", f"/api/certificate/{token}/pdf")
    finally:
        if auth:
            session.headers["Authorization"] = auth
    content = resp.content or b""
    step("certificate PDF renders for passed candidate", resp.status_code == 200 and resp.headers.get("content-type", "").startswith("application/pdf") and content.startswith(b"%PDF") and len(content) > 1000,
         {"status": resp.status_code, "content_type": resp.headers.get("content-type"), "starts_pdf": content[:4].decode(errors="ignore"), "bytes": len(content)})

def completed_token_no_language_prompt(token):
    resp = req("GET", f"/api/test/{token}")
    data = resp.json() if resp.ok else {}
    step("completed test returns completed state without language prompt", resp.status_code == 200 and data.get("status") == "completed" and "questions" not in data,
         {"status": resp.status_code, "body_status": data.get("status"), "keys": list(data.keys())})

def main():
    login()
    all_questions = assert_questions_seeded()
    event_id = get_event_id()

    # English pass flow
    en_cid, _ = register_candidate(event_id, "en_pass")
    en_token = generate_token(en_cid)
    results["tokens"]["en_pass"] = en_token
    verify_language_required(en_token)
    en_test = get_test_questions(en_token, "en")
    en_result = submit_answers(en_token, en_test["questions"], all_questions, "correct")
    verify_candidate_status(en_cid, "passed", 10)
    completed_token_no_language_prompt(en_token)

    # Malayalam pass flow + PDF
    ml_cid, _ = register_candidate(event_id, "ml_pass")
    ml_token = generate_token(ml_cid)
    results["tokens"]["ml_pass"] = ml_token
    verify_language_required(ml_token)
    ml_test = get_test_questions(ml_token, "ml")
    ml_result = submit_answers(ml_token, ml_test["questions"], all_questions, "correct")
    verify_candidate_status(ml_cid, "passed", 10)
    verify_pdf(ml_token)

    # Malayalam fail flow verifies same pass threshold/fail persistence
    fail_cid, _ = register_candidate(event_id, "ml_fail")
    fail_token = generate_token(fail_cid)
    results["tokens"]["ml_fail"] = fail_token
    verify_language_required(fail_token)
    fail_test = get_test_questions(fail_token, "ml")
    fail_result = submit_answers(fail_token, fail_test["questions"], all_questions, "wrong")
    verify_candidate_status(fail_cid, "failed", 0)

    results["ok"] = True

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        results["ok"] = False
        results["error"] = str(exc)
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit_code = 1
    finally:
        out = "/app/test_reports/malayalam_assessment_backend_results.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Wrote {out}")
    if not results.get("ok"):
        sys.exit(1)
