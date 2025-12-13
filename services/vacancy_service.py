from services.ai import ai_answer
from prompts.vacancy import VACANCY_ANALYSIS_PROMPT


async def vacancy_match(payload: str) -> str:
    return await ai_answer(system_prompt=VACANCY_ANALYSIS_PROMPT, user_prompt=payload)
