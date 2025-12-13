from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбор направления", callback_data="scenario_direction")],
        [InlineKeyboardButton(text="Поиск работы", callback_data="scenario_job")],
        [InlineKeyboardButton(text="Подготовка к собеседованию", callback_data="scenario_interview")],
        [InlineKeyboardButton(text="Бесплатно", callback_data="free_menu")],
        [InlineKeyboardButton(text="Все услуги", callback_data="services_menu")],
        [InlineKeyboardButton(text="О боте", callback_data="info")],
    ])


def back_to_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu")]
    ])


def process_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад на шаг", callback_data="back_step")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu")]
    ])


def services_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Профориентация", callback_data="career")],
        [InlineKeyboardButton(text="Создать резюме", callback_data="resume_create")],
        [InlineKeyboardButton(text="Проверить резюме", callback_data="resume_check")],
        [InlineKeyboardButton(text="Анализ вакансии", callback_data="vacancy")],
        [InlineKeyboardButton(text="HR-мок интервью (короткое)", callback_data="mock_short")],
        [InlineKeyboardButton(text="HR-мок интервью (полное)", callback_data="mock_full")],
        [InlineKeyboardButton(text="План поведения на собеседовании", callback_data="interview_plan")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu")],
    ])


def service_start_keyboard(code: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать", callback_data=f"start_{code}")],
        [InlineKeyboardButton(text="Назад", callback_data="services_menu")],
    ])


def scenario_direction_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Профориентация", callback_data="career")],
        [InlineKeyboardButton(text="Быстрая диагностика конкурентности", callback_data="free_competitiveness")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu")],
    ])


def scenario_job_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать резюме", callback_data="resume_create")],
        [InlineKeyboardButton(text="Проверить резюме", callback_data="resume_check")],
        [InlineKeyboardButton(text="Анализ вакансии", callback_data="vacancy")],
        [InlineKeyboardButton(text="Быстрая диагностика конкурентности", callback_data="free_competitiveness")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu")],
    ])


def scenario_interview_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="HR-мок интервью (короткое)", callback_data="mock_short")],
        [InlineKeyboardButton(text="HR-мок интервью (полное)", callback_data="mock_full")],
        [InlineKeyboardButton(text="План поведения на собеседовании", callback_data="interview_plan")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu")],
    ])


def free_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мини-советы по резюме", callback_data="free_mini_resume")],
        [InlineKeyboardButton(text="Чек-лист к собеседованию", callback_data="free_checklist")],
        [InlineKeyboardButton(text="Быстрая диагностика конкурентности", callback_data="free_competitiveness")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu")],
    ])


def mock_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Уточнить вопрос HR", callback_data="mock_clarify")],
        [InlineKeyboardButton(text="Завершить интервью", callback_data="mock_finish")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu")],
    ])
