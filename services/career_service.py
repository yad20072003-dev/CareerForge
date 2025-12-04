import os
from services.ai import ai_answer
from prompts.career import CAREER_SYSTEM_PROMPT


async def make_career_report(user_text: str) -> str:
    return await ai_answer(
        system_prompt=CAREER_SYSTEM_PROMPT,
        user_prompt=user_text
    )
