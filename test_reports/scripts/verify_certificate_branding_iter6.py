import json
import os
import uuid
from pathlib import Path

import fitz
import numpy as np
import requests
from PIL import Image, ImageChops, ImageDraw, ImageStat


BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://responder-registry.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"
OUT = Path("/app/test_reports/bug_assets/iter6_certificate_branding")
OUT.mkdir(parents=True, exist_ok=True)


def step(result, name, ok, details=None):
    payload = {"name": name, "ok": bool(ok), "details": details or {}}
    result["steps"].append(payload)
    print(f"{name}: {'OK' if ok else 'FAIL'} {details or {}}")
    return bool(ok)


def render_pdf_bytes_to_png(pdf_bytes, out_path):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    pix.save(str(out_path))
    return Image.open(out_path).convert("RGB")


def red_pixel_ratio(img):
    arr = np.array(img.convert("RGB"))
    red_mask = (arr[:, :, 0] > 150) & (arr[:, :, 1] < 95) & (arr[:, :, 2] < 95)
    return float(red_mask.mean())


def alpha_border_ratio(img):
    rgba = img.convert("RGBA")
    arr = np.array(rgba)
    alpha = arr[:, :, 3]
    border = np.concatenate([alpha[0, :], alpha[-1, :], alpha[:, 0], alpha[:, -1]])
    return float((border < 10).mean())


result = {"api": API, "steps": [], "assets": {}}
session = requests.Session()

# Backend flow: create a real passed candidate and download the real certificate PDF.
r = session.post(f"{API}/auth/login", json={"email": "admin@kfr.org", "password": "Kfr@2026"}, timeout=30)
step(result, "admin_login_api", r.status_code == 200, {"status": r.status_code, "body": r.text[:200]})
r.raise_for_status()
headers = {"Authorization": f"Bearer {r.json()['token']}"}

r = session.get(f"{API}/events", timeout=30)
step(result, "list_events_api", r.status_code == 200 and len(r.json()) > 0, {"status": r.status_code, "count": len(r.json()) if r.ok else None})
r.raise_for_status()
event = r.json()[0]

r = session.get(f"{API}/questions", headers=headers, timeout=30)
step(result, "list_questions_api", r.status_code == 200 and len(r.json()) >= 10, {"status": r.status_code, "count": len(r.json()) if r.ok else None})
r.raise_for_status()
correct_map = {q["id"]: q["correct_key"] for q in r.json()}

unique = uuid.uuid4().hex[:8]
candidate_name = f"QA Certificate No Boxes {unique}"
candidate_payload = {
    "name": candidate_name,
    "phone": "9876501234",
    "email": f"qa_cert_iter6_{unique}@example.com",
    "dob": "1994-07-17",
    "district": "Ernakulam",
    "category": "Volunteer",
    "organisation": "Aster Medcity",
    "event_id": event["id"],
}
r = session.post(f"{API}/candidates/register", json=candidate_payload, timeout=30)
step(result, "register_candidate_api", r.status_code == 200, {"status": r.status_code, "body": r.text[:200], "candidate_name": candidate_name})
r.raise_for_status()
candidate_id = r.json()["candidate_id"]

r = session.post(f"{API}/admin/generate-test", json={"candidate_ids": [candidate_id]}, headers=headers, timeout=60)
step(result, "generate_test_api", r.status_code == 200, {"status": r.status_code, "body": r.text[:300]})
r.raise_for_status()

r = session.get(f"{API}/candidates", headers=headers, timeout=30)
r.raise_for_status()
candidate = next(c for c in r.json() if c["id"] == candidate_id)
test_token = candidate.get("test_token")
step(result, "candidate_has_token", bool(test_token) and candidate.get("test_status") == "pending", {"test_status": candidate.get("test_status"), "token_len": len(test_token or "")})

r = session.get(f"{API}/test/{test_token}", timeout=30)
step(result, "get_test_api", r.status_code == 200 and r.json().get("status") == "active", {"status": r.status_code, "body": r.text[:200]})
r.raise_for_status()
questions = r.json()["questions"]
answers = {q["id"]: correct_map[q["id"]] for q in questions}
r = session.post(f"{API}/test/{test_token}/submit", json={"answers": answers}, timeout=30)
step(result, "submit_passed_test_api", r.status_code == 200 and r.json().get("passed") is True, {"status": r.status_code, "body": r.text[:300]})
r.raise_for_status()
cert_id = r.json().get("certificate_id")

r = session.get(f"{API}/certificate/{test_token}", timeout=30)
step(result, "certificate_info_api", r.status_code == 200 and r.json().get("certificate_id") == cert_id, {"status": r.status_code, "body": r.text[:300]})
r.raise_for_status()
cert_info = r.json()

r = session.get(f"{API}/certificate/{test_token}/pdf", timeout=30)
pdf_path = OUT / f"certificate_{unique}.pdf"
pdf_path.write_bytes(r.content)
step(
    result,
    "certificate_pdf_download_api",
    r.status_code == 200 and r.content.startswith(b"%PDF") and r.headers.get("content-type", "").startswith("application/pdf"),
    {"status": r.status_code, "content_type": r.headers.get("content-type"), "bytes": len(r.content), "path": str(pdf_path)},
)
r.raise_for_status()

generated_png = OUT / f"certificate_{unique}.png"
generated_img = render_pdf_bytes_to_png(r.content, generated_png)
step(result, "certificate_pdf_renders_to_png", generated_png.exists(), {"path": str(generated_png), "size": generated_img.size})

# Build a baseline PDF using the same clean template with no drawn values. This makes compression/rendering comparable.
template_path = Path("/app/backend/assets/cert_template_clean.jpg")
clean_img = Image.open(template_path).convert("RGB")
baseline_pdf = OUT / "baseline_clean_template.pdf"
clean_img.save(baseline_pdf, "PDF", resolution=150.0)
baseline_png = OUT / "baseline_clean_template.png"
baseline_img = render_pdf_bytes_to_png(baseline_pdf.read_bytes(), baseline_png)

sx = generated_img.width / 1222
sy = generated_img.height / 864
mask = Image.new("L", generated_img.size, 255)
draw = ImageDraw.Draw(mask)
# Mask only the new text/underline regions; icon/label areas stay unmasked so any white boxes there are detected.
for box in [
    (275, 388, 910, 470),  # candidate name + underline
    (332, 636, 500, 664),  # date value only
    (552, 636, 765, 664),  # cert ID value only
    (784, 636, 1125, 664),  # training centre value only
]:
    scaled = tuple(int(v * sx if i % 2 == 0 else v * sy) for i, v in enumerate(box))
    draw.rectangle(scaled, fill=0)
diff = ImageChops.difference(generated_img, baseline_img)
stat = ImageStat.Stat(diff, mask)
mean_diff = sum(stat.mean) / 3
max_diff = max(stat.extrema[0][1], stat.extrema[1][1], stat.extrema[2][1])
step(result, "background_matches_clean_template_outside_text_only", mean_diff < 2.5, {"mean_rgb_abs_diff": mean_diff, "max_channel_diff": max_diff})

# Directly check regions around date/cert/place icons are not materially changed by generated PDF.
icon_regions = {
    "calendar_icon_and_label": (255, 585, 520, 635),
    "cert_id_icon_and_label": (475, 585, 775, 635),
    "map_pin_icon_and_label": (705, 585, 1065, 635),
}
for label, box in icon_regions.items():
    scaled = tuple(int(v * sx if i % 2 == 0 else v * sy) for i, v in enumerate(box))
    g_crop = generated_img.crop(scaled)
    b_crop = baseline_img.crop(scaled)
    g_crop.save(OUT / f"{label}_{unique}.png")
    region_diff = ImageChops.difference(g_crop, b_crop)
    region_stat = ImageStat.Stat(region_diff)
    region_mean = sum(region_stat.mean) / 3
    step(result, f"{label}_unchanged", region_mean < 2.5, {"mean_rgb_abs_diff": region_mean, "crop": str(OUT / f"{label}_{unique}.png")})

# Crop dynamic fields for human audit.
for label, box in {
    "name_field": (260, 360, 940, 490),
    "date_value": (310, 610, 525, 690),
    "cert_id_value": (525, 610, 795, 690),
    "training_centre_value": (765, 610, 1140, 690),
}.items():
    scaled = tuple(int(v * sx if i % 2 == 0 else v * sy) for i, v in enumerate(box))
    generated_img.crop(scaled).save(OUT / f"{label}_{unique}.png")

# Asset checks used by the landing page.
kfr = Image.open("/app/frontend/public/assets/kfr-shield.png")
wisdom = Image.open("/app/frontend/public/assets/wisdom4future-logo.png")
result["assets"]["kfr_shield"] = {"mode": kfr.mode, "size": kfr.size, "transparent_border_ratio": alpha_border_ratio(kfr)}
result["assets"]["wisdom4future"] = {"mode": wisdom.mode, "size": wisdom.size, "red_pixel_ratio": red_pixel_ratio(wisdom)}
step(result, "kfr_shield_has_transparent_outer_background", kfr.mode == "RGBA" and alpha_border_ratio(kfr) > 0.95, result["assets"]["kfr_shield"])
step(result, "wisdom_logo_has_no_red_certificate_bleed", red_pixel_ratio(wisdom) < 0.01, result["assets"]["wisdom4future"])

result.update(
    {
        "candidate_id": candidate_id,
        "test_token": test_token,
        "dynamic_values": {
            "candidate_name": candidate_name,
            "certificate_id": cert_id,
            "training_date": cert_info.get("training_date"),
            "training_place": cert_info.get("training_place"),
        },
        "pdf_path": str(pdf_path),
        "png_path": str(generated_png),
        "baseline_png_path": str(baseline_png),
    }
)

json_path = OUT / f"certificate_branding_result_{unique}.json"
json_path.write_text(json.dumps(result, indent=2))
Path("/app/test_reports/certificate_branding_iter6_latest.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))

if not all(s["ok"] for s in result["steps"]):
    raise SystemExit(1)