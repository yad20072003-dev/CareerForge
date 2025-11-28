from services.ai import ai_answer
from prompts.vacancy import PROMPT_VACANCY

async def vacancy_match(vacancy_and_profile: str):
    return await ai_answer(PROMPT_VACANCY, vacancy_and_profile)
