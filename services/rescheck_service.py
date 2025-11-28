from services.ai import ai_answer
from prompts.rescheck import PROMPT_RESCHECK

async def check_resume(resume_text: str):
    return await ai_answer(PROMPT_RESCHECK, resume_text)
