from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def create_pdf(text: str, filepath: str):
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    text_obj = c.beginText(40, height - 40)
    text_obj.setFont("Helvetica", 10)

    for line in text.split("\n"):
        text_obj.textLine(line)

    c.drawText(text_obj)
    c.save()
    return filepath
