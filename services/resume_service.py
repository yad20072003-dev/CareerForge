from services.ai import ai_answer
from prompts.resume import build_resume_prompt

async def make_resume(user_text: str) -> str:
    system_prompt = build_resume_prompt(user_text)
    result = await ai_answer(system_prompt, "")
    return result
