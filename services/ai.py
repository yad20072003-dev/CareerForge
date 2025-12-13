import os
import asyncio
from openai import OpenAI

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
MAX_CHARS = 12000

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.strip()


def safe_truncate(text: str, max_len: int = MAX_CHARS) -> str:
    if text and len(text) > max_len:
        return text[:max_len]
    return text


def _sync_call(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.45,
        max_tokens=2048,
    )
    return clean_text(response.choices[0].message.content)


async def ai_answer(system_prompt: str, user_prompt: str) -> str:
    system_prompt = safe_truncate(system_prompt)
    user_prompt = safe_truncate(user_prompt)

    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            _sync_call,
            system_prompt,
            user_prompt
        )
    except Exception as e:
        print("AI ERROR:", e)
        return "Не удалось получить ответ от ИИ. Попробуйте позже."
