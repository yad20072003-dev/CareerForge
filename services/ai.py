import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-5.1-mini"


async def ai_answer(prompt: str) -> str:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты — уверенный, вежливый и профессиональный HR-эксперт, карьерный консультант "
                    "и специалист по резюме мирового уровня. "
                    "Отвечай структурировано, детально и по делу. "
                    "Если в сообщении пользователя хаос, мало данных, ошибки — мягко, но честно укажи на это "
                    "и попроси уточнить. "
                    "Всегда адаптируй стиль под ситуацию: дружелюбный тон для новичков, строгий — если нужно. "
                    "Если просят анализ — анализируй. "
                    "Если просят резюме — формируй полноценный текст. "
                    "Если просят HR-интервью — задавай вопросы как реальный HR, "
                    "включая уточняющие, стрессовые и кейсовые."
                )
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=4096,
        temperature=0.8,
    )
    return completion.choices[0].message["content"]
