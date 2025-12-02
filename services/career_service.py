from services.ai import ai_answer
from prompts.career import build_career_prompt

async def make_career_report(user_text: str) -> str:
    system_prompt = build_career_prompt(user_text)
    result = await ai_answer(system_prompt, "")
    return result
