from services.ai import ai_answer
from prompts.plan import INTERVIEW_PLAN_PROMPT


async def interview_plan(user_text: str) -> str:
    return await ai_answer(
        system_prompt=INTERVIEW_PLAN_PROMPT,
        user_prompt=user_text
    )
