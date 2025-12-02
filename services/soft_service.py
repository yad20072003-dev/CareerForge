from services.ai import ai_answer


async def soft_analysis(text: str) -> str:
    prompt = (
        "Сделай анализ soft skills пользователя. "
        "Определи сильные стороны, слабые стороны, поведенческие паттерны и рекомендации.\n\n"
        f"Ситуации пользователя:\n{text}"
    )
    return await ai_answer(prompt)
