import json
import os
import uuid
from pathlib import Path

import fitz
import requests
from PIL import Image, ImageChops, ImageDraw, ImageStat


BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://responder-registry.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"
OUT = Path("/app/test_reports/bug_assets/iter7")
OUT.mkdir(parents=True, exist_ok=True)


def step(result, name, ok, details=None):
    payload = {"name": name, "ok": bool(ok), "details": details or {}}
    result["steps"].append(payload)
    print(f"{name}: {'OK' if ok else 'FAIL'} {details or {}}")
    return bool(ok)


def render_pdf(pdf_bytes, out_path):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    pix.save(str(out_path))
    return Image.open(out_path).convert("RGB")


def candidate_payload(event_id, label):
    unique = uuid.uuid4().hex[:10]
    return {
        "name": f"QA Iter7 {label} {unique}",
        "phone": "9876501234",
        "email": f"qa_iter7_{label.lower()}_{unique}@example.com",
        "dob": "1994-07-17",
        "district": "Ernakulam",
        "category": "Volunteer",
        "organisation": "Aster Medcity",
        "event_id": event_id,
    }


result = {"api": API, "steps": [], "created_candidates": {}}
s = requests.Session()

# Admin auth and metadata used by all flows.
r = s.post(f"{API}/auth/login", json={"email": "admin@kfr.org", "password": "Kfr@2026"}, timeout=30)
step(result, "admin_login_api", r.status_code == 200 and "token" in r.text, {"status": r.status_code, "body": r.text[:200]})
r.raise_for_status()
headers = {"Authorization": f"Bearer {r.json()['token']}"}

r = s.get(f"{API}/events", timeout=30)
step(result, "public_events_available", r.status_code == 200 and len(r.json()) > 0, {"status": r.status_code, "count": len(r.json()) if r.ok else None})
r.raise_for_status()
event = r.json()[0]

# Backend DELETE /api/candidates/{id}: auth required, unknown id 404, success removes row.
r = s.delete(f"{API}/candidates/definitely-not-real")
step(result, "delete_requires_admin_auth", r.status_code == 401, {"status": r.status_code, "body": r.text[:200]})

r = s.delete(f"{API}/candidates/definitely-not-real", headers=headers, timeout=30)
step(result, "delete_unknown_candidate_404", r.status_code == 404, {"status": r.status_code, "body": r.text[:200]})

delete_payload = candidate_payload(event["id"], "BackendDelete")
r = s.post(f"{API}/candidates/register", json=delete_payload, timeout=30)
step(result, "register_candidate_for_backend_delete", r.status_code == 200 and r.json().get("candidate_id"), {"status": r.status_code, "body": r.text[:200], "email": delete_payload["email"]})
r.raise_for_status()
delete_id = r.json()["candidate_id"]
result["created_candidates"]["backend_delete"] = {"id": delete_id, **delete_payload}

r = s.get(f"{API}/candidates", headers=headers, timeout=30)
r.raise_for_status()
step(result, "backend_delete_candidate_visible_before_delete", any(c["id"] == delete_id for c in r.json()), {"candidate_id": delete_id})

r = s.delete(f"{API}/candidates/{delete_id}", headers=headers, timeout=30)
step(result, "delete_candidate_success_200", r.status_code == 200 and r.json() == {"ok": True, "deleted": delete_id}, {"status": r.status_code, "body": r.text[:200]})

r = s.get(f"{API}/candidates", headers=headers, timeout=30)
r.raise_for_status()
step(result, "deleted_candidate_absent_from_get_candidates", all(c["id"] != delete_id for c in r.json()), {"candidate_id": delete_id, "remaining_count": len(r.json())})

# Leave one real candidate for the browser/UI delete-button verification.
ui_payload = candidate_payload(event["id"], "UIDelete")
r = s.post(f"{API}/candidates/register", json=ui_payload, timeout=30)
step(result, "register_candidate_for_ui_delete", r.status_code == 200 and r.json().get("candidate_id"), {"status": r.status_code, "body": r.text[:200], "email": ui_payload["email"]})
r.raise_for_status()
ui_id = r.json()["candidate_id"]
result["created_candidates"]["ui_delete"] = {"id": ui_id, **ui_payload}

# Lightweight no-regression: generate-test, test-taking, certificate PDF render/no-white-patches.
r = s.get(f"{API}/questions", headers=headers, timeout=30)
step(result, "questions_available_for_test", r.status_code == 200 and len(r.json()) >= 10, {"status": r.status_code, "count": len(r.json()) if r.ok else None})
r.raise_for_status()
correct_map = {q["id"]: q["correct_key"] for q in r.json()}

reg_payload = candidate_payload(event["id"], "RegressionCert")
r = s.post(f"{API}/candidates/register", json=reg_payload, timeout=30)
step(result, "register_candidate_for_regression_flow", r.status_code == 200 and r.json().get("candidate_id"), {"status": r.status_code, "body": r.text[:200], "email": reg_payload["email"]})
r.raise_for_status()
reg_id = r.json()["candidate_id"]
result["created_candidates"]["regression_certificate"] = {"id": reg_id, **reg_payload}

r = s.post(f"{API}/admin/generate-test", json={"candidate_ids": [reg_id]}, headers=headers, timeout=60)
gen_ok = r.status_code == 200 and r.json().get("total") == 1
step(result, "generate_test_endpoint_accepts_candidate", gen_ok, {"status": r.status_code, "body": r.text[:300]})
r.raise_for_status()
result["generate_test_response"] = r.json()

r = s.get(f"{API}/candidates", headers=headers, timeout=30)
r.raise_for_status()
reg_candidate = next(c for c in r.json() if c["id"] == reg_id)
test_token = reg_candidate.get("test_token")
step(result, "generate_test_sets_pending_token", bool(test_token) and reg_candidate.get("test_status") == "pending", {"test_status": reg_candidate.get("test_status"), "token_len": len(test_token or "")})

r = s.get(f"{API}/test/{test_token}", timeout=30)
step(result, "test_link_opens_active_test", r.status_code == 200 and r.json().get("status") == "active", {"status": r.status_code, "body": r.text[:200]})
r.raise_for_status()
questions = r.json()["questions"]
answers = {q["id"]: correct_map[q["id"]] for q in questions}

r = s.post(f"{API}/test/{test_token}/submit", json={"answers": answers}, timeout=30)
step(result, "test_submit_passes_with_correct_answers", r.status_code == 200 and r.json().get("passed") is True, {"status": r.status_code, "body": r.text[:300]})
r.raise_for_status()
cert_id = r.json().get("certificate_id")

r = s.get(f"{API}/certificate/{test_token}/pdf", timeout=30)
pdf_path = OUT / f"certificate_{reg_id}.pdf"
pdf_path.write_bytes(r.content)
step(result, "certificate_pdf_downloads", r.status_code == 200 and r.content.startswith(b"%PDF"), {"status": r.status_code, "content_type": r.headers.get("content-type"), "bytes": len(r.content), "cert_id": cert_id})
r.raise_for_status()

generated_png = OUT / f"certificate_{reg_id}.png"
generated_img = render_pdf(r.content, generated_png)
template_path = Path("/app/backend/assets/cert_template_clean.jpg")
clean_img = Image.open(template_path).convert("RGB")
baseline_pdf = OUT / "baseline_clean_template.pdf"
clean_img.save(baseline_pdf, "PDF", resolution=150.0)
baseline_png = OUT / "baseline_clean_template.png"
baseline_img = render_pdf(baseline_pdf.read_bytes(), baseline_png)

sx = generated_img.width / 1222
sy = generated_img.height / 864
mask = Image.new("L", generated_img.size, 255)
draw = ImageDraw.Draw(mask)
for box in [(275, 388, 910, 470), (332, 636, 500, 664), (552, 636, 765, 664), (784, 636, 1125, 664)]:
    scaled = tuple(int(v * sx if i % 2 == 0 else v * sy) for i, v in enumerate(box))
    draw.rectangle(scaled, fill=0)
diff = ImageChops.difference(generated_img, baseline_img)
stat = ImageStat.Stat(diff, mask)
mean_diff = sum(stat.mean) / 3
step(result, "certificate_background_unchanged_outside_dynamic_text", mean_diff < 2.5, {"mean_rgb_abs_diff": mean_diff, "png": str(generated_png)})

state_path = OUT / "iter7_api_state.json"
state_path.write_text(json.dumps(result, indent=2))
Path("/app/test_reports/iter7_api_backend_latest.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))

if not all(s["ok"] for s in result["steps"]):
    raise SystemExit(1)