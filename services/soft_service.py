from services.ai import ai_answer
from prompts.soft import SOFT_ANALYSIS_PROMPT


async def soft_analysis(user_text: str) -> str:
    return await ai_answer(
        system_prompt=SOFT_ANALYSIS_PROMPT,
        user_prompt=user_text
    )
