import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def ai_answer(prompt, user_text):
    response = client.chat.completions.create(
        model="gpt-5.1-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_text}
        ],
        temperature=0.25,
        max_tokens=5000
    )
    return response.choices[0].message.content
