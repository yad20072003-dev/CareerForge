from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Я выбираю профессию", callback_data="scenario_profession")],
        [InlineKeyboardButton(text="💼 Я ищу работу", callback_data="scenario_job")],
        [InlineKeyboardButton(text="🗣 Собеседование", callback_data="scenario_interview")],
        [InlineKeyboardButton(text="🆓 Бесплатно", callback_data="free_menu")],
        [InlineKeyboardButton(text="ℹ️ О боте", callback_data="info")],
        [InlineKeyboardButton(text="📜 Условия", callback_data="terms")]
    ])


def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ])


def process_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад на шаг", callback_data="back_step")]
    ])


def services_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧭 Профориентация — 149₽", callback_data="career")],
        [InlineKeyboardButton(text="✏️ Создание резюме — 199₽", callback_data="resume_create")],
        [InlineKeyboardButton(text="🔍 Проверка резюме — 149₽", callback_data="resume_check")],
        [InlineKeyboardButton(text="🎤 HR-мок интервью — 199₽", callback_data="mock")],
        [InlineKeyboardButton(text="📘 План поведения — 149₽", callback_data="interview_plan")],
        [InlineKeyboardButton(text="💬 Soft-skills анализ — 99₽", callback_data="soft")],
        [InlineKeyboardButton(text="📄 Анализ вакансии — 99₽", callback_data="vacancy")],
        [InlineKeyboardButton(text="🎓 Подбор обучения — 99₽", callback_data="courses")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ])


def service_start_keyboard(code: str, price: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Начать", callback_data=f"start_{code}")],
        [InlineKeyboardButton(text=f"💳 Оплатить {price}₽", callback_data=f"pay_{code}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="services_menu")]
    ])


def scenario_profession_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧭 Профориентация — 149₽", callback_data="career")],
        [InlineKeyboardButton(text="💬 Soft skills — 99₽", callback_data="soft")],
        [InlineKeyboardButton(text="🎓 Обучение — 99₽", callback_data="courses")],
        [InlineKeyboardButton(text="🎁 Пакет «Старт карьеры» — 399₽", callback_data="pack_start_career")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ])


def scenario_job_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Создать резюме — 199₽", callback_data="resume_create")],
        [InlineKeyboardButton(text="🔍 Проверить резюме — 149₽", callback_data="resume_check")],
        [InlineKeyboardButton(text="📄 Анализ вакансии — 99₽", callback_data="vacancy")],
        [InlineKeyboardButton(text="🎓 Подбор обучения — 99₽", callback_data="courses")],
        [InlineKeyboardButton(text="🏆 Пакет «Максимум» — 699₽", callback_data="pack_max")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ])


def scenario_interview_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎤 HR-мок интервью — 199₽", callback_data="mock")],
        [InlineKeyboardButton(text="📘 План поведения — 149₽", callback_data="interview_plan")],
        [InlineKeyboardButton(text="🔍 Проверка резюме — 149₽", callback_data="resume_check")],
        [InlineKeyboardButton(text="📄 Анализ вакансии — 99₽", callback_data="vacancy")],
        [InlineKeyboardButton(text="🎯 Пакет «Перед собесом» — 449₽", callback_data="pack_before_interview")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ])


def free_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Мини-советы по резюме", callback_data="free_mini_resume")],
        [InlineKeyboardButton(text="📌 Чек-лист к собесу", callback_data="free_checklist")],
        [InlineKeyboardButton(text="🔎 Советы по поиску", callback_data="free_tips")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ])
