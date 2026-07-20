from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import io
import csv
import random
import secrets
import asyncio
import bcrypt
import jwt as pyjwt
import httpx
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone, timedelta, date

from certificate import build_certificate_pdf
from seed_data import DEFAULT_QUESTIONS, DEFAULT_ORGANISATIONS
from seed_data_ml import MALAYALAM_QUESTIONS

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Config
JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGO = "HS256"
EMAIL_BASE_URL = "https://integrations.emergentagent.com"
EMAIL_KEY = os.environ.get('EMERGENT_EMAIL_KEY', '')
EMAIL_FROM_NAME = os.environ.get('EMAIL_FROM_NAME', 'Kerala First Responders')
PUBLIC_BASE_URL = os.environ.get('PUBLIC_BASE_URL', '')

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer(auto_error=False)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============ Models ============
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AdminMe(BaseModel):
    id: str
    email: EmailStr
    name: str

class CandidateCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr
    dob: str  # ISO date
    district: str
    category: str
    organisation: str
    event_id: str

class CandidateOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    phone: str
    email: EmailStr
    dob: str
    district: str
    category: str
    organisation: str
    event_id: str
    event_name: Optional[str] = None
    event_date: Optional[str] = None
    event_place: Optional[str] = None
    test_status: str = "not_sent"  # not_sent | pending | passed | failed
    test_score: Optional[int] = None
    test_token: Optional[str] = None
    certificate_id: Optional[str] = None
    created_at: str

class EventCreate(BaseModel):
    name: str
    training_date: str  # ISO date
    place: str
    trainer: Optional[str] = ""
    organisation: Optional[str] = "Aster Medcity"

class EventOut(BaseModel):
    id: str
    name: str
    training_date: str
    place: str
    trainer: str
    organisation: str
    created_at: str

class OrganisationCreate(BaseModel):
    name: str

class OrganisationOut(BaseModel):
    id: str
    name: str

class QuestionOption(BaseModel):
    key: str  # A, B, C, D
    text: str

class QuestionCreate(BaseModel):
    text: str
    options: List[QuestionOption]
    correct_key: str
    language: Optional[str] = "en"

class QuestionOut(QuestionCreate):
    id: str

class QuestionPublic(BaseModel):
    id: str
    text: str
    options: List[QuestionOption]

class GenerateTestRequest(BaseModel):
    candidate_ids: List[str]

class TestSubmit(BaseModel):
    answers: dict  # {question_id: option_key}


# ============ Helpers ============
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except Exception:
        return False

def create_token(admin_id: str) -> str:
    payload = {
        "sub": admin_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc),
    }
    return pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

async def get_current_admin(creds: HTTPAuthorizationCredentials = Depends(security)):
    if not creds:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = pyjwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
        admin_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    admin = await db.admins.find_one({"id": admin_id}, {"_id": 0, "password_hash": 0})
    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found")
    return admin

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def gen_id() -> str:
    return secrets.token_hex(8)


# ============ Auth ============
@api_router.post("/auth/login")
async def login(req: LoginRequest):
    admin = await db.admins.find_one({"email": req.email.lower()})
    if not admin or not verify_password(req.password, admin.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(admin["id"])
    return {"token": token, "admin": {"id": admin["id"], "email": admin["email"], "name": admin["name"]}}

@api_router.get("/auth/me")
async def me(admin = Depends(get_current_admin)):
    return admin


# ============ Events ============
@api_router.get("/events")
async def list_events():
    docs = await db.events.find({}, {"_id": 0}).sort("training_date", -1).to_list(500)
    return docs

@api_router.post("/events")
async def create_event(req: EventCreate, admin = Depends(get_current_admin)):
    doc = {
        "id": gen_id(),
        "name": req.name,
        "training_date": req.training_date,
        "place": req.place,
        "trainer": req.trainer or "",
        "organisation": req.organisation or "Aster Medcity",
        "created_at": now_iso(),
    }
    await db.events.insert_one(doc)
    doc.pop("_id", None)
    return doc

@api_router.delete("/events/{event_id}")
async def delete_event(event_id: str, admin = Depends(get_current_admin)):
    await db.events.delete_one({"id": event_id})
    return {"ok": True}


# ============ Organisations ============
@api_router.get("/organisations")
async def list_orgs():
    docs = await db.organisations.find({}, {"_id": 0}).sort("name", 1).to_list(500)
    return docs

@api_router.post("/organisations")
async def create_org(req: OrganisationCreate, admin = Depends(get_current_admin)):
    existing = await db.organisations.find_one({"name": req.name})
    if existing:
        raise HTTPException(status_code=400, detail="Organisation already exists")
    doc = {"id": gen_id(), "name": req.name}
    await db.organisations.insert_one(doc)
    doc.pop("_id", None)
    return doc

@api_router.delete("/organisations/{org_id}")
async def delete_org(org_id: str, admin = Depends(get_current_admin)):
    await db.organisations.delete_one({"id": org_id})
    return {"ok": True}


# ============ Questions ============
@api_router.get("/questions")
async def list_questions(admin = Depends(get_current_admin)):
    docs = await db.questions.find({}, {"_id": 0}).to_list(500)
    return docs

@api_router.post("/questions")
async def create_question(req: QuestionCreate, admin = Depends(get_current_admin)):
    if not any(o.key == req.correct_key for o in req.options):
        raise HTTPException(status_code=400, detail="Correct key must match an option")
    doc = {"id": gen_id(), **req.model_dump()}
    await db.questions.insert_one(doc)
    doc.pop("_id", None)
    return doc

@api_router.put("/questions/{qid}")
async def update_question(qid: str, req: QuestionCreate, admin = Depends(get_current_admin)):
    if not any(o.key == req.correct_key for o in req.options):
        raise HTTPException(status_code=400, detail="Correct key must match an option")
    await db.questions.update_one({"id": qid}, {"$set": req.model_dump()})
    return {"ok": True}

@api_router.delete("/questions/{qid}")
async def delete_question(qid: str, admin = Depends(get_current_admin)):
    await db.questions.delete_one({"id": qid})
    return {"ok": True}


# ============ Candidates ============
async def _enrich_candidate(c: dict) -> dict:
    if c.get("event_id"):
        ev = await db.events.find_one({"id": c["event_id"]}, {"_id": 0})
        if ev:
            c["event_name"] = ev["name"]
            c["event_date"] = ev["training_date"]
            c["event_place"] = ev["place"]
    return c

@api_router.post("/candidates/register")
async def register_candidate(req: CandidateCreate):
    # Check duplicate by email+event
    existing = await db.candidates.find_one({"email": req.email.lower(), "event_id": req.event_id})
    if existing:
        raise HTTPException(status_code=400, detail="Already registered for this training session")
    event = await db.events.find_one({"id": req.event_id})
    if not event:
        raise HTTPException(status_code=400, detail="Invalid training session")
    doc = {
        "id": gen_id(),
        "name": req.name,
        "phone": req.phone,
        "email": req.email.lower(),
        "dob": req.dob,
        "district": req.district,
        "category": req.category,
        "organisation": req.organisation,
        "event_id": req.event_id,
        "test_status": "not_sent",
        "test_score": None,
        "test_token": None,
        "certificate_id": None,
        "created_at": now_iso(),
    }
    await db.candidates.insert_one(doc)
    doc.pop("_id", None)
    return {"ok": True, "candidate_id": doc["id"]}

@api_router.get("/candidates")
async def list_candidates(
    admin = Depends(get_current_admin),
    district: Optional[str] = None,
    category: Optional[str] = None,
    organisation: Optional[str] = None,
    event_id: Optional[str] = None,
    test_status: Optional[str] = None,
):
    q = {}
    if district: q["district"] = district
    if category: q["category"] = category
    if organisation: q["organisation"] = organisation
    if event_id: q["event_id"] = event_id
    if test_status: q["test_status"] = test_status
    docs = await db.candidates.find(q, {"_id": 0}).sort("created_at", -1).to_list(10000)
    for c in docs:
        await _enrich_candidate(c)
    return docs


@api_router.delete("/candidates/{candidate_id}")
async def delete_candidate(candidate_id: str, admin = Depends(get_current_admin)):
    result = await db.candidates.delete_one({"id": candidate_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"ok": True, "deleted": candidate_id}


# ============ Test Generation & Emails ============
async def _send_email(to_email: str, subject: str, html: str):
    if not EMAIL_KEY:
        logger.warning("EMERGENT_EMAIL_KEY not set — skipping email")
        return False
    try:
        async with httpx.AsyncClient(timeout=30) as ac:
            resp = await ac.post(
                f"{EMAIL_BASE_URL}/api/v1/email/send",
                headers={"X-Email-Key": EMAIL_KEY},
                json={"to": [to_email], "subject": subject, "html": html, "from_name": EMAIL_FROM_NAME},
            )
            resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Email send failed to {to_email}: {e}")
        return False

def _test_email_html(name: str, test_url: str, event_name: str, training_date: str) -> str:
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="font-family: Arial, sans-serif; background:#F8FAFC; padding:32px 0;">
      <tr><td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 4px 12px rgba(11,27,61,0.08);">
          <tr><td style="background:#0B1B3D; padding:28px 32px; color:#ffffff;">
            <div style="font-size:12px; letter-spacing:3px; color:#D4AF37; text-transform:uppercase;">Kerala First Responders</div>
            <div style="font-size:22px; font-weight:700; margin-top:6px;">Mission 100K &mdash; CPR Assessment</div>
          </td></tr>
          <tr><td style="padding:32px;">
            <p style="font-size:16px; color:#1E293B;">Dear {name},</p>
            <p style="font-size:14px; color:#334155; line-height:1.7;">
              Thank you for attending the <b>{event_name}</b> training on <b>{training_date}</b>.
              You are now invited to take your CPR &amp; BLS knowledge assessment.
              You must score at least <b>5 out of 10</b> to earn your Kerala First Responder certificate.
            </p>
            <div style="text-align:left; margin:28px 0;">
              <a href="{test_url}" style="background:#E63946; color:#fff; padding:14px 28px; border-radius:8px; text-decoration:none; font-weight:600; display:inline-block;">Take the Assessment</a>
            </div>
            <p style="font-size:12px; color:#64748B;">Or copy this link: <br/><span style="color:#0B1B3D; word-break:break-all;">{test_url}</span></p>
          </td></tr>
          <tr><td style="background:#F1F5F9; padding:20px 32px; font-size:11px; color:#64748B;">
            An initiative by <b>Wisdom Foundation</b> &middot; Medical Partner: <b>Aster Medcity</b>
          </td></tr>
        </table>
      </td></tr>
    </table>
    """

def _cert_email_html(name: str, cert_url: str, score: int) -> str:
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="font-family: Arial, sans-serif; background:#F8FAFC; padding:32px 0;">
      <tr><td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden;">
          <tr><td style="background:#0B1B3D; padding:28px 32px; color:#fff;">
            <div style="font-size:12px; letter-spacing:3px; color:#D4AF37; text-transform:uppercase;">Congratulations!</div>
            <div style="font-size:22px; font-weight:700; margin-top:6px;">You are now a Kerala First Responder</div>
          </td></tr>
          <tr><td style="padding:32px;">
            <p style="font-size:16px; color:#1E293B;">Dear {name},</p>
            <p style="font-size:14px; color:#334155; line-height:1.7;">
              You have successfully passed the CPR &amp; BLS Assessment with a score of <b>{score}/10</b>.
              Your official <b>Kerala First Responder</b> certificate is ready.
            </p>
            <div style="margin:28px 0;">
              <a href="{cert_url}" style="background:#D4AF37; color:#0B1B3D; padding:14px 28px; border-radius:8px; text-decoration:none; font-weight:700; display:inline-block;">Download Certificate (PDF)</a>
            </div>
            <p style="font-size:13px; color:#334155;">Be a hero. Save a life.</p>
          </td></tr>
        </table>
      </td></tr>
    </table>
    """

def _get_public_base(request_host: Optional[str] = None) -> str:
    if PUBLIC_BASE_URL:
        return PUBLIC_BASE_URL.rstrip("/")
    return ""

@api_router.post("/admin/generate-test")
async def generate_test(req: GenerateTestRequest, admin = Depends(get_current_admin)):
    if not req.candidate_ids:
        raise HTTPException(status_code=400, detail="No candidates selected")
    sent = 0
    failed = 0
    for cid in req.candidate_ids:
        c = await db.candidates.find_one({"id": cid})
        if not c:
            failed += 1
            continue
        token = secrets.token_urlsafe(24)
        await db.candidates.update_one(
            {"id": cid},
            {"$set": {"test_token": token, "test_status": "pending", "test_score": None, "certificate_id": None}}
        )
        ev = await db.events.find_one({"id": c.get("event_id")}) or {}
        base = _get_public_base()
        test_url = f"{base}/test/{token}" if base else f"/test/{token}"
        html = _test_email_html(c["name"], test_url, ev.get("name", "CPR Training"), ev.get("training_date", ""))
        ok = await _send_email(c["email"], "Your Kerala First Responder Assessment", html)
        if ok:
            sent += 1
        else:
            failed += 1
    return {"sent": sent, "failed": failed, "total": len(req.candidate_ids)}


# ============ Test taking ============
@api_router.get("/test/{token}")
async def get_test(token: str, lang: Optional[str] = None):
    c = await db.candidates.find_one({"test_token": token}, {"_id": 0})
    if not c:
        raise HTTPException(status_code=404, detail="Invalid or expired test link")
    if c.get("test_status") in ("passed", "failed"):
        return {
            "status": "completed",
            "score": c.get("test_score"),
            "passed": c.get("test_status") == "passed",
            "candidate_name": c["name"],
            "certificate_id": c.get("certificate_id"),
        }
    # If language not chosen yet, prompt candidate to pick one
    if lang not in ("en", "ml"):
        return {"status": "language_required", "candidate_name": c["name"]}
    # Pick 10 random questions in the chosen language
    all_q = await db.questions.find({"language": lang}, {"_id": 0}).to_list(500)
    if len(all_q) < 10:
        raise HTTPException(status_code=500, detail=f"Insufficient questions configured for language '{lang}'")
    selected = random.sample(all_q, 10)
    # store selected question IDs + chosen language on candidate
    await db.candidates.update_one(
        {"id": c["id"]},
        {"$set": {"active_question_ids": [q["id"] for q in selected], "test_language": lang}}
    )
    return {
        "status": "active",
        "language": lang,
        "candidate_name": c["name"],
        "questions": [{"id": q["id"], "text": q["text"], "options": q["options"]} for q in selected],
    }

@api_router.post("/test/{token}/submit")
async def submit_test(token: str, body: TestSubmit):
    c = await db.candidates.find_one({"test_token": token})
    if not c:
        raise HTTPException(status_code=404, detail="Invalid test link")
    if c.get("test_status") in ("passed", "failed"):
        raise HTTPException(status_code=400, detail="Test already submitted")
    q_ids = c.get("active_question_ids", [])
    if not q_ids:
        raise HTTPException(status_code=400, detail="Please open the test first")
    questions = await db.questions.find({"id": {"$in": q_ids}}, {"_id": 0}).to_list(50)
    correct_map = {q["id"]: q["correct_key"] for q in questions}
    score = sum(1 for qid, ans in body.answers.items() if correct_map.get(qid) == ans)
    passed = score >= 5
    cert_id = None
    if passed:
        # Cert ID like KFR-2026-XXXXXX
        cert_id = f"KFR-{datetime.now(timezone.utc).year}-{secrets.token_hex(3).upper()}"
    await db.candidates.update_one(
        {"id": c["id"]},
        {"$set": {
            "test_status": "passed" if passed else "failed",
            "test_score": score,
            "certificate_id": cert_id,
            "test_submitted_at": now_iso(),
        }}
    )
    # Email cert if passed
    if passed:
        base = _get_public_base()
        cert_url = f"{base}/api/certificate/{token}/pdf" if base else f"/api/certificate/{token}/pdf"
        html = _cert_email_html(c["name"], cert_url, score)
        asyncio.create_task(_send_email(c["email"], "You are a Certified Kerala First Responder!", html))
    return {"score": score, "passed": passed, "certificate_id": cert_id, "total": 10}


# ============ Certificate ============
@api_router.get("/certificate/{token}")
async def cert_info(token: str):
    c = await db.candidates.find_one({"test_token": token}, {"_id": 0})
    if not c or c.get("test_status") != "passed":
        raise HTTPException(status_code=404, detail="Certificate not available")
    ev = await db.events.find_one({"id": c["event_id"]}, {"_id": 0}) or {}
    return {
        "candidate_name": c["name"],
        "certificate_id": c["certificate_id"],
        "training_date": ev.get("training_date", ""),
        "training_place": ev.get("place", ""),
        "organisation": c.get("organisation", ""),
        "score": c["test_score"],
    }

@api_router.get("/certificate/{token}/pdf")
async def cert_pdf(token: str):
    c = await db.candidates.find_one({"test_token": token}, {"_id": 0})
    if not c or c.get("test_status") != "passed":
        raise HTTPException(status_code=404, detail="Certificate not available")
    ev = await db.events.find_one({"id": c["event_id"]}, {"_id": 0}) or {}
    pdf_bytes = build_certificate_pdf(
        name=c["name"],
        cert_id=c["certificate_id"],
        training_date=ev.get("training_date", ""),
        training_place=ev.get("place", ""),
    )
    filename = f"KFR-Certificate-{c['certificate_id']}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


# ============ Public stats (no auth) — powers the home page counter ============
@api_router.get("/public/stats")
async def public_stats():
    total = await db.candidates.count_documents({})
    passed = await db.candidates.count_documents({"test_status": "passed"})
    return {"candidates": total, "passed": passed, "mission_goal": 100000}


# ============ Reports ============
@api_router.get("/reports/summary")
async def reports_summary(admin = Depends(get_current_admin)):
    total = await db.candidates.count_documents({})
    passed = await db.candidates.count_documents({"test_status": "passed"})
    failed = await db.candidates.count_documents({"test_status": "failed"})
    pending = await db.candidates.count_documents({"test_status": "pending"})
    not_sent = await db.candidates.count_documents({"test_status": "not_sent"})
    events = await db.events.count_documents({})
    orgs = await db.organisations.count_documents({})
    # District-wise
    district_pipe = [{"$group": {"_id": "$district", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
    district_docs = await db.candidates.aggregate(district_pipe).to_list(200)
    # Category-wise
    cat_pipe = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
    cat_docs = await db.candidates.aggregate(cat_pipe).to_list(50)
    # Organisation-wise
    org_pipe = [{"$group": {"_id": "$organisation", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
    org_docs = await db.candidates.aggregate(org_pipe).to_list(50)
    return {
        "totals": {
            "candidates": total, "passed": passed, "failed": failed,
            "pending": pending, "not_sent": not_sent,
            "events": events, "organisations": orgs,
            "mission_goal": 100000,
        },
        "district": [{"name": d["_id"] or "Unknown", "count": d["count"]} for d in district_docs],
        "category": [{"name": d["_id"] or "Unknown", "count": d["count"]} for d in cat_docs],
        "organisation": [{"name": d["_id"] or "Unknown", "count": d["count"]} for d in org_docs],
    }

@api_router.get("/reports/export")
async def export_csv(
    admin = Depends(get_current_admin),
    district: Optional[str] = None,
    category: Optional[str] = None,
    organisation: Optional[str] = None,
    event_id: Optional[str] = None,
    test_status: Optional[str] = None,
):
    q = {}
    if district: q["district"] = district
    if category: q["category"] = category
    if organisation: q["organisation"] = organisation
    if event_id: q["event_id"] = event_id
    if test_status: q["test_status"] = test_status
    docs = await db.candidates.find(q, {"_id": 0}).sort("created_at", -1).to_list(50000)
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Name", "Email", "Phone", "DoB", "District", "Category", "Organisation", "Event", "Training Date", "Place", "Test Status", "Score", "Certificate ID", "Registered"])
    for c in docs:
        ev = await db.events.find_one({"id": c.get("event_id")}, {"_id": 0}) or {}
        writer.writerow([
            c.get("name",""), c.get("email",""), c.get("phone",""), c.get("dob",""),
            c.get("district",""), c.get("category",""), c.get("organisation",""),
            ev.get("name",""), ev.get("training_date",""), ev.get("place",""),
            c.get("test_status",""), c.get("test_score",""), c.get("certificate_id",""),
            c.get("created_at",""),
        ])
    return Response(
        content=out.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="kfr_candidates.csv"'},
    )


# ============ Districts (Kerala) ============
KERALA_DISTRICTS = [
    "Alappuzha","Ernakulam","Idukki","Kannur","Kasaragod","Kollam","Kottayam",
    "Kozhikode","Malappuram","Palakkad","Pathanamthitta","Thiruvananthapuram",
    "Thrissur","Wayanad"
]

@api_router.get("/districts")
async def districts():
    return KERALA_DISTRICTS

@api_router.get("/categories")
async def categories():
    return ["Student", "Professional", "Army", "NCC", "Police", "Teacher", "Healthcare Worker", "Volunteer", "Other"]


# ============ Seed ============
@app.on_event("startup")
async def startup_seed():
    # Seed admin
    if await db.admins.count_documents({}) == 0:
        await db.admins.insert_one({
            "id": gen_id(),
            "email": "admin@kfr.org",
            "name": "KFR Administrator",
            "password_hash": hash_password("Kfr@2026"),
            "created_at": now_iso(),
        })
        logger.info("Seeded default admin: admin@kfr.org / Kfr@2026")
    # Seed organisations
    if await db.organisations.count_documents({}) == 0:
        for name in DEFAULT_ORGANISATIONS:
            await db.organisations.insert_one({"id": gen_id(), "name": name})
        logger.info("Seeded default organisations")
    # Seed questions
    if await db.questions.count_documents({}) == 0:
        for q in DEFAULT_QUESTIONS:
            await db.questions.insert_one({"id": gen_id(), "language": "en", **q})
        logger.info(f"Seeded {len(DEFAULT_QUESTIONS)} English questions")
    # Seed Malayalam questions (idempotent — only if none exist)
    if await db.questions.count_documents({"language": "ml"}) == 0:
        for q in MALAYALAM_QUESTIONS:
            await db.questions.insert_one({"id": gen_id(), "language": "ml", **q})
        logger.info(f"Seeded {len(MALAYALAM_QUESTIONS)} Malayalam questions")
    # Backfill: mark any legacy questions without a language as English
    await db.questions.update_many({"language": {"$exists": False}}, {"$set": {"language": "en"}})
    # Seed a demo event so registration flow works out of the box
    if await db.events.count_documents({}) == 0:
        await db.events.insert_one({
            "id": gen_id(),
            "name": "KFR CPR Training — Kochi Batch 1",
            "training_date": (datetime.now(timezone.utc) + timedelta(days=7)).date().isoformat(),
            "place": "Aster Medcity, Kochi",
            "trainer": "Dr. Anish Menon",
            "organisation": "Aster Medcity",
            "created_at": now_iso(),
        })


app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
