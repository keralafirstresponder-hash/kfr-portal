import json
from pathlib import Path

report = {
  "verdict": "fixed",
  "user_reported_bug": "again the certificate is not good. dont make the background stripes in the previously mentioned places. just write on the existing background. the stripes and white boxes make the part of icons hidden. the uploaded one is the logo of KFR. make this in the place of croped one.so that the logo become clear. in the website place this logo in the hero area with neat form. in the are of in partnership with... make the logo of wisdom foundation in a neat way. it is croped from the certificate. so it is not visible enough and also have a red part from the certificte. the be fist logo is the program name of aster medicity. so it should be place in another place. place that logo in another place without affecting the overall design. its the program name given by aster for this mission 100K. not mention this anywhere but consider and place th e be first logo in that way",
  "summary": "Focused bug verification passed. No relevant testing skill found. Rendered a real certificate PDF for a newly passed candidate and confirmed it draws values directly on the clean template: no white patches/stripes, and calendar/certificate/map-pin icons are unchanged/fully visible. Browser verification confirmed the new KFR shield appears large in the hero, partner strip contains only Aster + Wisdom, Wisdom has no red bleed and is on a white chip, and BeFirst is only in the footer. Smoke-checked /register, /admin/login, admin dashboard/candidates, /test/{token}, and certificate PDF download.",
  "backend_issues": {
    "critical": [],
    "minor": [
      {
        "endpoint": "POST /api/admin/generate-test",
        "issue": "The endpoint generated a usable test token, but email delivery reported sent=0, failed=1 in preview. This did not block the certificate branding verification, but the email integration is not fully working in this environment."
      }
    ]
  },
  "frontend_issues": {
    "ui_bugs": [],
    "integration_issues": [],
    "design_issues": []
  },
  "test_report_links": [
    "/app/test_reports/scripts/verify_certificate_branding_iter6.py",
    "/app/test_reports/certificate_branding_iter6_latest.json",
    "/app/test_reports/bug_assets/iter6_certificate_branding/certificate_64387216.pdf",
    "/app/test_reports/bug_assets/iter6_certificate_branding/certificate_64387216.png"
  ],
  "action_items": [
    "Optional: investigate preview email delivery for POST /api/admin/generate-test, which returned failed=1 despite creating the test token."
  ],
  "critical_code_review_comments": [
    "certificate.py loads cert_template_clean.jpg and only draws text/underline; no blanking rectangles/patches were found in code or rendered output.",
    "LandingPage.js uses /assets/kfr-shield.png for nav/hero/footer; hero image has data-testid='hero-kfr-shield'. Partner strip includes only /assets/aster-medcity-logo.png and /assets/wisdom4future-logo.png; footer includes /assets/befirst-logo.png."
  ],
  "updated_files": [
    "/app/test_reports/scripts/verify_certificate_branding_iter6.py",
    "/app/test_reports/scripts/write_bug_report_iter6.py",
    "/app/test_reports/bug_verification_6.json",
    "/app/test_reports/iteration_6.json"
  ],
  "success_rate": {"backend": "95%", "frontend": "100%"},
  "seed_data_creation": "Created candidate QA Certificate No Boxes 64387216 (id d2ef768906ec9049), generated token fb5i016485Jfjtchag4FfeOVMKNA4NRP, submitted 10/10 correct answers, certificate KFR-2026-F8A84A.",
  "retest_needed": False,
  "should_main_agent_self_test": False,
  "context_for_next_testing_agent": "Use /app/test_reports/scripts/verify_certificate_branding_iter6.py for repeatable API/PDF checks. Browser automation passed using token fb5i016485Jfjtchag4FfeOVMKNA4NRP for the completed test page. Certificate rendered PNG and crops are under /app/test_reports/bug_assets/iter6_certificate_branding/.",
  "rca_of_the_issue": "Previous certificate artifacts were caused by drawing blanking patches/stripes over dynamic fields. The current implementation uses a pre-cleaned template and overlays only text, confirmed by near-zero diff outside the dynamic text regions and zero diff over icon/label crops."
}

for path in [Path("/app/test_reports/bug_verification_6.json"), Path("/app/test_reports/iteration_6.json")]:
    path.write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))