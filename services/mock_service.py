from services.ai import ai_answer
from prompts.mock import PROMPT_MOCK

async def hr_mock_interview(conversation: str):
    return await ai_answer(PROMPT_MOCK, conversation)
