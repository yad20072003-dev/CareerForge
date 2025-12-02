from services.ai import ai_answer
from prompts.rescheck import build_rescheck_prompt

async def check_resume(user_text: str) -> str:
    system_prompt = build_rescheck_prompt(user_text)
    result = await ai_answer(system_prompt, "")
    return result
