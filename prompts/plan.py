from .base import AI_INTELLECT_BOOSTER

INTERVIEW_PLAN_PROMPT = AI_INTELLECT_BOOSTER + """
Task: Create a behavior and preparation plan for an interview in Russian.

Input: role, company/industry, user's experience, strengths, fears, and goal.

Output structure:
1) Interview strategy
   - Tone, positioning, and what to lead with
2) Core story
   - 60-second self-intro script
   - 3 key strengths with proof
3) Questions you must be ready for (8–12)
   For each:
   - best structure of answer
   - what evidence to cite
   - common mistake to avoid
4) Risk management
   - weak spots the interviewer may probe
   - how to answer without lying
5) Questions to ask employer (10–15)
   - grouped by: role clarity, team/processes, metrics, growth, risks
6) 24-hour prep checklist
7) Short final summary (5 bullets)

Rules:
- No promises, no therapy language.
- Make it specific to the role.
- Provide ready-to-use wording.
"""
