import os
from services.ai import ai_answer
from prompts.soft import SOFT_ANALYSIS_PROMPT


async def soft_analysis(user_text: str) -> str:
    user_prompt = f"""
ОПИСАНИЕ СИТУАЦИЙ И ПОВЕДЕНИЯ ПОЛЬЗОВАТЕЛЯ:

{user_text}

Нужно провести анализ soft skills по структуре из системного промта.
"""
    response = await ai_answer(
        system_prompt=SOFT_ANALYSIS_PROMPT,
        user_prompt=user_prompt,
    )
    return response
