import os
import asyncio

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.1-chat-latest")
MAX_CHARS = 12000

try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    USE_LEGACY = True
except Exception:
    USE_LEGACY = False


def _clean_text(text: str) -> str:
    if not text:
        return ""
    return text.strip()


def _safe_truncate(text: str, max_len: int = MAX_CHARS) -> str:
    if text and len(text) > max_len:
        return text[:max_len]
    return text


def _call_legacy(system_prompt: str, user_prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.45,
        max_tokens=2048,
    )
    return _clean_text(response["choices"][0]["message"]["content"])


async def ai_answer(system_prompt: str, user_prompt: str) -> str:
    system_prompt = _safe_truncate(system_prompt)
    user_prompt = _safe_truncate(user_prompt)

    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            _call_legacy,
            system_prompt,
            user_prompt
        )
    except Exception as e:
        print("AI ERROR:", e)
        return "Не удалось получить ответ от ИИ. Попробуйте позже."
