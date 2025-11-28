from services.ai import ai_answer
from prompts.plan import PROMPT_PLAN

async def interview_plan(user_data: str):
    return await ai_answer(PROMPT_PLAN, user_data)
