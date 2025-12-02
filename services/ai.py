import os
from openai import OpenAI
from httpx import Client

http_client = Client(proxies=None)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=http_client
)

async def ai_answer(prompt: str, model: str = "gpt-5.1-mini"):
    answer = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return answer.choices[0].message["content"]
