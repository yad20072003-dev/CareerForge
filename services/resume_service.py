from services.ai import ai_answer
from prompts.resume import RESUME_GENERATION_PROMPT


async def make_resume(payload: str) -> str:
    return await ai_answer(system_prompt=RESUME_GENERATION_PROMPT, user_prompt=payload)
