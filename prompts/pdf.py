import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from datetime import datetime

OUTPUT_DIR = "generated_pdfs"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def generate_pdf(title: str, content: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = title.replace(" ", "_").replace("/", "_")
    filename = f"{OUTPUT_DIR}/{safe_title}_{timestamp}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Heading1"],
        alignment=TA_LEFT,
        fontSize=18,
        spaceAfter=16,
    )
    body_style = ParagraphStyle(
        name="BodyStyle",
        parent=styles["Normal"],
        alignment=TA_LEFT,
        fontSize=11,
        leading=15,
        spaceAfter=12,
    )

    story = [
        Paragraph(title, title_style),
        Spacer(1, 12),
    ]

    for block in content.split("\n"):
        block = block.strip()
        if not block:
            story.append(Spacer(1, 6))
            continue
        story.append(Paragraph(block, body_style))

    doc.build(story)
    return filename
