from services.ai import ai_answer
from prompts.vacancy import build_vacancy_prompt

async def vacancy_match(text: str) -> str:
    prompt = build_vacancy_prompt(text)
    result = await ai_answer(prompt, "")
    return result
