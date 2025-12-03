from services.ai import ai_answer
from prompts.courses import COURSE_RECOMMEND_PROMPT


async def course_recommendations(user_text: str) -> str:
    return await ai_answer(
        system_prompt=COURSE_RECOMMEND_PROMPT,
        user_prompt=user_text
    )
