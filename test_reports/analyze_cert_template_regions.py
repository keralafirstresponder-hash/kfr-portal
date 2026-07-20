from pathlib import Path
from PIL import Image, ImageDraw
import json

ROOT = Path('/app')
orig = Image.open(ROOT / 'backend/assets/cert_template.jpg').convert('RGB')
clean = Image.open(ROOT / 'backend/assets/cert_template_clean.jpg').convert('RGB')

# Approximate user-reported regions on the 1222x864 certificate template.
regions = {
    'info_row_full': (280, 560, 1080, 665),
    'date_icon': (300, 580, 355, 638),
    'cert_id_icon': (520, 580, 575, 638),
    'training_centre_icon': (750, 580, 815, 638),
    'middle_signature': (500, 655, 770, 810),
    'left_signature': (280, 655, 505, 810),
    'right_signature': (770, 655, 1045, 810),
}

def blue_count(im, box):
    crop = im.crop(box)
    cnt = 0
    strong = 0
    for r, g, b in crop.getdata():
        if b > r + 25 and b > g + 5 and b > 80:
            cnt += 1
        if b > r + 45 and b > g + 15 and b > 110:
            strong += 1
    return cnt, strong, crop.size[0] * crop.size[1]

def dark_count(im, box):
    crop = im.crop(box)
    return sum(1 for r, g, b in crop.getdata() if r < 100 and g < 100 and b < 130), crop.size[0] * crop.size[1]

out = {}
for name, box in regions.items():
    out[name] = {
        'box': box,
        'orig_blue': blue_count(orig, box),
        'clean_blue': blue_count(clean, box),
        'orig_dark': dark_count(orig, box),
        'clean_dark': dark_count(clean, box),
    }

Path('/app/test_reports/cert_template_region_analysis.json').write_text(json.dumps(out, indent=2))

# Build a visual contact sheet for manual inspection (not referenced as report link).
thumbs = []
for name, box in regions.items():
    if name in ('date_icon', 'cert_id_icon', 'training_centre_icon', 'middle_signature', 'left_signature', 'right_signature'):
        o = orig.crop(box).resize(((box[2]-box[0])*2, (box[3]-box[1])*2))
        c = clean.crop(box).resize(((box[2]-box[0])*2, (box[3]-box[1])*2))
        thumbs.append((name + ' original', o))
        thumbs.append((name + ' clean', c))

w = max(t[1].width for t in thumbs)
h = sum(t[1].height + 28 for t in thumbs)
sheet = Image.new('RGB', (w + 260, h), 'white')
d = ImageDraw.Draw(sheet)
y = 0
for label, im in thumbs:
    d.text((5, y + 5), label, fill=(0, 0, 0))
    sheet.paste(im, (250, y))
    y += im.height + 28
sheet.save('/app/test_reports/cert_template_region_contact_sheet.jpg', quality=80)
print(json.dumps(out, indent=2))