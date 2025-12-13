from .base import AI_INTELLECT_BOOSTER

VACANCY_ANALYSIS_PROMPT = AI_INTELLECT_BOOSTER + """
Task: Analyze a vacancy vs candidate profile and produce a practical match report in Russian.

Input includes:
- vacancy text,
- candidate profile (short description of experience).

Goal:
Help the user decide:
- whether to apply,
- how to position themselves,
- what to fix in resume and interview to improve odds.

Mandatory structure:
1) Vacancy decoding
   - What the role actually wants (5–10 bullets)
   - Hidden priorities (inferences allowed, but label them and justify)
2) Fit map
   - Strong matches (with evidence from candidate profile)
   - Partial matches (what is missing and how to compensate)
   - Red flags for this vacancy (risks and how to address)
3) Resume targeting plan
   - What to emphasize (skills, cases, keywords)
   - What to de-emphasize
   - 6–12 ready-to-use bullet formulations (truthful, no invented facts)
4) Interview targeting plan
   - 6–10 likely questions based on vacancy
   - For each: what angle to take, what proof to use
5) Quick skill gap plan (14–30 days)
   - Only practical actions
6) Decision
   - Apply / apply with changes / skip
   - Short justification

Rules:
- No invented facts.
- No generic advice; make it vacancy-specific.
- Keep it realistic.
"""
