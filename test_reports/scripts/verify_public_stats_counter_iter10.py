#!/usr/bin/env python3
"""Focused backend/API verification for public certified counter bug.

Creates one real candidate, moves them through generate-test and passed assessment,
and verifies /api/public/stats matches MongoDB passed count before/after.
"""
import json
import time
from pathlib import Path

import requests
from pymongo import MongoClient
from dotenv import dotenv_values

ROOT = Path('/app')
backend_env = dotenv_values(ROOT / 'backend' / '.env')
frontend_env = dotenv_values(ROOT / 'frontend' / '.env')
BASE_URL = (frontend_env.get('REACT_APP_BACKEND_URL') or 'http://localhost:8001').rstrip('/')
API = f'{BASE_URL}/api'
MONGO_URL = backend_env.get('MONGO_URL', 'mongodb://localhost:27017').strip('"')
DB_NAME = backend_env.get('DB_NAME', 'test_database').strip('"')
ADMIN_EMAIL = 'admin@kfr.org'
ADMIN_PASSWORD = 'Kfr@2026'

session = requests.Session()
results = {
    'base_url': BASE_URL,
    'checks': [],
    'created_candidate_id': None,
    'created_candidate_email': None,
    'token': None,
}


def check(name, ok, details=None):
    results['checks'].append({'name': name, 'ok': bool(ok), 'details': details})
    status = 'PASS' if ok else 'FAIL'
    print(f'{status}: {name} :: {details}')
    if not ok:
        raise AssertionError(f'{name} failed: {details}')


def mongo_counts():
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    total = db.candidates.count_documents({})
    passed = db.candidates.count_documents({'test_status': 'passed'})
    client.close()
    return {'candidates': total, 'passed': passed, 'mission_goal': 100000}


def login_admin():
    r = session.post(f'{API}/auth/login', json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}, timeout=20)
    check('admin login works for candidate/test verification', r.status_code == 200, {'status': r.status_code, 'body': r.text[:200]})
    token = r.json()['token']
    session.headers.update({'Authorization': f'Bearer {token}'})
    return token


def main():
    # Anonymous endpoint check: use fresh session with no token.
    anon = requests.Session()
    r = anon.get(f'{API}/public/stats', timeout=20)
    check('GET /api/public/stats anonymous returns 200 (no auth/no 401)', r.status_code == 200, {'status': r.status_code, 'body': r.text[:200]})
    data = r.json()
    keys_ok = all(k in data for k in ('candidates', 'passed', 'mission_goal'))
    types_ok = isinstance(data.get('candidates'), int) and isinstance(data.get('passed'), int) and isinstance(data.get('mission_goal'), int)
    check('public stats JSON keys and int types', keys_ok and types_ok and data.get('mission_goal') == 100000, data)

    db_before = mongo_counts()
    check('public stats matches MongoDB passed count before increment', data['passed'] == db_before['passed'] and data['candidates'] == db_before['candidates'], {'api': data, 'db': db_before})
    check('preview DB has non-zero passed candidates for landing counter', db_before['passed'] > 0, db_before)
    results['before'] = {'api': data, 'db': db_before}

    # Confirm admin candidates API also agrees with passed count.
    login_admin()
    cr = session.get(f'{API}/candidates', timeout=20)
    check('admin GET /api/candidates still works', cr.status_code == 200, {'status': cr.status_code, 'count': len(cr.json()) if cr.status_code == 200 else None})
    candidates = cr.json()
    admin_passed = sum(1 for c in candidates if c.get('test_status') == 'passed')
    check('public passed count matches admin candidates passed count', admin_passed == data['passed'], {'admin_passed': admin_passed, 'public_passed': data['passed']})

    # Create a real new candidate via public register, generate test as admin, submit passing answers as candidate.
    evr = requests.get(f'{API}/events', timeout=20)
    check('public GET /api/events works for choosing session', evr.status_code == 200 and len(evr.json()) > 0, {'status': evr.status_code, 'count': len(evr.json()) if evr.status_code == 200 else None})
    org_r = requests.get(f'{API}/organisations', timeout=20)
    org_name = org_r.json()[0]['name'] if org_r.status_code == 200 and org_r.json() else 'Aster Medcity'
    event = evr.json()[0]
    stamp = int(time.time())
    email = f'counter-pass-{stamp}@example.com'
    payload = {
        'name': f'Counter Pass {stamp}',
        'phone': f'+9199{stamp % 100000000:08d}',
        'email': email,
        'dob': '1990-01-01',
        'district': 'Ernakulam',
        'category': 'Volunteer',
        'organisation': org_name,
        'event_id': event['id'],
    }
    reg = requests.post(f'{API}/candidates/register', json=payload, timeout=20)
    check('public candidate registration works for new candidate', reg.status_code == 200 and reg.json().get('candidate_id'), {'status': reg.status_code, 'body': reg.text[:300]})
    candidate_id = reg.json()['candidate_id']
    results['created_candidate_id'] = candidate_id
    results['created_candidate_email'] = email

    gen = session.post(f'{API}/admin/generate-test', json={'candidate_ids': [candidate_id]}, timeout=40)
    # Email may fail in preview, but endpoint should complete and token should be written.
    check('admin generate-test endpoint completes for new candidate', gen.status_code == 200, {'status': gen.status_code, 'body': gen.text[:300]})

    cand = session.get(f'{API}/candidates', params={'test_status': 'pending'}, timeout=20)
    check('admin candidates filter pending still works', cand.status_code == 200, {'status': cand.status_code})
    created = next((c for c in cand.json() if c.get('id') == candidate_id), None)
    if not created:
        all_c = session.get(f'{API}/candidates', timeout=20).json()
        created = next((c for c in all_c if c.get('id') == candidate_id), None)
    check('new candidate has pending test token after generate-test', bool(created and created.get('test_token')), {'candidate': {k: created.get(k) for k in ('id','test_status','test_token')} if created else None})
    token = created['test_token']
    results['token'] = token

    # Open test in English, submit all correct answers.
    tr = requests.get(f'{API}/test/{token}', params={'lang': 'en'}, timeout=20)
    check('candidate GET /api/test/{token}?lang=en returns active test', tr.status_code == 200 and tr.json().get('status') == 'active' and len(tr.json().get('questions', [])) == 10, {'status': tr.status_code, 'body_keys': list(tr.json().keys()) if tr.status_code == 200 else tr.text[:200]})
    question_ids = [q['id'] for q in tr.json()['questions']]
    # Correct answers are not public; read them from DB for deterministic QA submission.
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    qs = list(db.questions.find({'id': {'$in': question_ids}}, {'_id': 0, 'id': 1, 'correct_key': 1}))
    correct_map = {q['id']: q['correct_key'] for q in qs}
    client.close()
    answers = {qid: correct_map[qid] for qid in question_ids}
    sub = requests.post(f'{API}/test/{token}/submit', json={'answers': answers}, timeout=20)
    check('candidate submit assessment passes', sub.status_code == 200 and sub.json().get('passed') is True and sub.json().get('score') == 10, {'status': sub.status_code, 'body': sub.text[:300]})

    after = requests.get(f'{API}/public/stats', timeout=20).json()
    db_after = mongo_counts()
    check('public stats returns fresh incremented passed count after assessment pass', after['passed'] == data['passed'] + 1 and after['passed'] == db_after['passed'], {'before_public': data, 'after_public': after, 'db_after': db_after})
    results['after_increment'] = {'api': after, 'db': db_after}

    # Leave candidate in DB so UI browser can verify the incremented count.
    out = ROOT / 'test_reports' / 'scripts' / 'public_stats_backend_result_iter10.json'
    out.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(f'Wrote {out}')


if __name__ == '__main__':
    main()