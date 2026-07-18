import json, os, time, requests
BASE=os.environ.get('TEST_BASE_URL','https://responder-registry.preview.emergentagent.com').rstrip('/')
s=requests.Session()
out={'base':BASE,'tokens':{},'candidate_ids':{}}
r=s.post(BASE+'/api/auth/login',json={'email':'admin@kfr.org','password':'Kfr@2026'},timeout=30)
r.raise_for_status(); s.headers['Authorization']='Bearer '+r.json()['token']
events=s.get(BASE+'/api/events',timeout=30).json(); event_id=events[0]['id']
for label in ['ui_en','ui_ml','ui_ml_submit']:
    auth=s.headers.pop('Authorization')
    try:
        payload={'name':f'QA {label} Candidate','phone':'9999999999','email':f'qa_{label}_{int(time.time()*1000)}@example.com','dob':'1990-01-01','district':'Ernakulam','category':'Volunteer','organisation':'Aster Medcity','event_id':event_id}
        reg=s.post(BASE+'/api/candidates/register',json=payload,timeout=30); reg.raise_for_status(); cid=reg.json()['candidate_id']
    finally:
        s.headers['Authorization']=auth
    gen=s.post(BASE+'/api/admin/generate-test',json={'candidate_ids':[cid]},timeout=30); gen.raise_for_status()
    cands=s.get(BASE+'/api/candidates',timeout=30).json(); cand=next(c for c in cands if c['id']==cid)
    out['tokens'][label]=cand['test_token']; out['candidate_ids'][label]=cid
with open('/app/test_reports/ui_pending_tokens.json','w') as f: json.dump(out,f,indent=2)
print(json.dumps(out,indent=2))
