import os
from services.ai import ai_answer
from prompts.rescheck import RESCHECK_SYSTEM_PROMPT


async def check_resume(text: str) -> str:
    return await ai_answer(
        system_prompt=RESCHECK_SYSTEM_PROMPT,
        user_prompt=text
    )
