import os
from services.ai import ai_answer
from prompts.vacancy import VACANCY_MATCH_PROMPT


async def vacancy_match(joined_text: str) -> str:
    user_prompt = f"""
ДАНО:

{joined_text}

Сначала кратко сформулируй суть вакансии.
Затем сравни требования и профиль кандидата по структуре из системного промта.
"""
    response = await ai_answer(
        system_prompt=VACANCY_MATCH_PROMPT,
        user_prompt=user_prompt,
    )
    return response
