from services.ai import ai_answer
from prompts.vacancy import VACANCY_MATCH_SYSTEM_PROMPT


async def vacancy_match(user_payload: str) -> str:
    return await ai_answer(
        system_prompt=VACANCY_MATCH_SYSTEM_PROMPT,
        user_prompt=user_payload
    )
