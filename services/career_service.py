from services.ai import ai_answer
from prompts.career import PROMPT_CAREER

async def make_career_report(user_data: str):
    return await ai_answer(PROMPT_CAREER, user_data)
