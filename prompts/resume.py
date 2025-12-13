from .base import AI_INTELLECT_BOOSTER

RESUME_GENERATION_PROMPT = AI_INTELLECT_BOOSTER + """
Task: Generate a strong resume text in Russian, tailored to a target role.

Input will include:
- target role and level,
- contacts and city,
- experience description,
- education,
- skills,
- achievements/projects,
- extra details.

Goal:
Produce a resume that a recruiter can scan in 30–45 seconds and immediately understand:
- who the candidate is,
- what value they bring,
- why they fit the target role.

Rules:
- No invented facts. If dates, company names, metrics are missing, you may:
  a) keep them blank or replace with neutral placeholders like "Компания (уточнить)", or
  b) propose options as "Вариант формулировки" without stating them as facts.
- Use measurable outcomes if provided; if not, help the user convert outcomes into measurable formats by suggesting wording that does not invent numbers.

Mandatory structure:
1) Header
   - Name (if absent: "Имя Фамилия")
   - Target role title
   - City
   - Contacts
2) Positioning summary (3–5 sentences)
   - Role identity
   - 3 key strengths linked to the target role
   - Value proposition
3) Key skills
   - Hard skills (grouped)
   - Tools/tech (if relevant)
   - Soft skills (only those supported by input)
4) Experience
   For each role:
   - Period (if missing: "Период (уточнить)")
   - Company (if missing: "Компания (уточнить)")
   - Title
   - Responsibilities (3–6 bullets, action verbs)
   - Achievements (2–5 bullets, specific outcomes; avoid fluff)
5) Projects/Achievements block (optional if already included above)
6) Education
7) Additional
   - Languages, formats, links, portfolio

Quality bar:
- Wording must be modern, clear, market-ready.
- Avoid generic clichés ("стрессоустойчивый", "коммуникабельный") unless proven by examples.
- Avoid long paragraphs; use bullets.

Output only the final resume text, ready to copy-paste.
"""
