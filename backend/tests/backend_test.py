"""Backend tests for Kerala First Responders Mission 100K"""
import os
import io
import csv
import uuid
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://responder-registry.preview.emergentagent.com').rstrip('/')
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "admin@kfr.org"
ADMIN_PW = "Kfr@2026"


@pytest.fixture(scope="session")
def admin_token():
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PW})
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    data = r.json()
    assert "token" in data and "admin" in data
    return data["token"]


@pytest.fixture(scope="session")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def seeded_event():
    r = requests.get(f"{API}/events")
    assert r.status_code == 200
    events = r.json()
    assert len(events) >= 1
    return events[0]


# ---- Auth ----
class TestAuth:
    def test_login_invalid(self):
        r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": "wrong"})
        assert r.status_code == 401

    def test_me_without_token(self):
        r = requests.get(f"{API}/auth/me")
        assert r.status_code in (401, 403)

    def test_me_with_token(self, auth_headers):
        r = requests.get(f"{API}/auth/me", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["email"] == ADMIN_EMAIL


# ---- Reference data ----
class TestRefData:
    def test_events(self):
        r = requests.get(f"{API}/events")
        assert r.status_code == 200 and len(r.json()) >= 1

    def test_organisations(self):
        r = requests.get(f"{API}/organisations")
        assert r.status_code == 200
        names = [o["name"] for o in r.json()]
        assert "Aster Medcity" in names

    def test_districts(self):
        r = requests.get(f"{API}/districts")
        assert r.status_code == 200 and len(r.json()) >= 14

    def test_categories(self):
        r = requests.get(f"{API}/categories")
        assert r.status_code == 200 and len(r.json()) >= 5


# ---- Candidate registration + admin flow ----
class TestCandidateFlow:
    unique = uuid.uuid4().hex[:8]

    def _payload(self, event_id, email=None):
        return {
            "name": f"TEST_Candidate_{self.unique}",
            "phone": "9876543210",
            "email": email or f"test_{self.unique}@example.com",
            "dob": "1995-05-20",
            "district": "Ernakulam",
            "category": "Healthcare Worker",
            "organisation": "Aster Medcity",
            "event_id": event_id,
        }

    def test_register(self, seeded_event):
        r = requests.post(f"{API}/candidates/register", json=self._payload(seeded_event["id"]))
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["ok"] is True and "candidate_id" in data
        pytest.candidate_id = data["candidate_id"]

    def test_register_duplicate(self, seeded_event):
        r = requests.post(f"{API}/candidates/register", json=self._payload(seeded_event["id"]))
        assert r.status_code == 400

    def test_register_invalid_email(self, seeded_event):
        p = self._payload(seeded_event["id"], email="not-email")
        r = requests.post(f"{API}/candidates/register", json=p)
        assert r.status_code in (400, 422)

    def test_register_invalid_event(self):
        r = requests.post(f"{API}/candidates/register", json=self._payload("nonexistent"))
        assert r.status_code == 400

    def test_list_candidates_requires_auth(self):
        r = requests.get(f"{API}/candidates")
        assert r.status_code in (401, 403)

    def test_list_candidates(self, auth_headers):
        r = requests.get(f"{API}/candidates", headers=auth_headers)
        assert r.status_code == 200
        cs = r.json()
        found = next((c for c in cs if c["id"] == pytest.candidate_id), None)
        assert found is not None
        assert found.get("event_name")

    def test_generate_test(self, auth_headers):
        r = requests.post(f"{API}/admin/generate-test", json={"candidate_ids": [pytest.candidate_id]}, headers=auth_headers)
        assert r.status_code == 200, r.text
        # Verify token set
        cs = requests.get(f"{API}/candidates", headers=auth_headers).json()
        found = next((c for c in cs if c["id"] == pytest.candidate_id), None)
        assert found["test_status"] == "pending"
        assert found["test_token"]
        pytest.test_token = found["test_token"]

    def test_get_test(self):
        r = requests.get(f"{API}/test/{pytest.test_token}")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "active"
        assert len(data["questions"]) == 10
        pytest.q_ids = [q["id"] for q in data["questions"]]

    def test_submit_pass(self, auth_headers):
        # Get correct answers via admin questions API
        r = requests.get(f"{API}/questions", headers=auth_headers)
        assert r.status_code == 200
        correct = {q["id"]: q["correct_key"] for q in r.json()}
        answers = {qid: correct[qid] for qid in pytest.q_ids}
        r = requests.post(f"{API}/test/{pytest.test_token}/submit", json={"answers": answers})
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["passed"] is True
        assert data["score"] == 10
        assert data["certificate_id"]

    def test_get_test_after_submit(self):
        r = requests.get(f"{API}/test/{pytest.test_token}")
        assert r.status_code == 200
        assert r.json()["status"] == "completed"

    def test_cert_pdf(self):
        r = requests.get(f"{API}/certificate/{pytest.test_token}/pdf")
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert r.content.startswith(b"%PDF")

    def test_cert_pdf_invalid(self):
        r = requests.get(f"{API}/certificate/invalidtoken/pdf")
        assert r.status_code == 404


class TestFailFlow:
    unique = uuid.uuid4().hex[:8]

    def test_full_fail_flow(self, seeded_event, auth_headers):
        # register
        payload = {
            "name": f"TEST_Fail_{self.unique}",
            "phone": "9876500000",
            "email": f"test_fail_{self.unique}@example.com",
            "dob": "1990-01-01",
            "district": "Kollam",
            "category": "Student",
            "organisation": "Aster Medcity",
            "event_id": seeded_event["id"],
        }
        r = requests.post(f"{API}/candidates/register", json=payload)
        assert r.status_code == 200
        cid = r.json()["candidate_id"]
        r = requests.post(f"{API}/admin/generate-test", json={"candidate_ids": [cid]}, headers=auth_headers)
        assert r.status_code == 200
        cs = requests.get(f"{API}/candidates", headers=auth_headers).json()
        found = next(c for c in cs if c["id"] == cid)
        token = found["test_token"]
        r = requests.get(f"{API}/test/{token}")
        qs = r.json()["questions"]
        # Wrong answers - use "Z"
        answers = {q["id"]: "Z" for q in qs}
        r = requests.post(f"{API}/test/{token}/submit", json={"answers": answers})
        assert r.status_code == 200
        data = r.json()
        assert data["passed"] is False
        assert data["certificate_id"] is None
        # No cert available
        r = requests.get(f"{API}/certificate/{token}/pdf")
        assert r.status_code == 404


# ---- Questions CRUD ----
class TestQuestions:
    def test_list_requires_auth(self):
        r = requests.get(f"{API}/questions")
        assert r.status_code in (401, 403)

    def test_list_seeded(self, auth_headers):
        r = requests.get(f"{API}/questions", headers=auth_headers)
        assert r.status_code == 200
        assert len(r.json()) >= 15

    def test_crud(self, auth_headers):
        payload = {
            "text": "TEST_ question?",
            "options": [{"key": "A", "text": "a"}, {"key": "B", "text": "b"}, {"key": "C", "text": "c"}, {"key": "D", "text": "d"}],
            "correct_key": "A",
        }
        r = requests.post(f"{API}/questions", json=payload, headers=auth_headers)
        assert r.status_code == 200
        qid = r.json()["id"]
        payload["text"] = "TEST_ updated?"
        r = requests.put(f"{API}/questions/{qid}", json=payload, headers=auth_headers)
        assert r.status_code == 200
        r = requests.delete(f"{API}/questions/{qid}", headers=auth_headers)
        assert r.status_code == 200


# ---- Events/Orgs CRUD ----
class TestEventsOrgs:
    def test_event_crud(self, auth_headers):
        r = requests.post(f"{API}/events", json={
            "name": "TEST_Event", "training_date": "2026-06-01", "place": "Kochi", "trainer": "T", "organisation": "Aster Medcity"
        }, headers=auth_headers)
        assert r.status_code == 200
        eid = r.json()["id"]
        r = requests.delete(f"{API}/events/{eid}", headers=auth_headers)
        assert r.status_code == 200

    def test_org_crud(self, auth_headers):
        name = f"TEST_Org_{uuid.uuid4().hex[:6]}"
        r = requests.post(f"{API}/organisations", json={"name": name}, headers=auth_headers)
        assert r.status_code == 200
        oid = r.json()["id"]
        r = requests.post(f"{API}/organisations", json={"name": name}, headers=auth_headers)
        assert r.status_code == 400
        r = requests.delete(f"{API}/organisations/{oid}", headers=auth_headers)
        assert r.status_code == 200


# ---- Reports ----
class TestReports:
    def test_summary(self, auth_headers):
        r = requests.get(f"{API}/reports/summary", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "totals" in data and "district" in data and "category" in data and "organisation" in data

    def test_export(self, auth_headers):
        r = requests.get(f"{API}/reports/export", headers=auth_headers)
        assert r.status_code == 200
        assert "text/csv" in r.headers.get("content-type", "")
        reader = csv.reader(io.StringIO(r.text))
        rows = list(reader)
        assert len(rows) >= 1  # header

    def test_export_filtered(self, auth_headers):
        r = requests.get(f"{API}/reports/export?district=Ernakulam", headers=auth_headers)
        assert r.status_code == 200
