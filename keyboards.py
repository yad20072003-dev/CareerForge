from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_keyboard():
    kb = [
        [InlineKeyboardButton(text="🔥 Меню услуг", callback_data="services_menu")],
        [InlineKeyboardButton(text="ℹ️ Инфо / Услуги / Цены", callback_data="info")],
        [InlineKeyboardButton(text="📜 Условия использования", callback_data="terms")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def services_keyboard():
    kb = [
        [InlineKeyboardButton(text="🧭 Профориентация — 149₽", callback_data="career")],
        [InlineKeyboardButton(text="📝 Создание резюме — 199₽", callback_data="resume_create")],
        [InlineKeyboardButton(text="🔍 Проверка резюме — 149₽", callback_data="resume_check")],
        [InlineKeyboardButton(text="🎤 HR-мок интервью — 199₽", callback_data="mock")],
        [InlineKeyboardButton(text="📘 План на собеседование — 149₽", callback_data="interview_plan")],
        [InlineKeyboardButton(text="💬 Soft skills анализ — 129₽", callback_data="soft")],
        [InlineKeyboardButton(text="📄 Анализ вакансии — 129₽", callback_data="vacancy")],
        [InlineKeyboardButton(text="🎓 Подбор обучения — 129₽", callback_data="courses")],
        [InlineKeyboardButton(text="⬅️ Назад в главное меню", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def back_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
        ]
    )


def service_start_keyboard(service_code: str, price: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", callback_data=f"pay_{service_code}")],
            [InlineKeyboardButton(text="🚀 Начать без оплаты", callback_data=f"start_{service_code}")],
            [InlineKeyboardButton(text="⬅️ Назад к услугам", callback_data="services_menu")],
        ]
    )


def process_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Отмена", callback_data="back_to_menu")]
        ]
    )
