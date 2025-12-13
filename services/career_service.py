from services.ai import ai_answer
from prompts.career import CAREER_ORIENTATION_PROMPT


async def make_career_report(payload: str) -> str:
    return await ai_answer(system_prompt=CAREER_ORIENTATION_PROMPT, user_prompt=payload)
