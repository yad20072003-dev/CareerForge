from services.ai import ai_answer
from prompts.soft import build_soft_prompt

async def soft_analysis(text: str) -> str:
    prompt = build_soft_prompt(text)
    result = await ai_answer(prompt, "")
    return result
