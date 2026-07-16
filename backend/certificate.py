"""Generate the Kerala First Responder certificate PDF using ReportLab."""
import io
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm

NAVY = HexColor("#0B1B3D")
NAVY_LIGHT = HexColor("#1A2B56")
GOLD = HexColor("#D4AF37")
RED = HexColor("#E63946")
CREAM = HexColor("#FBF5E7")
WHITE = HexColor("#FFFFFF")
MUTED = HexColor("#64748B")


def build_certificate_pdf(name: str, cert_id: str, training_date: str, training_place: str) -> bytes:
    buf = io.BytesIO()
    W, H = landscape(A4)  # 842 x 595 pts
    c = canvas.Canvas(buf, pagesize=(W, H))

    # Cream background
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # Left navy panel
    c.setFillColor(NAVY)
    c.rect(0, 0, 130, H, stroke=0, fill=1)
    # Left panel gold triangle accent
    c.setFillColor(GOLD)
    p = c.beginPath()
    p.moveTo(130, H); p.lineTo(180, H); p.lineTo(130, H - 60); p.close()
    c.drawPath(p, stroke=0, fill=1)
    p2 = c.beginPath()
    p2.moveTo(130, 0); p2.lineTo(180, 0); p2.lineTo(130, 60); p2.close()
    c.drawPath(p2, stroke=0, fill=1)

    # Right red accent triangle
    c.setFillColor(RED)
    p3 = c.beginPath()
    p3.moveTo(W, H); p3.lineTo(W - 90, H); p3.lineTo(W, H - 60); p3.close()
    c.drawPath(p3, stroke=0, fill=1)
    c.setFillColor(GOLD)
    p4 = c.beginPath()
    p4.moveTo(W, 0); p4.lineTo(W - 90, 0); p4.lineTo(W, 60); p4.close()
    c.drawPath(p4, stroke=0, fill=1)

    # Left panel: vertical "BE A HERO. SAVE A LIFE."
    c.saveState()
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 20)
    c.translate(45, 90)
    c.rotate(90)
    c.drawString(0, 0, "BE A HERO.  SAVE A LIFE.")
    c.restoreState()

    # KFR shield placeholder in left panel
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.setFillColor(NAVY_LIGHT)
    c.roundRect(25, H - 165, 80, 100, 8, stroke=1, fill=1)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(65, H - 115, "KFR")
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(65, H - 130, "KERALA")
    c.drawCentredString(65, H - 140, "FIRST RESPONDER")

    # Top header row: Aster Medcity (left) + Wisdom4Future (right)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(160, H - 55, "Aster Medcity")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(160, H - 68, "MEDICAL PARTNER  •  We'll Treat You Well")

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Oblique", 8)
    c.drawRightString(W - 100, H - 45, "An Initiative by")
    c.setFillColor(HexColor("#007260"))
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(W - 100, H - 62, "WISDOM 4 FUTURE")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7)
    c.drawRightString(W - 100, H - 73, "Empowering Lives. Enriching Futures.")

    # Main title
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(W / 2 + 20, H - 115, "KERALA FIRST RESPONDER")

    # Tagline pill
    c.setFillColor(RED)
    c.roundRect(W / 2 - 155, H - 148, 350, 22, 4, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W / 2 + 20, H - 141, "COURAGE TO CARE, SKILL TO SAVE")

    # "CERTIFICATE"
    c.setFillColor(GOLD)
    c.setFont("Times-Bold", 30)
    c.drawCentredString(W / 2 + 20, H - 195, "CERTIFICATE")
    c.setFillColor(NAVY)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2 + 20, H - 213, "— OF COMPLETION —")

    # "This is to certify that"
    c.setFillColor(NAVY)
    c.setFont("Helvetica", 12)
    c.drawCentredString(W / 2 + 20, H - 245, "This is to certify that")

    # Candidate name — italic
    c.setFillColor(NAVY)
    c.setFont("Times-BoldItalic", 32)
    c.drawCentredString(W / 2 + 20, H - 285, name)

    # Underline for name
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    text_w = c.stringWidth(name, "Times-BoldItalic", 32)
    c.line(W / 2 + 20 - max(text_w, 320) / 2, H - 292, W / 2 + 20 + max(text_w, 320) / 2, H - 292)

    # Body text
    c.setFillColor(NAVY)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2 + 20, H - 315, "has successfully completed the Kerala First Responder (KFR)")
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W / 2 + 20, H - 330, "Training Program in CPR and Basic Life Support.")
    c.setFillColor(NAVY)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W / 2 + 20, H - 348, "We commend your dedication to learn life-saving skills")
    c.drawCentredString(W / 2 + 20, H - 361, "and your commitment to help save lives.")

    # Info row: Date | Cert ID | Place
    y_info = H - 405
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(180, y_info + 12, "DATE OF TRAINING")
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(180, y_info - 3, training_date or "—")

    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(370, y_info + 12, "CERTIFICATE ID")
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(370, y_info - 3, cert_id or "—")

    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(560, y_info + 12, "TRAINING CENTRE")
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(560, y_info - 3, training_place or "Aster Medcity, Kochi")

    # Gold seal top right area
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.setFillColor(NAVY)
    c.circle(W - 130, H - 240, 38, stroke=1, fill=1)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(W - 130, H - 232, "TRAINED TO")
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W - 130, H - 244, "RESPOND")
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(W - 130, H - 258, "READY TO SAVE")

    # Signatures
    y_sig = 90
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.8)
    positions = [
        (220, "Chairman & Managing Director", "Aster DM Healthcare"),
        (430, "CEO", "Aster Medcity"),
        (640, "Program Director", "Kerala First Responder (KFR)"),
    ]
    for x, title1, title2 in positions:
        c.line(x - 70, y_sig, x + 70, y_sig)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x, y_sig - 12, title1)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawCentredString(x, y_sig - 23, title2)

    # Bottom banner
    c.setFillColor(NAVY)
    c.rect(130, 0, W - 130, 40, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 9)
    tags = ["ALWAYS READY", "EVERY SECOND COUNTS", "COMMUNITY FIRST", "TRAINED TO SAVE"]
    spacing = (W - 130) / (len(tags) + 1)
    for i, t in enumerate(tags, start=1):
        c.drawCentredString(130 + spacing * i, 15, t)

    c.showPage()
    c.save()
    return buf.getvalue()
