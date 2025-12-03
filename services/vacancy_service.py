from services.ai import ai_answer
from prompts.vacancy import VACANCY_MATCH_PROMPT


async def vacancy_match(user_text: str) -> str:
    return await ai_answer(
        system_prompt=VACANCY_MATCH_PROMPT,
        user_prompt=user_text
    )
