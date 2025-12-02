from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_keyboard():
    kb = [
        [InlineKeyboardButton(text="🎯 Я выбираю профессию", callback_data="scenario_profession")],
        [InlineKeyboardButton(text="💼 Я ищу работу", callback_data="scenario_job")],
        [InlineKeyboardButton(text="🗣 У меня собеседование", callback_data="scenario_interview")],
        [InlineKeyboardButton(text="🆓 Бесплатно", callback_data="free_menu")],
        [InlineKeyboardButton(text="📋 Все услуги", callback_data="services_menu")],
        [InlineKeyboardButton(text="ℹ️ Инфо", callback_data="info")],
        [InlineKeyboardButton(text="📜 Условия", callback_data="terms")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def services_keyboard():
    kb = [
        [InlineKeyboardButton(text="🧭 Профориентация — 149₽", callback_data="career")],
        [InlineKeyboardButton(text="✏️ Создание резюме — 199₽", callback_data="resume_create")],
        [InlineKeyboardButton(text="🔍 Проверка резюме — 149₽", callback_data="resume_check")],
        [InlineKeyboardButton(text="🎤 HR-мок интервью — 199₽", callback_data="mock")],
        [InlineKeyboardButton(text="📘 План на собеседование — 149₽", callback_data="interview_plan")],
        [InlineKeyboardButton(text="💬 Soft skills анализ — 99₽", callback_data="soft")],
        [InlineKeyboardButton(text="📄 Анализ вакансии — 99₽", callback_data="vacancy")],
        [InlineKeyboardButton(text="🎓 Подбор обучения — 99₽", callback_data="courses")],
        [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def scenario_profession_keyboard():
    kb = [
        [InlineKeyboardButton(text="🎁 Пакет «Старт карьеры» — 399₽", callback_data="pack_start_career")],
        [InlineKeyboardButton(text="🧭 Профориентация — 149₽", callback_data="career")],
        [InlineKeyboardButton(text="💬 Soft skills анализ — 99₽", callback_data="soft")],
        [InlineKeyboardButton(text="🎓 Подбор обучения — 99₽", callback_data="courses")],
        [InlineKeyboardButton(text="📋 Все услуги", callback_data="services_menu")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def scenario_job_keyboard():
    kb = [
        [InlineKeyboardButton(text="🏆 Пакет «Максимум» — 699₽", callback_data="pack_max")],
        [InlineKeyboardButton(text="✏️ Создание резюме — 199₽", callback_data="resume_create")],
        [InlineKeyboardButton(text="🔍 Проверка резюме — 149₽", callback_data="resume_check")],
        [InlineKeyboardButton(text="📄 Анализ вакансии — 99₽", callback_data="vacancy")],
        [InlineKeyboardButton(text="💬 Soft skills анализ — 99₽", callback_data="soft")],
        [InlineKeyboardButton(text="🎓 Подбор обучения — 99₽", callback_data="courses")],
        [InlineKeyboardButton(text="📋 Все услуги", callback_data="services_menu")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def scenario_interview_keyboard():
    kb = [
        [InlineKeyboardButton(text="🎯 Пакет «Перед собесом» — 449₽", callback_data="pack_before_interview")],
        [InlineKeyboardButton(text="🎤 HR-мок интервью — 199₽", callback_data="mock")],
        [InlineKeyboardButton(text="📘 План на собеседование — 149₽", callback_data="interview_plan")],
        [InlineKeyboardButton(text="🔍 Проверка резюме — 149₽", callback_data="resume_check")],
        [InlineKeyboardButton(text="📄 Анализ вакансии — 99₽", callback_data="vacancy")],
        [InlineKeyboardButton(text="📋 Все услуги", callback_data="services_menu")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def free_keyboard():
    kb = [
        [InlineKeyboardButton(text="⚡ Мини-советы по резюме", callback_data="free_mini_resume")],
        [InlineKeyboardButton(text="📌 Чек-лист к собеседованию", callback_data="free_checklist")],
        [InlineKeyboardButton(text="🔎 Советы по поиску работы", callback_data="free_tips")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def back_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_to_menu")]
        ]
    )


def service_start_keyboard(service_code: str, price: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"💳 Оплатить {price}₽", callback_data=f"pay_{service_code}")],
            [InlineKeyboardButton(text="🚀 Начать сейчас", callback_data=f"start_{service_code}")],
            [InlineKeyboardButton(text="⬅️ Назад к услугам", callback_data="services_menu")],
        ]
    )


def process_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_step")]
        ]
    )
