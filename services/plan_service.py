from services.ai import ai_answer


async def interview_plan(text: str) -> str:
    prompt = (
        "Составь индивидуальный план поведения на собеседовании. Включи:\n"
        "— что подчеркнуть,\n"
        "— что скрыть,\n"
        "— вопросы, к которым подготовиться,\n"
        "— ошибки, которых избегать,\n"
        "— рекомендации по стилю общения.\n\n"
        f"Данные пользователя:\n{text}"
    )
    return await ai_answer(prompt)
