import os
from services.ai import ai_answer
from prompts.mock import MOCK_INTERVIEW_SYSTEM_PROMPT


async def hr_mock_interview(payload: str) -> str:
    user_prompt = f"{payload}"
    response = await ai_answer(
        system_prompt=MOCK_INTERVIEW_SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )
    return response
