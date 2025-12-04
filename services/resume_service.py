import os
from services.ai import ai_answer
from prompts.resume import RESUME_CREATE_PROMPT


async def make_resume(user_text: str) -> str:
    user_prompt = f"""
ДАННЫЕ ДЛЯ РЕЗЮМЕ:

{user_text}

Нужно сформировать готовый текст резюме под указанную должность.
Выдай результат в виде готового резюме, без лишних пояснений.
"""
    response = await ai_answer(
        system_prompt=RESUME_CREATE_PROMPT,
        user_prompt=user_prompt,
    )
    return response
