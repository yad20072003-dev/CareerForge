from services.ai import ai_answer


async def check_resume(text: str) -> str:
    prompt = (
        "Проанализируй резюме как опытный HR. "
        "Формат ответа:\n"
        "1. Главные проблемы\n"
        "2. Недостающие блоки\n"
        "3. Что убрать или переформулировать\n"
        "4. Риски для работодателя\n"
        "5. Улучшенная версия резюме (полностью, целиком)\n\n"
        f"Текст резюме:\n{text}"
    )
    return await ai_answer(prompt)
