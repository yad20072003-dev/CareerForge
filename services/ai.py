import os
from openai import OpenAI
import httpx

transport = httpx.HTTPTransport(proxy=None)
http_client = httpx.Client(transport=transport)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=http_client
)


async def ai_answer(system_prompt: str, user_text: str):
    response = client.chat.completions.create(
        model="gpt-5.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        temperature=0.25,
        max_tokens=5000
    )
    return response.choices[0].message.content
