import os, json, uuid, requests, fitz
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL') or 'https://responder-registry.preview.emergentagent.com'
API = BASE_URL.rstrip('/') + '/api'
OUT = Path('/app/test_reports/bug_assets')
OUT.mkdir(parents=True, exist_ok=True)
ADMIN_EMAIL='admin@kfr.org'
ADMIN_PW='Kfr@2026'

result = {'api': API, 'steps': []}
def step(name, ok, details=None):
    result['steps'].append({'name': name, 'ok': bool(ok), 'details': details or {}})
    print(f"{name}: {'OK' if ok else 'FAIL'} {details or ''}")

s = requests.Session()
# Login
r = s.post(f'{API}/auth/login', json={'email': ADMIN_EMAIL, 'password': ADMIN_PW}, timeout=30)
step('admin_login', r.status_code == 200, {'status': r.status_code, 'body': r.text[:200]})
r.raise_for_status()
token = r.json()['token']
h = {'Authorization': f'Bearer {token}'}
# Reference data
r = s.get(f'{API}/events', timeout=30); step('list_events', r.status_code == 200 and len(r.json())>0, {'status': r.status_code, 'count': len(r.json()) if r.ok else None}); r.raise_for_status(); event = r.json()[0]
r = s.get(f'{API}/questions', headers=h, timeout=30); step('admin_questions', r.status_code == 200 and len(r.json())>=10, {'status': r.status_code, 'count': len(r.json()) if r.ok else None}); r.raise_for_status(); all_questions = r.json(); correct = {q['id']: q['correct_key'] for q in all_questions}
# Register a fresh candidate with a distinctive dynamic name and place/date from event.
unique = uuid.uuid4().hex[:8]
name = f'QA Branding {unique}'
email = f'qa_branding_{unique}@example.com'
payload = {'name': name, 'phone': '9876512345', 'email': email, 'dob': '1993-07-16', 'district': 'Ernakulam', 'category': 'Student', 'organisation': 'Aster Medcity', 'event_id': event['id']}
r = s.post(f'{API}/candidates/register', json=payload, timeout=30)
step('candidate_register', r.status_code == 200, {'status': r.status_code, 'body': r.text[:200], 'name': name, 'event': event})
r.raise_for_status(); cid = r.json()['candidate_id']
# Generate test link
r = s.post(f'{API}/admin/generate-test', json={'candidate_ids':[cid]}, headers=h, timeout=60)
step('generate_test', r.status_code == 200, {'status': r.status_code, 'body': r.text[:200]}); r.raise_for_status()
# Read candidate token
r = s.get(f'{API}/candidates', headers=h, timeout=30); r.raise_for_status(); cand = next(c for c in r.json() if c['id']==cid); test_token = cand['test_token']
step('candidate_has_pending_token', cand['test_status']=='pending' and bool(test_token), {'status': cand['test_status'], 'token_len': len(test_token)})
# Open test and submit all correct answers
r = s.get(f'{API}/test/{test_token}', timeout=30); step('get_test', r.status_code == 200 and r.json().get('status')=='active', {'status': r.status_code}); r.raise_for_status(); qs = r.json()['questions']
answers = {q['id']: correct[q['id']] for q in qs}
r = s.post(f'{API}/test/{test_token}/submit', json={'answers': answers}, timeout=30)
step('submit_pass', r.status_code == 200 and r.json().get('passed') is True, {'status': r.status_code, 'body': r.text[:200]}); r.raise_for_status(); cert_id = r.json()['certificate_id']
# Cert info
r = s.get(f'{API}/certificate/{test_token}', timeout=30)
step('cert_info', r.status_code == 200 and r.json().get('candidate_name') == name and r.json().get('certificate_id') == cert_id, {'status': r.status_code, 'body': r.text[:300]}); r.raise_for_status(); cert_info = r.json()
# Download PDF
r = s.get(f'{API}/certificate/{test_token}/pdf', timeout=30)
pdf_path = OUT / f'generated_certificate_{unique}.pdf'
pdf_path.write_bytes(r.content)
step('cert_pdf_download', r.status_code == 200 and r.headers.get('content-type','').startswith('application/pdf') and r.content.startswith(b'%PDF'), {'status': r.status_code, 'content_type': r.headers.get('content-type'), 'bytes': len(r.content), 'path': str(pdf_path)})
# Render PDF to PNG for visual inspection.
doc = fitz.open(stream=r.content, filetype='pdf')
page = doc[0]
pix = page.get_pixmap(matrix=fitz.Matrix(2,2), alpha=False)
png_path = OUT / f'generated_certificate_{unique}.png'
pix.save(str(png_path))
step('render_pdf_png', png_path.exists(), {'path': str(png_path), 'width': pix.width, 'height': pix.height})
# Crop dynamic fields for close visual check.
img = Image.open(png_path).convert('RGB')
# The 2x render is approximately 1222x864 points rendered 2x? Use scale based on template coordinate mapping.
sx = img.width / 1222
sy = img.height / 864
crop_boxes = {
    'name_field': (275,385,910,472),
    'date_field': (315,610,520,680),
    'cert_id_field': (530,610,790,680),
    'place_field': (770,610,1120,680),
    'kfr_logo': (0,0,265,270),
    'partner_logos_top': (280,40,1160,125),
    'gold_seal_and_cpr_photo': (850,220,1210,630),
    'bottom_banner': (170,780,1120,860),
    'vertical_be_hero': (0,610,220,740),
}
for label, b in crop_boxes.items():
    rb = tuple(int(v*sx if i%2==0 else v*sy) for i,v in enumerate(b))
    Image.open(png_path).convert('RGB').crop(rb).save(OUT / f'{label}_{unique}.png')
# Compare generated rendered image against original template outside blanked dynamic areas (proves full branded sample template remains as background).
template_path = Path('/app/backend/assets/cert_template.jpg')
template = Image.open(template_path).convert('RGB').resize(img.size)
mask = Image.new('L', img.size, 255)
# zero out dynamic rectangles + small expanded padding
from PIL import ImageDraw
draw = ImageDraw.Draw(mask)
for b in [(260,370,930,485),(310,610,525,685),(530,610,795,685),(765,610,1130,685)]:
    rb = tuple(int(v*sx if i%2==0 else v*sy) for i,v in enumerate(b))
    draw.rectangle(rb, fill=0)
diff = ImageChops.difference(img, template)
stat = ImageStat.Stat(diff, mask)
mean_diff = sum(stat.mean)/3
step('background_matches_template_outside_dynamic_fields', mean_diff < 8, {'mean_rgb_abs_diff': mean_diff})
result.update({'candidate_id': cid, 'test_token': test_token, 'dynamic_values': {'candidate_name': name, 'cert_id': cert_id, 'training_date': event.get('training_date'), 'training_place': event.get('place')}, 'cert_info': cert_info, 'pdf_path': str(pdf_path), 'png_path': str(png_path), 'crop_dir': str(OUT)})
(OUT / f'certificate_flow_result_{unique}.json').write_text(json.dumps(result, indent=2))
Path('/app/test_reports/certificate_branding_latest.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
