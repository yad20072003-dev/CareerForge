from services.ai import ai_answer
from prompts.competitiveness import COMPETITIVENESS_PROMPT


async def competitiveness_check(payload: str) -> str:
    return await ai_answer(system_prompt=COMPETITIVENESS_PROMPT, user_prompt=payload)
