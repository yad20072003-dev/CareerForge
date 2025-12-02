import os
from services.ai import ai_answer
from prompts.mock_prompt import MOCK_INTERVIEW_SYSTEM_PROMPT


async def hr_mock_interview(payload: str) -> str:
    """
    Универсальная функция для всех этапов мок-интервью.
    payload — то, что формирует bot.py (старт / шаг / финал).
    """
    user_message = f"{payload}"

    response = await ai_answer(
        system_prompt=MOCK_INTERVIEW_SYSTEM_PROMPT,
        user_prompt=user_message,
        temperature=0.65,
        max_tokens=2000
    )

    return response
