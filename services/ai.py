import os
import asyncio
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def ai_answer(system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> str:
    def _call():
        model = os.getenv("OPENAI_MODEL", "gpt-5.1-mini")
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()

    return await asyncio.to_thread(_call)
