import os
from services.ai import ai_answer
from prompts.career import CAREER_ANALYSIS_PROMPT


async def make_career_report(user_text: str) -> str:
    user_prompt = f"""
ДАННЫЕ ПОЛЬЗОВАТЕЛЯ:

{user_text}

Сформируй полный карьерный разбор по заданной структуре.
"""
    response = await ai_answer(
        system_prompt=CAREER_ANALYSIS_PROMPT,
        user_prompt=user_prompt,
    )
    return response
