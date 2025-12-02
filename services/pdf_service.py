from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm

async def build_pdf(text: str, filepath: str):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm
    )

    style = ParagraphStyle(
        name="Main",
        fontName="Helvetica",
        fontSize=11,
        leading=15
    )

    story = []
    paragraphs = text.split("\n")

    for p in paragraphs:
        story.append(Paragraph(p, style))
        story.append(Spacer(1, 6 * mm))

    doc.build(story)
    return filepath
