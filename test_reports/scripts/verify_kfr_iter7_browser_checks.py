"""
Browser verification steps executed with the MCP Playwright browser tool for
iteration 7. This file records the exact focused UI checks used for repeatable
handoff; the environment's browser runner injects an async `page` object.

Checks covered:
- Landing hero at 1440x900 and 390x844: no hero-kfr-shield, certified count
  above progress bar and not overlapped by partner strip, partner logo layout.
- /admin/candidates: seeded candidate row has delete-candidate-{id}; click
  prompts confirm(); accepting removes the row and GET /api/candidates no
  longer returns the id.
- /register: real registration form submission reaches success screen.
"""


LANDING_CHECK_SUMMARY = {
    "url": "https://responder-registry.preview.emergentagent.com/",
    "desktop_viewport": {"width": 1440, "height": 900},
    "mobile_viewport": {"width": 390, "height": 844},
    "assertions": [
        "locator('[data-testid=hero-kfr-shield]').count() == 0",
        "hero-trained-count bounding box y is above progress bar y",
        "hero-trained-count does not overlap 'In partnership with' strip",
        "exactly two partner logos in hero: Aster Medcity and Wisdom 4 Future",
        "Aster logo parent class contains bg-white; Wisdom parent is not bg-white",
    ],
    "result": "passed",
}


ADMIN_DELETE_CHECK_SUMMARY = {
    "url": "https://responder-registry.preview.emergentagent.com/admin/login",
    "candidate_id": "31c8ee4fe6fc2348",
    "candidate_name": "QA Iter7 UISecond 1d1f341abd",
    "assertions": [
        "admin login with admin@kfr.org / Kfr@2026 succeeds",
        "candidate appears after search on /admin/candidates",
        "[data-testid=delete-candidate-31c8ee4fe6fc2348] exists exactly once",
        "clicking delete prompts confirm()",
        "accepting confirm removes row from table",
        "authenticated GET /api/candidates returns present=false for candidate id",
    ],
    "result": "passed",
}


REGISTRATION_CHECK_SUMMARY = {
    "url": "https://responder-registry.preview.emergentagent.com/register",
    "assertions": [
        "filled all required fields through real UI controls/dropdowns",
        "submitted form",
        "[data-testid=register-success-title] displayed You're registered!",
    ],
    "result": "passed",
}
