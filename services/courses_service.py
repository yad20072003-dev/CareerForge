from services.ai import ai_answer


async def course_recommendations(text: str) -> str:
    prompt = (
        "На основе целей предложи чёткий план обучения. "
        "Сформируй по пунктам:\n"
        "— чему учиться,\n"
        "— в каком порядке,\n"
        "— какие мини-проекты сделать,\n"
        "— каких ошибок избегать.\n\n"
        f"{text}"
    )
    return await ai_answer(prompt)
