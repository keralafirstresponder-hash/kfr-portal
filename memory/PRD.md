# PRD — Kerala First Responders · Mission 100K

## Problem Statement (verbatim)
Create a website to host events for a team's CPR training program. Same training on different days at different places across Kerala, aiming to train 100,000 people in CPR. Register candidates (Name, Phone, DoB, District, Place of Training, Organisation, Category — Student/Professional/Army/NCC/etc). A test link is emailed to the registered user after training. After the MCQ test, if the user scores ≥5/10 they receive a certificate PDF. Admin can log in, view details, view district-wise & category-wise reports (with filters), and generate reports. Admin can bulk-select users in an event via checkboxes and "Generate Test" — only then the users receive the test link. Admin dashboard should have charts (overall summary, district-wise, category-wise). Program is by Wisdom Foundation, medical partner is Aster Medcity.

## Personas
- **Candidate** — trainee (student / professional / army / NCC / etc.) who registers and takes the assessment.
- **Admin** — KFR program manager who runs sessions, issues tests, and views reports.

## Core requirements (locked)
- Public candidate registration form (Name, Phone, DoB, District, Email, Organisation, Category, Training Session)
- Admin JWT login, single seeded admin
- Admin creates training sessions (name, date, place, trainer, organisation)
- Admin manages organisations dropdown (Aster Medcity by default)
- Admin manages MCQ question bank (15 seeded CPR/BLS questions, 10 picked randomly per test)
- Admin dashboard: totals + district bar chart + category donut + organisation summary
- Bulk-select candidates → Generate Test → unique per-candidate token + Resend email
- Candidate takes 10-MCQ test → ≥5/10 = pass → certificate PDF generated & emailed
- Reports page with filters (district / category / organisation / session) + CSV export
- Certificate PDF branded with KFR + Aster Medcity + Wisdom4Future

## Architecture
- FastAPI backend (`/app/backend/server.py`), MongoDB via MONGO_URL
- ReportLab for certificate PDF (`/app/backend/certificate.py`)
- React 19 + Tailwind + shadcn UI + recharts + lucide-react
- Emergent-managed email proxy (`https://integrations.emergentagent.com`) with `EMERGENT_EMAIL_KEY`

## Implemented — Feb 2026
- ✅ Full public registration flow (single event dropdown)
- ✅ Admin JWT auth, admin dashboard, candidates list, bulk generate-test
- ✅ MCQ test taking with random 10 Q + submission + pass/fail result
- ✅ Certificate PDF (navy/gold branded, KFR + Aster + Wisdom4Future)
- ✅ Reports summary + district/category/organisation aggregations
- ✅ CSV export with filters
- ✅ Organisations + Events + Questions CRUD
- ✅ Backend + frontend fully tested (28/28 backend, frontend green)

## Backlog (P1)
- Logo upload UI for admin (currently ReportLab draws stylised placeholders that match brand colours)
- Certificate settings page for sponsor logos
- Public metric API (currently `/api/reports/summary` requires auth — used on landing via graceful fallback)
- Bulk import candidates via CSV
- Reattempt policy for failed candidates
- SMS delivery via Twilio

## Backlog (P2)
- Multi-admin roles (viewer vs editor)
- Localisation (Malayalam)
- Audit log / activity feed

## Seed data
- Admin: `admin@kfr.org` / `Kfr@2026`
- Organisation: Aster Medcity
- Event: "KFR CPR Training — Kochi Batch 1" (+7 days from seed)
- 15 CPR/BLS MCQs
