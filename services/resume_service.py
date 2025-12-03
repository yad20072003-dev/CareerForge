from services.ai import ai_answer
from prompts.resume import RESUME_CREATE_PROMPT


async def make_resume(user_text: str) -> str:
    return await ai_answer(
        system_prompt=RESUME_CREATE_PROMPT,
        user_prompt=user_text
    )
