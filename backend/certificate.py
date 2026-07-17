"""Generate the Kerala First Responder certificate PDF by overlaying dynamic
fields on a pre-cleaned template image.

The clean template (`cert_template_clean.jpg`) has all sample text removed via
OpenCV inpainting, so we simply draw the new values on top — no rectangles,
no patches, no visible modifications to the background."""

import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = Path(__file__).parent / "assets" / "cert_template_clean.jpg"

FONT_NAME = "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"
FONT_VALUE = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

NAVY = (11, 27, 61)
GOLD = (196, 156, 60)


def build_certificate_pdf(name: str, cert_id: str, training_date: str, training_place: str) -> bytes:
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Candidate name — large italic serif, navy, centred + gold underline
    name_font = _fit_font(FONT_NAME, name, max_width=580, start_size=54, min_size=32)
    tw = _text_width(draw, name, name_font)
    name_x = 285 + (900 - 285 - tw) / 2
    draw.text((name_x, 400), name, fill=NAVY, font=name_font)
    draw.line([(305, 462), (880, 462)], fill=GOLD, width=2)

    # Date / Cert ID / Centre values
    val_font = ImageFont.truetype(FONT_VALUE, 18)
    draw.text((338, 640), training_date or "—", fill=NAVY, font=val_font)
    draw.text((558, 640), cert_id or "—", fill=NAVY, font=val_font)
    place = training_place or "Aster Medcity, Kochi"
    place_font = _fit_font(FONT_VALUE, place, max_width=310, start_size=18, min_size=11)
    draw.text((790, 640), place, fill=NAVY, font=place_font)

    buf = io.BytesIO()
    img.save(buf, "PDF", resolution=150.0)
    return buf.getvalue()


def _text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _fit_font(path, text, max_width, start_size, min_size):
    size = start_size
    dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    while size > min_size:
        f = ImageFont.truetype(path, size)
        if _text_width(dummy, text, f) <= max_width:
            return f
        size -= 2
    return ImageFont.truetype(path, min_size)
