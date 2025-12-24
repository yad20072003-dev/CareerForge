from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

def make(path, title, data):
    os.makedirs("data", exist_ok=True)
    s = getSampleStyleSheet()
    doc = SimpleDocTemplate(path)
    story = [Paragraph(title, s["Title"])]
    for k,v in data.items():
        if v:
            story.append(Paragraph(k.upper(), s["Heading2"]))
            story.append(Paragraph(str(v).replace("\n","<br/>"), s["BodyText"]))
    doc.build(story)
