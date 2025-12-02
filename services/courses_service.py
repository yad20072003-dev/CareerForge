from services.ai import ai_answer
from prompts.courses import build_courses_prompt

async def course_recommendations(user_text: str) -> str:
    prompt = build_courses_prompt(user_text)
    result = await ai_answer(prompt, "")
    return result
