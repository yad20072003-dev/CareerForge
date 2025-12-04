import os
from services.ai import ai_answer
from prompts.rescheck import RESUME_CHECK_PROMPT


async def check_resume(resume_text: str) -> str:
    user_prompt = f"""
ТЕКСТ РЕЗЮМЕ:

{resume_text}

Разбери резюме по структуре из системного промта и предложи улучшения.
"""
    response = await ai_answer(
        system_prompt=RESUME_CHECK_PROMPT,
        user_prompt=user_prompt,
    )
    return response
