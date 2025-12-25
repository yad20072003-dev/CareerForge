import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chat(prompt: str, system: str) -> str:
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.1"),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.4")),
    )
    return resp.choices[0].message.content.strip()
