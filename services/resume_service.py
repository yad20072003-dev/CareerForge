from services.ai import ai_answer
from prompts.resume import PROMPT_RESUME

async def make_resume(user_data: str):
    return await ai_answer(PROMPT_RESUME, user_data)
