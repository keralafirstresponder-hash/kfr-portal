import json
from pathlib import Path
from PIL import Image, ImageChops, ImageStat, ImageDraw

meta = json.loads(Path('/app/test_reports/certificate_branding_latest.json').read_text())
img = Image.open(meta['png_path']).convert('RGB')
template = Image.open('/app/backend/assets/cert_template.jpg').convert('RGB').resize(img.size)
sx = img.width / 1222
sy = img.height / 864
# Same approximate dynamic regions used in previous verification, but check each region separately.
regions = {
    'name': (260,370,930,485),
    'date': (310,610,525,685),
    'cert_id': (530,610,795,685),
    'training_centre': (765,610,1130,685),
}
results = {}
for name, box in regions.items():
    rb = tuple(int(v*sx if i % 2 == 0 else v*sy) for i, v in enumerate(box))
    gen_crop = img.crop(rb)
    tpl_crop = template.crop(rb)
    # detect flat/white rectangle symptom: large near-white pixels in generated crop compared to template.
    pixels = list(gen_crop.getdata())
    near_white_ratio = sum(1 for p in pixels if min(p) >= 245) / len(pixels)
    # texture still present: non-zero channel variation in generated crop.
    st = ImageStat.Stat(gen_crop)
    texture_std = sum(st.stddev) / 3
    # Compare only non-text/gold pixels by excluding dark and saturated line pixels in generated crop.
    mask = Image.new('L', gen_crop.size, 255)
    md = ImageDraw.Draw(mask)
    # Build mask pixel-wise: 0 for dynamic text/underline, 255 for surrounding background.
    mask_pixels = []
    for p in pixels:
        r,g,b = p
        # exclude navy text and gold/red-ish underline/icons to focus on background around values
        is_dynamic_or_graphic = (max(p) < 120) or (b < 120 and r > 120 and g > 80) or (r > 100 and g < 100 and b < 100)
        mask_pixels.append(0 if is_dynamic_or_graphic else 255)
    mask.putdata(mask_pixels)
    diff = ImageChops.difference(gen_crop, tpl_crop)
    stat = ImageStat.Stat(diff, mask)
    bg_mean_diff = sum(stat.mean)/3
    results[name] = {
        'box': rb,
        'near_white_ratio': round(near_white_ratio, 4),
        'texture_stddev_avg': round(texture_std, 3),
        'background_mean_rgb_abs_diff_excluding_text': round(bg_mean_diff, 3),
        'passes_no_flat_white_box_check': near_white_ratio < 0.70 and texture_std > 8
    }

ok = all(r['passes_no_flat_white_box_check'] for r in results.values())
out = {'png_path': meta['png_path'], 'pdf_path': meta['pdf_path'], 'results': results, 'overall_pass': ok}
Path('/app/test_reports/certificate_no_white_boxes_iter5.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
if not ok:
    raise SystemExit(1)
