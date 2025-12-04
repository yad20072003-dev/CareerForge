import os
from services.ai import ai_answer
from prompts.plan import INTERVIEW_PLAN_PROMPT


async def interview_plan(user_text: str) -> str:
    user_prompt = f"""
ДАННЫЕ О СОБЕСЕДОВАНИИ И КАНДИДАТЕ:

{user_text}

Сформируй подробный план поведения на собеседовании по структуре из системного промта.
"""
    response = await ai_answer(
        system_prompt=INTERVIEW_PLAN_PROMPT,
        user_prompt=user_prompt,
    )
    return response
