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
    process_keyboard,
    services_keyboard,
    scenario_profession_keyboard,
    scenario_job_keyboard,
    scenario_interview_keyboard,
    free_keyboard,
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
MAX_MOCK_STEPS = 7

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def is_answer_too_short(text: str) -> bool:
    if not text:
        return True
    t = text.strip()
    return len(t) < 10


@dp.message(CommandStart())
async def start_cmd(message: Message):
    text = (
        "👋 Это «Кузница карьеры».\n\n"
        "Бот помогает:\n"
        "• выбрать профессию;\n"
        "• собрать резюме;\n"
        "• подготовиться к собеседованию.\n\n"
        "Выберите подходящий сценарий."
    )
    await message.answer(text, reply_markup=main_keyboard())


@dp.callback_query(F.data == "scenario_profession")
async def scenario_profession(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "🎯 Сценарий: «Я выбираю профессию».\n\n"
        "Можно пройти профориентацию, анализ soft skills или подобрать обучение.\n"
        "Есть пакет «Старт карьеры»."
    )
    await cb.message.edit_text(text, reply_markup=scenario_profession_keyboard())


@dp.callback_query(F.data == "scenario_job")
async def scenario_job(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "💼 Сценарий: «Я ищу работу».\n\n"
        "Доступны резюме, проверка, анализ вакансии и обучение.\n"
        "Есть пакет «Максимум»."
    )
    await cb.message.edit_text(text, reply_markup=scenario_job_keyboard())


@dp.callback_query(F.data == "scenario_interview")
async def scenario_interview(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "🗣 Сценарий: «У меня собеседование».\n\n"
        "Доступны HR-мок, план, проверка резюме и анализ вакансии.\n"
        "Есть пакет «Перед собесом»."
    )
    await cb.message.edit_text(text, reply_markup=scenario_interview_keyboard())


@dp.callback_query(F.data == "free_menu")
async def free_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "🆓 Бесплатные материалы:\n"
        "• мини-советы по резюме;\n"
        "• чек-лист к собеседованию;\n"
        "• советы по поиску работы."
    )
    await cb.message.edit_text(text, reply_markup=free_keyboard())


@dp.callback_query(F.data == "free_mini_resume")
async def free_mini_resume(cb: CallbackQuery):
    text = (
        "⚡ Мини-советы по резюме:\n"
        "1) Одно резюме — одна цель.\n"
        "2) Показывайте результаты, а не обязанности.\n"
        "3) Конкретика важнее общих слов."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "free_checklist")
async def free_checklist(cb: CallbackQuery):
    text = (
        "📌 Чек-лист к собеседованию:\n"
        "• самопрезентация 1–2 минуты;\n"
        "• 2–3 примера задач;\n"
        "• понимание компании;\n"
        "• вопросы работодателю."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "free_tips")
async def free_tips(cb: CallbackQuery):
    text = (
        "🔎 Советы по поиску работы:\n"
        "• откликаться регулярно;\n"
        "• адаптировать резюме под вакансию;\n"
        "• вести учёт откликов."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "services_menu")
async def services_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Все услуги:", reply_markup=services_keyboard())


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Главное меню:", reply_markup=main_keyboard())


@dp.callback_query(F.data == "pack_start_career")
async def pack_start_career(cb: CallbackQuery):
    text = (
        "🎁 Пакет «Старт карьеры» — 399₽\n\n"
        "Включает:\n"
        "• профориентацию;\n"
        "• создание резюме;\n"
        "• план на собеседование."
    )
    await cb.message.edit_text(text, reply_markup=services_keyboard())


@dp.callback_query(F.data == "pack_before_interview")
async def pack_before_interview(cb: CallbackQuery):
    text = (
        "🎯 Пакет «Перед собесом» — 449₽\n\n"
        "Включает:\n"
        "• проверку резюме;\n"
        "• анализ вакансии;\n"
        "• план;\n"
        "• HR-мок интервью."
    )
    await cb.message.edit_text(text, reply_markup=services_keyboard())


@dp.callback_query(F.data == "pack_max")
async def pack_max(cb: CallbackQuery):
    text = (
        "🏆 Пакет «Максимум» — 699₽\n\n"
        "Полная подготовка: направления, резюме, soft skills, вакансии и собеседование."
    )
    await cb.message.edit_text(text, reply_markup=services_keyboard())


@dp.callback_query(F.data == "info")
async def info_block(cb: CallbackQuery):
    text = (
        "ℹ️ О боте.\n\n"
        "Цены:\n"
        "• 99₽ — лёгкие разборы;\n"
        "• 149₽ — глубокий разбор;\n"
        "• 199₽ — форматы «под ключ»."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "terms")
async def terms_block(cb: CallbackQuery):
    text = (
        "📜 Условия использования:\n"
        "1. Услуги информационные.\n"
        "2. Оплата через платёжные сервисы.\n"
        "3. Возврат — если услуга не оказана."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data.startswith("pay_"))
async def pay_stub(cb: CallbackQuery):
    code = cb.data.replace("pay_", "")
    product = PRODUCTS.get(code)
    if not product:
        await cb.message.answer("Ошибка товара.", reply_markup=back_button())
        return
    await cb.message.answer(
        f"{product['title']}\nЦена: {product['amount']}₽\n\n"
        "Оплата появится после подключения ЮKassa.",
        reply_markup=back_button()
    )


@dp.callback_query(F.data == "career")
async def start_career(cb: CallbackQuery):
    text = (
        "🧭 Профориентация — 149₽\n\n"
        "Разбор интересов, опыта и направлений."
    )
    await cb.message.edit_text(
        text,
        reply_markup=service_start_keyboard("CAREER_ANALYSIS_149", 149)
    )


@dp.callback_query(F.data == "start_CAREER_ANALYSIS_149")
async def career_input(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CareerState.waiting_for_basic)
    await cb.message.edit_text(
        "Сколько вам лет и чем занимаетесь?",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_basic)
async def career_basic(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Чуть подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(basic=message.text)
    await state.set_state(CareerState.waiting_for_education)
    await message.answer(
        "Расскажите про образование.",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_education)
async def career_education(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(education=message.text)
    await state.set_state(CareerState.waiting_for_experience)
    await message.answer(
        "Опишите опыт.",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_experience)
async def career_experience(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте деталей.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(CareerState.waiting_for_interests)
    await message.answer(
        "Что вам интересно?",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_interests)
async def career_interests(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Напишите подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(interests=message.text)
    await state.set_state(CareerState.waiting_for_preferences)
    await message.answer(
        "Какая работа вам комфортна?",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_preferences)
async def career_preferences(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно чуть конкретнее.", reply_markup=process_keyboard())
        return
    await state.update_data(preferences=message.text)
    await state.set_state(CareerState.waiting_for_goals)
    await message.answer(
        "Ваши цели на 1–3 года?",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_goals)
async def career_goals(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Чуть подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(goals=message.text)
    data = await state.get_data()
    joined = (
        f"{data.get('basic')}\n\n{data.get('education')}\n\n"
        f"{data.get('experience')}\n\n{data.get('interests')}\n\n"
        f"{data.get('preferences')}\n\n{data.get('goals')}"
    )
    await state.clear()
    result = await make_career_report(joined)
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "resume_create")
async def resume_start(cb: CallbackQuery):
    text = "✏️ Создание резюме — 199₽"
    await cb.message.edit_text(text, reply_markup=service_start_keyboard("RESUME_CREATE_199", 199))


@dp.callback_query(F.data == "start_RESUME_CREATE_199")
async def resume_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ResumeCreateState.waiting_for_position)
    await cb.message.edit_text("Под какую должность резюме?", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_position)
async def resume_position(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Уточните должность.", reply_markup=process_keyboard())
        return
    await state.update_data(position=message.text)
    await state.set_state(ResumeCreateState.waiting_for_contacts)
    await message.answer("Город и контакты.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_contacts)
async def resume_contacts(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно указать контакты.", reply_markup=process_keyboard())
        return
    await state.update_data(contacts=message.text)
    await state.set_state(ResumeCreateState.waiting_for_experience)
    await message.answer("Опыт работы.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_experience)
async def resume_exp(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте деталей.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(ResumeCreateState.waiting_for_education)
    await message.answer("Образование.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_education)
async def resume_edu(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(education=message.text)
    await state.set_state(ResumeCreateState.waiting_for_skills)
    await message.answer("Навыки.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_skills)
async def resume_skills(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно перечислить навыки.", reply_markup=process_keyboard())
        return
    await state.update_data(skills=message.text)
    await state.set_state(ResumeCreateState.waiting_for_projects)
    await message.answer("Проекты.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_projects)
async def resume_projects(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте примеры проектов.", reply_markup=process_keyboard())
        return
    await state.update_data(projects=message.text)
    await state.set_state(ResumeCreateState.waiting_for_extra)
    await message.answer("Дополнительная информация.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_extra)
async def resume_extra(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно чуть подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(extra=message.text)
    data = await state.get_data()
    joined = (
        f"{data.get('position')}\n\n{data.get('contacts')}\n\n{data.get('experience')}\n\n"
        f"{data.get('education')}\n\n{data.get('skills')}\n\n{data.get('projects')}\n\n"
        f"{data.get('extra')}"
    )
    await state.clear()
    result = await make_resume(joined)
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "resume_check")
async def resume_check_start(cb: CallbackQuery):
    text = "🔍 Проверка резюме — 149₽\nОтправьте текст резюме."
    await cb.message.edit_text(text, reply_markup=service_start_keyboard("RESUME_CHECK_149", 149))


@dp.callback_query(F.data == "start_RESUME_CHECK_149")
async def resume_check_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ResumeCheckState.waiting_for_resume)
    await cb.message.edit_text("Отправьте резюме.", reply_markup=process_keyboard())


@dp.message(ResumeCheckState.waiting_for_resume)
async def resume_check_process(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно полное резюме.", reply_markup=process_keyboard())
        return
    result = await check_resume(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "mock")
async def mock_start(cb: CallbackQuery):
    text = "🎤 HR-мок интервью — 199₽"
    await cb.message.edit_text(text, reply_markup=service_start_keyboard("MOCK_INTERVIEW_199", 199))


@dp.callback_query(F.data == "start_MOCK_INTERVIEW_199")
async def mock_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(MockInterviewState.waiting_for_position)
    await cb.message.edit_text("Целевая должность?", reply_markup=process_keyboard())


@dp.message(MockInterviewState.waiting_for_position)
async def mock_pos(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Уточните должность.", reply_markup=process_keyboard())
        return
    await state.update_data(position=message.text)
    await state.set_state(MockInterviewState.waiting_for_experience)
    await message.answer("Опыт под эту должность.", reply_markup=process_keyboard())


@dp.message(MockInterviewState.waiting_for_experience)
async def mock_exp(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте деталей.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(MockInterviewState.waiting_for_goals)
    await message.answer("Ваши цели и страхи?", reply_markup=process_keyboard())


@dp.message(MockInterviewState.waiting_for_goals)
async def mock_goals(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно подробнее.", reply_markup=process_keyboard())
        return

    data = await state.get_data()
    position = data.get("position")
    experience = data.get("experience")

    await state.update_data(goals=message.text, dialog="")

    payload = (
        "РЕЖИМ: start\n\n"
        f"Целевая должность: {position}\n\n"
        f"Опыт кандидата: {experience}\n\n"
        f"Цели и страхи: {message.text}\n\n"
        "Дай приветствие и первый вопрос."
    )

    reply = await hr_mock_interview(payload)

    await state.set_state(MockInterviewState.in_interview)
    await state.update_data(step=1)
    await message.answer(reply, reply_markup=process_keyboard())


@dp.message(MockInterviewState.in_interview)
async def mock_steps(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно развернуть ответ.", reply_markup=process_keyboard())
        return

    data = await state.get_data()
    step = data.get("step", 1)
    position = data.get("position")
    experience = data.get("experience")
    goals = data.get("goals")
    dialog = data.get("dialog", "")

    dialog += f"Ответ {step}: {message.text}\n\n"

    if step < MAX_MOCK_STEPS:
        payload = (
            "РЕЖИМ: step\n\n"
            f"Шаг: {step}\n\n"
            f"Цель: {position}\nОпыт: {experience}\nЦели/страхи: {goals}\n\n"
            f"История:\n{dialog}\n\n"
            "Оцени ответ и задай следующий вопрос."
        )
        reply = await hr_mock_interview(payload)
        await state.update_data(step=step + 1, dialog=dialog)
        await message.answer(reply, reply_markup=process_keyboard())
    else:
        payload = (
            "РЕЖИМ: summary\n\n"
            f"Цель: {position}\nОпыт: {experience}\nЦели/страхи: {goals}\n\n"
            f"История:\n{dialog}\n\n"
            "Сделай итог собеседования."
        )
        reply = await hr_mock_interview(payload)
        await state.clear()
        await message.answer(reply, reply_markup=main_keyboard())


@dp.callback_query(F.data == "interview_plan")
async def plan_start(cb: CallbackQuery):
    text = "📘 План на собеседование — 149₽"
    await cb.message.edit_text(text, reply_markup=service_start_keyboard("INTERVIEW_PLAN_149", 149))


@dp.callback_query(F.data == "start_INTERVIEW_PLAN_149")
async def plan_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(InterviewPlanState.waiting_for_info)
    await cb.message.edit_text("Опишите должность, компанию, сильные стороны и страхи.", reply_markup=process_keyboard())


@dp.message(InterviewPlanState.waiting_for_info)
async def plan_info(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно подробнее.", reply_markup=process_keyboard())
        return
    result = await interview_plan(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "soft")
async def soft_start(cb: CallbackQuery):
    text = "💬 Soft skills анализ — 99₽"
    await cb.message.edit_text(text, reply_markup=service_start_keyboard("SOFT_ANALYSIS_99", 99))


@dp.callback_query(F.data == "start_SOFT_ANALYSIS_99")
async def soft_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(SoftSkillsState.waiting_for_answers)
    await cb.message.edit_text("Опишите несколько ситуаций: команда, конфликт, дедлайн.", reply_markup=process_keyboard())


@dp.message(SoftSkillsState.waiting_for_answers)
async def soft_process(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно подробнее.", reply_markup=process_keyboard())
        return
    result = await soft_analysis(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "vacancy")
async def vacancy_start(cb: CallbackQuery):
    text = "📄 Анализ вакансии — 99₽"
    await cb.message.edit_text(text, reply_markup=service_start_keyboard("VACANCY_MATCH_99", 99))


@dp.callback_query(F.data == "start_VACANCY_MATCH_99")
async def vacancy_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(VacancyMatchState.waiting_for_vacancy)
    await cb.message.edit_text("Отправьте текст вакансии.", reply_markup=process_keyboard())


@dp.message(VacancyMatchState.waiting_for_vacancy)
async def vacancy_vac(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно полное описание.", reply_markup=process_keyboard())
        return
    await state.update_data(vacancy=message.text)
    await state.set_state(VacancyMatchState.waiting_for_profile)
    await message.answer("Теперь опишите ваш опыт и навыки.", reply_markup=process_keyboard())


@dp.message(VacancyMatchState.waiting_for_profile)
async def vacancy_profile(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно подробнее.", reply_markup=process_keyboard())
        return
    data = await state.get_data()
    joined = f"Вакансия:\n{data['vacancy']}\n\nПрофиль:\n{message.text}"
    await state.clear()
    result = await vacancy_match(joined)
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "courses")
async def courses_start(cb: CallbackQuery):
    text = "🎓 Подбор обучения — 99₽"
    await cb.message.edit_text(text, reply_markup=service_start_keyboard("COURSE_RECOMMEND_99", 99))


@dp.callback_query(F.data == "start_COURSE_RECOMMEND_99")
async def courses_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CoursesState.waiting_for_info)
    await cb.message.edit_text("Ваш уровень и цель?", reply_markup=process_keyboard())


@dp.message(CoursesState.waiting_for_info)
async def courses_process(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Чуть подробнее.", reply_markup=process_keyboard())
        return
    result = await course_recommendations(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
