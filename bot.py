import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import (
    main_keyboard,
    back_button,
    process_keyboard,
    services_keyboard,
    service_start_keyboard,
    scenario_profession_keyboard,
    scenario_job_keyboard,
    scenario_interview_keyboard,
    free_keyboard,
)
from states import (
    CareerState,
    ResumeCreateState,
    ResumeCheckState,
    MockInterviewState,
    InterviewPlanState,
    SoftSkillsState,
    VacancyMatchState,
    CoursesState,
)
from products.products import PRODUCTS

from services.career_service import make_career_report
from services.resume_service import make_resume
from services.rescheck_service import check_resume
from services.mock_service import hr_mock_interview
from services.plan_service import interview_plan
from services.soft_service import soft_analysis
from services.vacancy_service import vacancy_match
from services.courses_service import course_recommendations


BOT_TOKEN = os.getenv("BOT_TOKEN")
MAX_MOCK_STEPS = 18
MAX_TG_MESSAGE_LENGTH = 4000

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def is_answer_too_short(text: str) -> bool:
    if not text:
        return True
    return len(text.strip()) < 10


def split_text(text: str, max_length: int = MAX_TG_MESSAGE_LENGTH) -> list[str]:
    if not text:
        return []
    parts = []
    remaining = text.strip()
    while len(remaining) > max_length:
        split_at = remaining.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = max_length
        parts.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    if remaining:
        parts.append(remaining)
    return parts


async def send_long_message(message: Message, text: str, reply_markup=None):
    parts = split_text(text)
    for i, part in enumerate(parts):
        if i == 0:
            await message.answer(part, reply_markup=reply_markup)
        else:
            await message.answer(part)


@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer(
        "👋 Это «Кузница карьеры».\n\n"
        "• выбор направления\n"
        "• сильное резюме\n"
        "• подготовка к собеседованию\n\n"
        "Выберите, что актуально сейчас.",
        reply_markup=main_keyboard()
    )


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Главное меню:", reply_markup=main_keyboard())


@dp.callback_query(F.data == "scenario_profession")
async def scenario_profession(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text(
        "🎯 Выбор направления.",
        reply_markup=scenario_profession_keyboard()
    )


@dp.callback_query(F.data == "scenario_job")
async def scenario_job(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text(
        "💼 Поиск работы.",
        reply_markup=scenario_job_keyboard()
    )


@dp.callback_query(F.data == "scenario_interview")
async def scenario_interview(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text(
        "🗣 Подготовка к собеседованию.",
        reply_markup=scenario_interview_keyboard()
    )


@dp.callback_query(F.data == "free_menu")
async def free_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text(
        "🆓 Бесплатные материалы.",
        reply_markup=free_keyboard()
    )


@dp.callback_query(F.data == "career")
async def start_career(cb: CallbackQuery):
    p = PRODUCTS["CAREER_ANALYSIS_149"]
    await cb.message.edit_text(
        p["description"],
        reply_markup=service_start_keyboard(p["code"], p["amount"])
    )


@dp.callback_query(F.data == "start_CAREER_ANALYSIS_149")
async def career_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CareerState.waiting_for_basic)
    await cb.message.edit_text(
        "Сколько вам лет и чем вы занимаетесь?",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_basic)
async def career_basic(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Чуть подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(basic=message.text)
    await state.set_state(CareerState.waiting_for_education)
    await message.answer("Образование.", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_education)
async def career_education(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте деталей.", reply_markup=process_keyboard())
        return
    await state.update_data(education=message.text)
    await state.set_state(CareerState.waiting_for_experience)
    await message.answer("Опыт.", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_experience)
async def career_experience(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Чуть подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(CareerState.waiting_for_interests)
    await message.answer("Интересы.", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_interests)
async def career_interests(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Раскройте мысль.", reply_markup=process_keyboard())
        return
    await state.update_data(interests=message.text)
    await state.set_state(CareerState.waiting_for_preferences)
    await message.answer("Предпочтения.", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_preferences)
async def career_preferences(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте деталей.", reply_markup=process_keyboard())
        return
    await state.update_data(preferences=message.text)
    await state.set_state(CareerState.waiting_for_goals)
    await message.answer("Цели.", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_goals)
async def career_goals(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Опишите цели подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(goals=message.text)
    data = await state.get_data()
    text = (
        f"База: {data['basic']}\n\n"
        f"Образование: {data['education']}\n\n"
        f"Опыт: {data['experience']}\n\n"
        f"Интересы: {data['interests']}\n\n"
        f"Предпочтения: {data['preferences']}\n\n"
        f"Цели: {data['goals']}"
    )
    await state.clear()
    result = await make_career_report(text)
    await send_long_message(message, result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "resume_create")
async def resume_start(cb: CallbackQuery):
    p = PRODUCTS["RESUME_CREATE_199"]
    await cb.message.edit_text(
        p["description"],
        reply_markup=service_start_keyboard(p["code"], p["amount"])
    )


@dp.callback_query(F.data == "start_RESUME_CREATE_199")
async def resume_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ResumeCreateState.waiting_for_position)
    await cb.message.edit_text("Должность.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_position)
async def resume_position(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Уточните.", reply_markup=process_keyboard())
        return
    await state.update_data(position=message.text)
    await state.set_state(ResumeCreateState.waiting_for_contacts)
    await message.answer("Контакты.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_contacts)
async def resume_contacts(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте контакты.", reply_markup=process_keyboard())
        return
    await state.update_data(contacts=message.text)
    await state.set_state(ResumeCreateState.waiting_for_experience)
    await message.answer("Опыт.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_experience)
async def resume_experience(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(ResumeCreateState.waiting_for_education)
    await message.answer("Образование.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_education)
async def resume_education(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(education=message.text)
    await state.set_state(ResumeCreateState.waiting_for_skills)
    await message.answer("Навыки.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_skills)
async def resume_skills(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте навыки.", reply_markup=process_keyboard())
        return
    await state.update_data(skills=message.text)
    await state.set_state(ResumeCreateState.waiting_for_projects)
    await message.answer("Проекты.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_projects)
async def resume_projects(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте примеры.", reply_markup=process_keyboard())
        return
    await state.update_data(projects=message.text)
    await state.set_state(ResumeCreateState.waiting_for_extra)
    await message.answer("Дополнительно.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_extra)
async def resume_extra(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте деталей.", reply_markup=process_keyboard())
        return
    await state.update_data(extra=message.text)
    data = await state.get_data()
    text = (
        f"Должность: {data['position']}\n\n"
        f"Контакты: {data['contacts']}\n\n"
        f"Опыт: {data['experience']}\n\n"
        f"Образование: {data['education']}\n\n"
        f"Навыки: {data['skills']}\n\n"
        f"Проекты: {data['projects']}\n\n"
        f"Дополнительно: {data['extra']}"
    )
    await state.clear()
    result = await make_resume(text)
    await send_long_message(message, result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "resume_check")
async def resume_check_start(cb: CallbackQuery):
    p = PRODUCTS["RESUME_CHECK_149"]
    await cb.message.edit_text(
        p["description"],
        reply_markup=service_start_keyboard(p["code"], p["amount"])
    )


@dp.callback_query(F.data == "start_RESUME_CHECK_149")
async def resume_check_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ResumeCheckState.waiting_for_resume)
    await cb.message.edit_text("Текст резюме.", reply_markup=process_keyboard())


@dp.message(ResumeCheckState.waiting_for_resume)
async def resume_check_step(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Полный текст.", reply_markup=process_keyboard())
        return
    result = await check_resume(message.text)
    await state.clear()
    await send_long_message(message, result, reply_markup=main_keyboard())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
