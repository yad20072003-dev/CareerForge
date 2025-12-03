import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-5.1-mini"
MAX_CHARS = 12000


def _clean(text: str) -> str:
    if not text:
        return ""
    return text.strip()


def _truncate(text: str, max_len: int = MAX_CHARS) -> str:
    if not text:
        return ""
    if len(text) > max_len:
        return text[:max_len]
    return text[:max_len]


async def ai_answer(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.45,
    max_tokens: int = 2048,
) -> str:
    system_prompt = _truncate(system_prompt)
    user_prompt = _truncate(user_prompt)

    try:
        completion = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = completion.choices[0].message.content
        return _clean(content)
    except Exception as e:
        print("AI ERROR:", e)
        return "⚠ Произошла ошибка при обращении к ИИ. Попробуйте ещё раз через минуту."
