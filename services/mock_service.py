from services.ai import ai_answer
from prompts.mock import (
    build_mock_start_prompt,
    build_mock_step_prompt,
    build_mock_summary_prompt,
)

async def hr_mock_interview(payload: str) -> str:
    result = await ai_answer(payload, "")
    return result

async def mock_start(position: str, experience: str, goals: str) -> str:
    prompt = build_mock_start_prompt(position, experience, goals)
    return await ai_answer(prompt, "")

async def mock_step(step: int, position: str, experience: str, goals: str, dialog: str) -> str:
    prompt = build_mock_step_prompt(step, position, experience, goals, dialog)
    return await ai_answer(prompt, "")

async def mock_summary(position: str, experience: str, goals: str, dialog: str) -> str:
    prompt = build_mock_summary_prompt(position, experience, goals, dialog)
    return await ai_answer(prompt, "")
