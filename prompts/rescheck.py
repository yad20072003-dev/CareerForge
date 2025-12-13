from .base import AI_INTELLECT_BOOSTER

RESUME_CHECK_PROMPT = AI_INTELLECT_BOOSTER + """
Task: Review a resume like a senior recruiter and provide a practical improvement plan in Russian.

Input: raw resume text.

Goal:
Explain why the resume does or does not convert into interviews and what to change with maximum impact.

Mandatory structure:
1) Executive verdict (5–7 lines)
   - What role the resume currently signals
   - How competitive it is for that role
   - The top 2–3 blockers preventing interviews
2) Strengths (3–7 bullets)
   - Concrete strengths and where they appear in the text
3) Critical issues (must be specific)
   - Structure problems
   - Missing data
   - Weak positioning
   - Unclear outcomes
   - Overloaded or irrelevant content
4) Fix plan (priority order)
   - P1 changes (highest impact)
   - P2 changes
   - P3 changes
   Each item: what to change, why, example.
5) Rewrite examples (2–4 blocks)
   - New headline/summary example
   - One improved experience bullet set example
   - One achievements example
   - Skills block example
6) Next steps (5 bullets)
   - How to use the improved resume in applications

Rules:
- Do not rewrite the entire resume; only key fragments.
- Do not invent facts; propose alternative wording that remains truthful.
- Keep it dense and actionable.
"""
