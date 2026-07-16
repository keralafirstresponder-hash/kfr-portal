import os, uuid, json, requests
from pathlib import Path
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL') or 'https://responder-registry.preview.emergentagent.com'
API = BASE_URL.rstrip() + '/api'
s = requests.Session()
r = s.post(f'{API}/auth/login', json={'email':'admin@kfr.org','password':'Kfr@2026'}, timeout=30); r.raise_for_status(); h={'Authorization': 'Bearer '+r.json()['token']}
events = s.get(f'{API}/events', timeout=30).json(); event=events[0]
unique = uuid.uuid4().hex[:8]
payload={'name':f'QA Nav Token {unique}','phone':'9876501234','email':f'qa_nav_{unique}@example.com','dob':'1990-01-01','district':'Ernakulam','category':'Student','organisation':'Aster Medcity','event_id':event['id']}
r=s.post(f'{API}/candidates/register', json=payload, timeout=30); r.raise_for_status(); cid=r.json()['candidate_id']
r=s.post(f'{API}/admin/generate-test', json={'candidate_ids':[cid]}, headers=h, timeout=60); r.raise_for_status()
cs=s.get(f'{API}/candidates', headers=h, timeout=30).json(); cand=next(c for c in cs if c['id']==cid)
out={'candidate_id':cid,'test_token':cand['test_token'],'name':payload['name'],'api':API}
Path('/app/test_reports/pending_test_token.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out))
