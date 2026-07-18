import json, os, time, requests
BASE=os.environ.get('TEST_BASE_URL','https://responder-registry.preview.emergentagent.com').rstrip('/')
s=requests.Session(); out={'base':BASE}
r=s.post(BASE+'/api/auth/login',json={'email':'admin@kfr.org','password':'Kfr@2026'},timeout=30); r.raise_for_status(); s.headers['Authorization']='Bearer '+r.json()['token']
event=s.get(BASE+'/api/events',timeout=30).json()[0]
auth=s.headers.pop('Authorization')
try:
    label=int(time.time()*1000)
    payload={'name':f'QA Delete Candidate {label}','phone':'9999999999','email':f'qa_delete_{label}@example.com','dob':'1990-01-01','district':'Ernakulam','category':'Volunteer','organisation':'Aster Medcity','event_id':event['id']}
    reg=s.post(BASE+'/api/candidates/register',json=payload,timeout=30); reg.raise_for_status(); cid=reg.json()['candidate_id']
finally:
    s.headers['Authorization']=auth
out.update({'candidate_id':cid,'name':payload['name'],'email':payload['email']})
with open('/app/test_reports/delete_candidate_fixture.json','w') as f: json.dump(out,f,indent=2)
print(json.dumps(out,indent=2))
