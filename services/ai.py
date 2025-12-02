import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

client = OpenAI()

MODEL = "gpt-5.1-mini"
MAX_CHARS = 12000


def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.strip()


def safe_truncate(text: str, max_len: int = MAX_CHARS) -> str:
    if not text:
        return ""
    if len(text) > max_len:
        return text[:max_len]
    return text


async def ai_answer(system_prompt: str, user_prompt: str) -> str:
    system_prompt = safe_truncate(system_prompt)
    user_prompt = safe_truncate(user_prompt)

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.45,
            max_tokens=2300
        )
        return clean_text(completion.choices[0].message.content)

    except Exception:
        return "⚠ Произошёл технический сбой. Попробуйте ещё раз через минуту."
