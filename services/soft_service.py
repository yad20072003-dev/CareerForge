from services.ai import ai_answer
from prompts.soft import SOFT_ANALYSIS_SYSTEM_PROMPT


async def soft_analysis(user_payload: str) -> str:
    return await ai_answer(
        system_prompt=SOFT_ANALYSIS_SYSTEM_PROMPT,
        user_prompt=user_payload
    )
