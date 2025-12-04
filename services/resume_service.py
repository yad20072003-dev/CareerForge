import os
from services.ai import ai_answer
from prompts.resume import RESUME_SYSTEM_PROMPT


async def make_resume(user_text: str) -> str:
    return await ai_answer(
        system_prompt=RESUME_SYSTEM_PROMPT,
        user_prompt=user_text
    )
