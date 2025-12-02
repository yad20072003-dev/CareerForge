import os
from openai import OpenAI
import httpx

transport = httpx.HTTPTransport(proxy=None)

http_client = httpx.Client(transport=transport)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=http_client
)

async def ai_answer(prompt: str, model: str = "gpt-5.1-mini"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]
