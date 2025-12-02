from services.ai import ai_answer


async def vacancy_match(text: str) -> str:
    prompt = (
        "Оцени соответствие профиля пользователя вакансии. "
        "Структура:\n"
        "1. Что подходит\n"
        "2. Что не подходит\n"
        "3. Что критично поправить\n"
        "4. Чего не хватает\n"
        "5. Итоговая рекомендация\n\n"
        f"{text}"
    )
    return await ai_answer(prompt)
