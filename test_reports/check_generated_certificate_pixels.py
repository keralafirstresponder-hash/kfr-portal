import json
from pathlib import Path
from PIL import Image, ImageStat
# Quick quantitative check that important branded regions in rendered cert are non-blank/colourful.
meta = json.loads(Path('/app/test_reports/certificate_branding_latest.json').read_text())
img = Image.open(meta['png_path']).convert('RGB')
sx = img.width / 1222
sy = img.height / 864
regions = {
  'kfr_shield': (15,25,245,260),
  'aster_logo': (285,45,435,115),
  'wisdom_logo': (940,45,1180,115),
  'gold_seal': (930,220,1080,360),
  'cpr_photo': (815,350,1200,610),
  'signatures': (290,665,940,735),
  'vertical_be_hero': (20,610,170,725),
  'bottom_banner': (180,790,1100,855),
}
out={}
for name,b in regions.items():
    rb=tuple(int(v*sx if i%2==0 else v*sy) for i,v in enumerate(b))
    crop=img.crop(rb)
    st=ImageStat.Stat(crop)
    out[name]={'mean':st.mean,'stddev':st.stddev, 'loaded_nonblank': sum(st.stddev)/3 > 5}
print(json.dumps(out, indent=2))
Path('/app/test_reports/certificate_region_pixel_checks.json').write_text(json.dumps(out, indent=2))
