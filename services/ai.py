import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-5.1-mini"
MAX_CHARS = 12000


def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.strip()


def safe_truncate(text: str, max_len: int = MAX_CHARS) -> str:
    if text and len(text) > max_len:
        return text[:max_len]
    return text


async def ai_answer(system_prompt: str, user_prompt: str) -> str:
    system_prompt = safe_truncate(system_prompt)
    user_prompt = safe_truncate(user_prompt)

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.45,
            max_tokens=2048
        )

        answer = completion.choices[0].message["content"]
        return clean_text(answer)

    except Exception as e:
        print("AI ERROR:", e)
        return (
            "⚠ Произошла ошибка при обращении к ИИ.\n"
            "Попробуйте ещё раз спустя минуту."
        )
