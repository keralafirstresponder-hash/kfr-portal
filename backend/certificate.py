"""Generate the Kerala First Responder certificate PDF by overlaying dynamic
fields (name, date, cert-id, training centre) on the branded template image.

The template already contains all logos (KFR shield, Aster Medcity, Wisdom4Future,
gold seal, tagline banner, signatures). We only need to blank the 4 sample text
areas and draw the new values in matching fonts."""

import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = Path(__file__).parent / "assets" / "cert_template.jpg"

# Fonts available on Debian/Ubuntu
FONT_NAME = "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"
FONT_LABEL = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_VALUE = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

CREAM = (238, 231, 217)
NAVY = (11, 27, 61)
GOLD = (196, 156, 60)


def build_certificate_pdf(name: str, cert_id: str, training_date: str, training_place: str) -> bytes:
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 1) Blank out the four dynamic value areas with the cream template colour
    #    Coordinates are for the 1222x864 template image.
    blanks = [
        (275, 385, 910, 472),   # Name + underline
        (332, 630, 510, 668),   # Date value
        (552, 630, 780, 668),   # Certificate ID value
        (785, 630, 1105, 668),  # Training centre value
    ]
    for box in blanks:
        draw.rectangle(box, fill=CREAM)

    # 2) Candidate name — large italic serif, navy, centred
    name_font = _fit_font(FONT_NAME, name, max_width=580, start_size=54, min_size=32)
    tw = _text_width(draw, name, name_font)
    name_x = 285 + (900 - 285 - tw) / 2
    name_y = 400
    draw.text((name_x, name_y), name, fill=NAVY, font=name_font)

    # Gold underline for name (matches template style)
    underline_y = 462
    draw.line([(305, underline_y), (880, underline_y)], fill=GOLD, width=2)

    # 3) Date / Cert ID / Centre values
    val_font = ImageFont.truetype(FONT_VALUE, 18)

    _draw_left(draw, training_date or "—", (338, 640), val_font, NAVY)
    _draw_left(draw, cert_id or "—", (558, 640), val_font, NAVY)

    # Training centre may be long — auto-shrink to fit width
    place = training_place or "Aster Medcity, Kochi"
    place_font = _fit_font(FONT_VALUE, place, max_width=310, start_size=18, min_size=11)
    _draw_left(draw, place, (790, 640), place_font, NAVY)

    # 4) Convert to PDF (single page)
    buf = io.BytesIO()
    img.save(buf, "PDF", resolution=150.0)
    return buf.getvalue()


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _fit_font(path: str, text: str, max_width: int, start_size: int, min_size: int) -> ImageFont.FreeTypeFont:
    size = start_size
    dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    while size > min_size:
        f = ImageFont.truetype(path, size)
        if _text_width(dummy, text, f) <= max_width:
            return f
        size -= 2
    return ImageFont.truetype(path, min_size)


def _draw_left(draw: ImageDraw.ImageDraw, text: str, pos, font, fill):
    draw.text(pos, text, fill=fill, font=font)
