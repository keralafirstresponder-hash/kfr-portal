import json
import os
import re
import uuid
from pathlib import Path

import fitz
import requests
from PIL import Image


BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://responder-registry.preview.emergentagent.com").rstrip("/")
API = BASE_URL + "/api"
OUT_DIR = Path("/app/test_reports")


def assert_ok(resp, context):
    if not resp.ok:
        raise RuntimeError(f"{context} failed: {resp.status_code} {resp.text[:500]}")


def pixel_counts(im, box):
    crop = im.crop(box).convert("RGB")
    total = crop.size[0] * crop.size[1]
    blue = 0
    strong_blue = 0
    dark = 0
    for r, g, b in crop.getdata():
        # Detect saturated blue/cyan circular icon pixels from the old template.
        if b > r + 25 and b > g + 5 and b > 80:
            blue += 1
        if b > r + 45 and b > g + 15 and b > 110:
            strong_blue += 1
        if r < 100 and g < 100 and b < 130:
            dark += 1
    return {"blue": blue, "strong_blue": strong_blue, "dark": dark, "total": total}


def page_text(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        return "\n".join(page.get_text("text") for page in doc)
    finally:
        doc.close()


def render_pdf(pdf_bytes, output_png):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
        pix.save(str(output_png))
    finally:
        doc.close()
    return Image.open(output_png).convert("RGB")


def main():
    s = requests.Session()
    evidence = {"base_url": BASE_URL, "api": API}

    landing = s.get(BASE_URL + "/", timeout=30)
    assert_ok(landing, "landing page")
    html = landing.text
    mission_idx = html.lower().find("mission progress")
    mission_slice = html[max(0, mission_idx - 1000): mission_idx + 3000] if mission_idx != -1 else html[:5000]
    percent_patterns = re.findall(r"\b\d+(?:\.\d+)?%", mission_slice)
    evidence["landing"] = {
        "status": landing.status_code,
        "has_mission_progress_text": "Mission Progress" in html,
        "has_certified_text": "certified" in html,
        "has_goal_text": "Goal · 100,000" in html or "Goal &middot; 100,000" in html,
        "percent_patterns_near_mission_progress": percent_patterns,
        "contains_0_00_percent": "0.00%" in mission_slice,
    }

    login = s.post(API + "/auth/login", json={"email": "admin@kfr.org", "password": "Kfr@2026"}, timeout=30)
    assert_ok(login, "admin login")
    headers = {"Authorization": "Bearer " + login.json()["token"]}
    evidence["admin_login"] = {"status": login.status_code, "email": login.json()["admin"]["email"]}

    events = s.get(API + "/events", timeout=30)
    assert_ok(events, "events")
    event = events.json()[0]
    unique = uuid.uuid4().hex[:8]
    payload = {
        "name": f"QA Certificate UI Fix {unique}",
        "phone": "9876501234",
        "email": f"qa_cert_fix_{unique}@example.com",
        "dob": "1990-01-01",
        "district": "Ernakulam",
        "category": "Student",
        "organisation": "Aster Medcity",
        "event_id": event["id"],
    }
    reg = s.post(API + "/candidates/register", json=payload, timeout=30)
    assert_ok(reg, "candidate registration")
    candidate_id = reg.json()["candidate_id"]
    gen = s.post(API + "/admin/generate-test", json={"candidate_ids": [candidate_id]}, headers=headers, timeout=60)
    assert_ok(gen, "generate test")
    candidates = s.get(API + "/candidates", headers=headers, timeout=30)
    assert_ok(candidates, "list candidates")
    cand = next(c for c in candidates.json() if c["id"] == candidate_id)
    token = cand["test_token"]
    test = s.get(API + f"/test/{token}?lang=en", timeout=30)
    assert_ok(test, "get English test")
    questions = test.json()["questions"]
    answer_key = {q["id"]: q["options"][0]["key"] for q in questions}
    # Fetch admin questions to answer all selected questions correctly.
    admin_q = s.get(API + "/questions", headers=headers, timeout=30)
    assert_ok(admin_q, "admin questions")
    correct_by_id = {q["id"]: q["correct_key"] for q in admin_q.json()}
    answers = {qid: correct_by_id[qid] for qid in answer_key}
    submit = s.post(API + f"/test/{token}/submit", json={"answers": answers}, timeout=30)
    assert_ok(submit, "submit passing test")
    submit_json = submit.json()
    if not submit_json.get("passed"):
        raise RuntimeError(f"Expected passing test, got {submit_json}")

    pdf = s.get(API + f"/certificate/{token}/pdf", timeout=30)
    assert_ok(pdf, "certificate PDF")
    pdf_path = OUT_DIR / f"certificate_bug_verification_{unique}.pdf"
    png_path = OUT_DIR / f"certificate_bug_verification_{unique}.png"
    pdf_path.write_bytes(pdf.content)
    im = render_pdf(pdf.content, png_path)
    text = page_text(pdf.content)

    # Scale template-coordinate boxes to the rendered PDF image size.
    sx = im.size[0] / 1222
    sy = im.size[1] / 864
    def scale_box(box):
        x1, y1, x2, y2 = box
        return (round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy))

    evidence["certificate"] = {
        "candidate_id": candidate_id,
        "token": token,
        "certificate_id": submit_json.get("certificate_id"),
        "pdf_status": pdf.status_code,
        "rendered_size": im.size,
        "pdf_text": text,
        "text_contains_ceo": "CEO" in text,
        "text_contains_aster_medcity": "Aster Medcity" in text,
        "text_contains_chairman": "Chairman" in text or "Managing Director" in text,
        "text_contains_program_director": "Program Director" in text or "Kerala First Responder" in text,
        "regions": {
            "date_icon": pixel_counts(im, scale_box((300, 580, 355, 638))),
            "cert_id_icon": pixel_counts(im, scale_box((520, 580, 575, 638))),
            "training_centre_icon": pixel_counts(im, scale_box((750, 580, 815, 638))),
            "middle_signature": pixel_counts(im, scale_box((500, 655, 770, 810))),
            "left_signature": pixel_counts(im, scale_box((280, 655, 505, 810))),
            "right_signature": pixel_counts(im, scale_box((770, 655, 1045, 810))),
        },
        "pdf_path": str(pdf_path),
        "png_path": str(png_path),
    }

    # Intentionally do not delete candidate: it is useful evidence and contributes to mission count.
    out_path = OUT_DIR / "certificate_landing_bug_results.json"
    out_path.write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()