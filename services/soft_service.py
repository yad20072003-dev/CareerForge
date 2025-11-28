from services.ai import ai_answer
from prompts.soft import PROMPT_SOFT

async def soft_analysis(user_data: str):
    return await ai_answer(PROMPT_SOFT, user_data)
