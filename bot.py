import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
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
from keyboards import (
    main_keyboard,
    back_button,
    service_start_keyboard,
    process_keyboard
)
from services.career_service import make_career_report
from services.resume_service import make_resume
from services.rescheck_service import check_resume
from services.mock_service import hr_mock_interview
from services.plan_service import interview_plan
from services.soft_service import soft_analysis
from services.vacancy_service import vacancy_match
from services.courses_service import course_recommendations
from products.products import PRODUCTS

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer(
        "Добро пожаловать! Выберите услугу:",
        reply_markup=main_keyboard()
    )


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Выберите услугу:", reply_markup=main_keyboard())


@dp.callback_query(F.data == "info")
async def info_block(cb: CallbackQuery):
    text = (
        "📌 Услуги и цены:\n\n"
        "🧭 Профориентация — 149₽\n"
        "📝 Создание резюме — 199₽\n"
        "🔍 Проверка резюме — 149₽\n"
        "🎤 HR-мок интервью — 199₽\n"
        "📘 План поведения — 149₽\n"
        "💬 Soft skills анализ — 129₽\n"
        "📄 Анализ вакансии — 129₽\n"
        "🎓 Подбор обучения — 129₽\n"
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "terms")
async def terms_block(cb: CallbackQuery):
    text = (
        "📜 Условия использования\n\n"
        "1. Бот предоставляет информационные услуги.\n"
        "2. Оплата производится через официальные платёжные сервисы.\n"
        "3. Возврат возможен, если услуга не была оказана.\n"
        "4. Данные пользователей не передаются третьим лицам.\n"
        "5. Используя бота, вы соглашаетесь с условиями."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data.startswith("pay_"))
async def pay_stub(cb: CallbackQuery):
    code = cb.data.replace("pay_", "")
    product = PRODUCTS.get(code)

    if not product:
        await cb.message.answer("Ошибка товара.")
        return

    await cb.message.answer(
        f"{product['title']}\n\nЦена: {product['amount']}₽\n\n"
        f"Оплата временно недоступна.",
        reply_markup=back_button()
    )


@dp.callback_query(F.data == "career")
async def start_career(cb: CallbackQuery):
    await cb.message.edit_text(
        "🧭 Профориентация — 149₽",
        reply_markup=service_start_keyboard("CAREER_ANALYSIS_149", 149)
    )


@dp.callback_query(F.data == "start_CAREER_ANALYSIS_149")
async def start_career_input(cb: CallbackQuery, state: FSMContext):
    await state.set_state(CareerState.waiting_for_input)
    await cb.message.edit_text(
        "Опишите: образование, навыки, интересы, опыт.",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_input)
async def career_process(message: Message, state: FSMContext):
    result = await make_career_report(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "resume_create")
async def start_resume(cb: CallbackQuery):
    await cb.message.edit_text(
        "📝 Создание резюме — 199₽",
        reply_markup=service_start_keyboard("RESUME_CREATE_199", 199)
    )


@dp.callback_query(F.data == "start_RESUME_CREATE_199")
async def begin_resume(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ResumeCreateState.waiting_for_input)
    await cb.message.edit_text(
        "Опишите всё для резюме: опыт, навыки, образование.",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_input)
async def resume_process(message: Message, state: FSMContext):
    result = await make_resume(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "resume_check")
async def start_resume_check(cb: CallbackQuery):
    await cb.message.edit_text(
        "🔍 Проверка резюме — 149₽",
        reply_markup=service_start_keyboard("RESUME_CHECK_149", 149)
    )


@dp.callback_query(F.data == "start_RESUME_CHECK_149")
async def begin_resume_check(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ResumeCheckState.waiting_for_resume)
    await cb.message.edit_text(
        "Отправьте текст резюме.",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCheckState.waiting_for_resume)
async def resume_check(message: Message, state: FSMContext):
    text = message.text
    result = await check_resume(text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "mock")
async def mock_start(cb: CallbackQuery):
    await cb.message.edit_text(
        "🎤 HR-мок интервью — 199₽",
        reply_markup=service_start_keyboard("MOCK_INTERVIEW_199", 199)
    )


@dp.callback_query(F.data == "start_MOCK_INTERVIEW_199")
async def mock_begin(cb: CallbackQuery, state: FSMContext):
    await state.set_state(MockInterviewState.waiting_for_dialog)
    await cb.message.edit_text(
        "Напишите вопросы и ответы, которые хотите разобрать.",
        reply_markup=process_keyboard()
    )


@dp.message(MockInterviewState.waiting_for_dialog)
async def mock_process(message: Message, state: FSMContext):
    result = await hr_mock_interview(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "interview_plan")
async def plan_start(cb: CallbackQuery):
    await cb.message.edit_text(
        "📘 План поведения — 149₽",
        reply_markup=service_start_keyboard("INTERVIEW_PLAN_149", 149)
    )


@dp.callback_query(F.data == "start_INTERVIEW_PLAN_149")
async def plan_begin(cb: CallbackQuery, state: FSMContext):
    await state.set_state(InterviewPlanState.waiting_for_info)
    await cb.message.edit_text(
        "Опишите: должность, компанию, сильные стороны, слабости.",
        reply_markup=process_keyboard()
    )


@dp.message(InterviewPlanState.waiting_for_info)
async def plan_process(message: Message, state: FSMContext):
    result = await interview_plan(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "soft")
async def soft_start(cb: CallbackQuery):
    await cb.message.edit_text(
        "💬 Soft skills анализ — 129₽",
        reply_markup=service_start_keyboard("SOFT_ANALYSIS_129", 129)
    )


@dp.callback_query(F.data == "start_SOFT_ANALYSIS_129")
async def soft_begin(cb: CallbackQuery, state: FSMContext):
    await state.set_state(SoftSkillsState.waiting_for_answers)
    await cb.message.edit_text(
        "Опишите поведение в команде, стресс, конфликты.",
        reply_markup=process_keyboard()
    )


@dp.message(SoftSkillsState.waiting_for_answers)
async def soft_process(message: Message, state: FSMContext):
    result = await soft_analysis(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "vacancy")
async def vacancy_start(cb: CallbackQuery):
    await cb.message.edit_text(
        "📄 Анализ вакансии — 129₽",
        reply_markup=service_start_keyboard("VACANCY_MATCH_129", 129)
    )


@dp.callback_query(F.data == "start_VACANCY_MATCH_129")
async def vacancy_begin(cb: CallbackQuery, state: FSMContext):
    await state.set_state(VacancyMatchState.waiting_for_vacancy)
    await cb.message.edit_text(
        "Отправьте текст вакансии.",
        reply_markup=process_keyboard()
    )


@dp.message(VacancyMatchState.waiting_for_vacancy)
async def vacancy_part1(message: Message, state: FSMContext):
    await state.update_data(vacancy=message.text)
    await state.set_state(VacancyMatchState.waiting_for_profile)
    await message.answer(
        "Теперь опишите ваш опыт и навыки.",
        reply_markup=process_keyboard()
    )


@dp.message(VacancyMatchState.waiting_for_profile)
async def vacancy_part2(message: Message, state: FSMContext):
    data = await state.get_data()
    joined = f"Вакансия:\n{data['vacancy']}\n\nПрофиль:\n{message.text}"
    result = await vacancy_match(joined)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "courses")
async def courses_start(cb: CallbackQuery):
    await cb.message.edit_text(
        "🎓 Подбор обучения — 129₽",
        reply_markup=service_start_keyboard("COURSE_RECOMMEND_129", 129)
    )


@dp.callback_query(F.data == "start_COURSE_RECOMMEND_129")
async def courses_begin(cb: CallbackQuery, state: FSMContext):
    await state.set_state(CoursesState.waiting_for_info)
    await cb.message.edit_text(
        "Опишите ваш уровень и цель обучения.",
        reply_markup=process_keyboard()
    )


@dp.message(CoursesState.waiting_for_info)
async def courses_process(message: Message, state: FSMContext):
    result = await course_recommendations(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
