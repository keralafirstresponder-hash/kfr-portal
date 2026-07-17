"""Generate the Kerala First Responder certificate PDF by overlaying dynamic
fields (name, date, cert-id, training centre) on the branded template image.

The template already contains all logos (KFR shield, Aster Medcity, Wisdom4Future,
gold seal, tagline banner, signatures). We only need to blank the 4 sample text
areas and draw the new values in matching fonts.

Instead of filling with a flat cream, we copy clean background patches from the
template itself so the paper texture flows through the dynamic-field region."""

import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = Path(__file__).parent / "assets" / "cert_template.jpg"

FONT_NAME = "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"
FONT_VALUE = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

NAVY = (11, 27, 61)
GOLD = (196, 156, 60)

# Blank targets on the 1222x864 template (left, top, right, bottom)
NAME_BOX = (275, 385, 910, 472)
DATE_BOX = (332, 630, 510, 668)
CERT_BOX = (552, 630, 780, 668)
PLACE_BOX = (785, 630, 1105, 668)

# Clean-background strips to sample from (same X-range as target, clean Y-range)
# y=340..360 is clean cream above "This is to certify that"
NAME_SRC_Y = (340, 360)
# y=575..595 is clean cream just below the body paragraph, before the label icons
VALUE_SRC_Y = (575, 593)


def build_certificate_pdf(name: str, cert_id: str, training_date: str, training_place: str) -> bytes:
    img = Image.open(TEMPLATE_PATH).convert("RGB")

    # 1) Cover sample text by pasting sampled background patches (preserves texture)
    _cover_with_texture(img, NAME_BOX, NAME_SRC_Y)
    _cover_with_texture(img, DATE_BOX, VALUE_SRC_Y)
    _cover_with_texture(img, CERT_BOX, VALUE_SRC_Y)
    _cover_with_texture(img, PLACE_BOX, VALUE_SRC_Y)

    draw = ImageDraw.Draw(img)

    # 2) Candidate name — large italic serif, navy, centred + gold underline
    name_font = _fit_font(FONT_NAME, name, max_width=580, start_size=54, min_size=32)
    tw = _text_width(draw, name, name_font)
    name_x = 285 + (900 - 285 - tw) / 2
    draw.text((name_x, 400), name, fill=NAVY, font=name_font)
    draw.line([(305, 462), (880, 462)], fill=GOLD, width=2)

    # 3) Date / Cert ID / Centre values
    val_font = ImageFont.truetype(FONT_VALUE, 18)
    draw.text((338, 640), training_date or "—", fill=NAVY, font=val_font)
    draw.text((558, 640), cert_id or "—", fill=NAVY, font=val_font)
    place = training_place or "Aster Medcity, Kochi"
    place_font = _fit_font(FONT_VALUE, place, max_width=310, start_size=18, min_size=11)
    draw.text((790, 640), place, fill=NAVY, font=place_font)

    # 4) Convert to PDF (single page)
    buf = io.BytesIO()
    img.save(buf, "PDF", resolution=150.0)
    return buf.getvalue()


def _cover_with_texture(img: Image.Image, target_box, src_y_range):
    """Fill target_box (l,t,r,b) with a texture patch sampled from the same X-range
    but a clean Y band. Repeats the source strip vertically until the target is filled."""
    l, t, r, b = target_box
    src_top, src_bottom = src_y_range
    src_strip = img.crop((l, src_top, r, src_bottom))  # same width as target
    strip_h = src_bottom - src_top

    y = t
    while y < b:
        remaining = b - y
        if remaining >= strip_h:
            img.paste(src_strip, (l, y))
            y += strip_h
        else:
            # Paste only the top `remaining` px of the strip
            img.paste(src_strip.crop((0, 0, r - l, remaining)), (l, y))
            break


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
