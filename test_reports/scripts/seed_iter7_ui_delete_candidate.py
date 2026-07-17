import json
import uuid
from pathlib import Path

import requests


BASE_URL = "https://responder-registry.preview.emergentagent.com"
API = f"{BASE_URL}/api"
OUT = Path("/app/test_reports/bug_assets/iter7")
OUT.mkdir(parents=True, exist_ok=True)

s = requests.Session()
login = s.post(f"{API}/auth/login", json={"email": "admin@kfr.org", "password": "Kfr@2026"}, timeout=30)
login.raise_for_status()
headers = {"Authorization": f"Bearer {login.json()['token']}"}
events = s.get(f"{API}/events", timeout=30)
events.raise_for_status()
event = events.json()[0]

unique = uuid.uuid4().hex[:10]
payload = {
    "name": f"QA Iter7 UISecond {unique}",
    "phone": "9876501234",
    "email": f"qa_iter7_uisecond_{unique}@example.com",
    "dob": "1994-07-17",
    "district": "Ernakulam",
    "category": "Volunteer",
    "organisation": "Aster Medcity",
    "event_id": event["id"],
}
reg = s.post(f"{API}/candidates/register", json=payload, timeout=30)
reg.raise_for_status()
candidate_id = reg.json()["candidate_id"]
state = {"candidate_id": candidate_id, "payload": payload, "api": API}
state_path = OUT / "iter7_ui_delete_second_state.json"
state_path.write_text(json.dumps(state, indent=2))
print(json.dumps(state, indent=2))