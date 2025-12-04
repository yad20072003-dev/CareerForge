import os
from services.ai import ai_answer
from prompts.courses import COURSES_PROMPT


async def course_recommendations(user_text: str) -> str:
    user_prompt = f"""
ДАННЫЕ О ТЕКУЩЕМ УРОВНЕ И ЦЕЛЯХ:

{user_text}

Сформируй рекомендации по обучению и мини-проектам по структуре из системного промта.
"""
    response = await ai_answer(
        system_prompt=COURSES_PROMPT,
        user_prompt=user_prompt,
    )
    return response
