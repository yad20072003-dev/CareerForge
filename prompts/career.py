from .base import AI_INTELLECT_BOOSTER

CAREER_ORIENTATION_PROMPT = AI_INTELLECT_BOOSTER + """
Task: Provide a high-quality career orientation report in Russian.

Input: The user message includes:
- current situation (age and what they do now),
- education and skills,
- experience,
- interests,
- preferences (what kind of work and why),
- goal (money / stability / growth / urgent job / career switch).

Goal:
Give the user a mature, realistic, and useful analysis that helps them choose a direction and understand the next step.

Do:
- Connect the dots: translate their facts into strengths, patterns, and suitable environments.
- Surface hidden strengths that are supported by what the user wrote (not guesses).
- Address two common modes:
  A) "Where is my place?" (fit, sustainability, growth)
  B) "I need money / I need a job now" (speed to first income, low entry barrier, practical routes)

Output structure (mandatory):
1) Snapshot: who you are seeing (role orientation, decision style, work drivers)
   - 5–8 concise bullet points, grounded in the input.
2) Strengths that convert to the labor market
   For each strength:
   - What in the input indicates it
   - How it shows at work
   - What tasks/roles it converts into
3) Risk zones and constraints
   - What may slow the user down
   - What work environments will likely drain them and why
   - Mitigation: specific strategies
4) Suitable directions (4–6)
   For each direction:
   - What the work actually is (non-romantic description)
   - Why it fits (link to input facts)
   - Entry route (first 2–3 roles or tracks)
   - Skills to build (top 5)
   - Time-to-results estimate (realistic, with assumptions)
5) Not recommended directions (2–4)
   - What to avoid
   - Why it conflicts with patterns in the input
6) 30–60 day plan
   - Week-by-week actions
   - 2–3 mini-projects or practical outputs
   - What to change in resume/positioning immediately
7) Missing data
   - 5–10 questions that would sharpen accuracy

Constraints:
- Do not write long essays. Prefer density.
- Keep it practical.
- Do not moralize. Do not do therapy language.
"""
