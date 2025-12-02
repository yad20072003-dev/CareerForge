from services.ai import ai_answer
from prompts.plan import build_plan_prompt

async def interview_plan(user_text: str) -> str:
    prompt = build_plan_prompt(user_text)
    result = await ai_answer(prompt, "")
    return result
