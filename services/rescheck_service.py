from services.ai import ai_answer
from prompts.rescheck import RESUME_CHECK_PROMPT


async def check_resume(user_payload: str) -> str:
    return await ai_answer(
        system_prompt=RESUME_CHECK_PROMPT,
        user_prompt=user_payload
    )
