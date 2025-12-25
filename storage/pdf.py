import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def build_pdf(path: str, title: str, blocks: dict, footer: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path)
    content = []

    content.append(Paragraph(str(title or "").strip() or "Отчёт", styles["Title"]))
    content.append(Spacer(1, 12))

    def add_section(header: str, body):
        text = "" if body is None else str(body).strip()
        if not text:
            return
        content.append(Paragraph(str(header), styles["Heading2"]))
        content.append(Paragraph(text.replace("\n", "<br/>"), styles["BodyText"]))
        content.append(Spacer(1, 10))

    add_section("HR-вердикт", blocks.get("verdict") if isinstance(blocks, dict) else "")
    add_section("Оценка", blocks.get("score_text") if isinstance(blocks, dict) else "")
    add_section("Итог", blocks.get("summary") if isinstance(blocks, dict) else "")
    add_section("Сильные стороны", blocks.get("strengths") if isinstance(blocks, dict) else "")
    add_section("Риски", blocks.get("risks") if isinstance(blocks, dict) else "")
    add_section("Рекомендации", blocks.get("recommendations") if isinstance(blocks, dict) else "")
    add_section("Следующие шаги", blocks.get("next_steps") if isinstance(blocks, dict) else "")
    add_section("Диалог", blocks.get("transcript") if isinstance(blocks, dict) else "")

    if footer:
        content.append(Spacer(1, 12))
        content.append(Paragraph(str(footer).strip().replace("\n", "<br/>"), styles["BodyText"]))

    doc.build(content)
