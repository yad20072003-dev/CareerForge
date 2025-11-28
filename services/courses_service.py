from services.ai import ai_answer
from prompts.courses import PROMPT_COURSES

async def course_recommendations(user_data: str):
    return await ai_answer(PROMPT_COURSES, user_data)
