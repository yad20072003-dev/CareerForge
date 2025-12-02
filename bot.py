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
    text = (
        "👋 Это «Кузница карьеры».\n\n"
        "Бот помогает:\n"
        "• понять, куда двигаться по карьере;\n"
        "• собрать сильное резюме под конкретную должность;\n"
        "• подготовиться к собеседованию и вопросам HR.\n\n"
        "Нажмите «Меню услуг», чтобы выбрать формат."
    )
    await message.answer(text, reply_markup=main_keyboard())


@dp.callback_query(F.data == "services_menu")
async def services_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Выберите услугу:", reply_markup=services_keyboard())


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Главное меню:", reply_markup=main_keyboard())


@dp.callback_query(F.data == "info")
async def info_block(cb: CallbackQuery):
    text = (
        "📌 Что делает «Кузница карьеры»:\n\n"
        "🧭 Профориентация — 149₽\n"
        "Разбор вашего опыта, интересов и характера. Итог: понятный портрет и список направлений, где вы можете раскрыться.\n\n"
        "📝 Создание резюме — 199₽\n"
        "Бот задаёт вопросы и собирает из ваших ответов готовое резюме под конкретную должность.\n\n"
        "🔍 Проверка резюме — 149₽\n"
        "Разбор вашего резюме глазами HR: что хорошо, что плохо, где риски, плюс улучшенная версия.\n\n"
        "🎤 HR-мок интервью — 199₽\n"
        "Вы присылаете вопросы и свои ответы, бот разбирает и показывает, как отвечать сильнее.\n\n"
        "📘 План на собеседование — 149₽\n"
        "Как себя вести, что подчеркивать, чего избегать, какие вопросы вам точно зададут.\n\n"
        "💬 Soft skills анализ — 129₽\n"
        "Разбор поведения, сильных и слабых сторон, рекомендации по развитию.\n\n"
        "📄 Анализ вакансии — 129₽\n"
        "Смотрим вакансию и ваш профиль, считаем match, показываем, чего не хватает.\n\n"
        "🎓 Подбор обучения — 129₽\n"
        "Что именно вам лучше учить сейчас и какие мини-проекты делать для прокачки."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "terms")
async def terms_block(cb: CallbackQuery):
    text = (
        "📜 Условия использования\n\n"
        "1. Бот предоставляет информационные услуги.\n"
        "2. Оплата будет происходить через официальные платёжные сервисы.\n"
        "3. Возврат возможен, если услуга не была оказана.\n"
        "4. Данные пользователей не передаются третьим лицам.\n"
        "5. Используя бота, вы соглашаетесь с этими условиями."
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
        f"{product['title']}\n\n"
        f"Цена: {product['amount']}₽\n\n"
        "Оплата временно недоступна. Как только ЮKassa будет подключена, здесь появится оплата.",
        reply_markup=back_button()
    )


@dp.callback_query(F.data == "career")
async def start_career(cb: CallbackQuery):
    text = (
        "🧭 Профориентация — 149₽\n\n"
        "Для тех, кто не до конца понимает, куда двигаться по карьере.\n"
        "Итог: разбор сильных сторон, рисков и список подходящих направлений.\n\n"
        "Можно оплатить позже и уже сейчас пройти разбор."
    )
    await cb.message.edit_text(
        text,
        reply_markup=service_start_keyboard("CAREER_ANALYSIS_149", 149)
    )


@dp.callback_query(F.data == "start_CAREER_ANALYSIS_149")
async def start_career_input(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CareerState.waiting_for_basic)
    await cb.message.edit_text(
        "Начнём. Скажите, сколько вам лет и чем вы сейчас занимаетесь (учёба, работа, перерыв).",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_basic)
async def career_basic(message: Message, state: FSMContext):
    await state.update_data(basic=message.text)
    await state.set_state(CareerState.waiting_for_education)
    await message.answer(
        "Расскажите про образование: где учитесь или учились, направление, курс или этап.",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_education)
async def career_education(message: Message, state: FSMContext):
    await state.update_data(education=message.text)
    await state.set_state(CareerState.waiting_for_experience)
    await message.answer(
        "Опишите ваш опыт: работа, стажировки, подработки, проекты. Что делали и что больше всего понравилось.",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_experience)
async def career_experience(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(CareerState.waiting_for_interests)
    await message.answer(
        "Что вам реально интересно по жизни и учёбе? Какие темы, задачи или активности вас цепляют.",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_interests)
async def career_interests(message: Message, state: FSMContext):
    await state.update_data(interests=message.text)
    await state.set_state(CareerState.waiting_for_preferences)
    await message.answer(
        "Какая работа вам ближе: с людьми, с цифрами, с текстами, с техникой, с креативом? Нравится стабильность или движ и изменения?",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_preferences)
async def career_preferences(message: Message, state: FSMContext):
    await state.update_data(preferences=message.text)
    await state.set_state(CareerState.waiting_for_goals)
    await message.answer(
        "Какие у вас цели на ближайшие 1–3 года по карьере или учёбе? Чего хотите добиться?",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_goals)
async def career_goals(message: Message, state: FSMContext):
    await state.update_data(goals=message.text)
    data = await state.get_data()
    user_text = (
        f"Базовая информация: {data.get('basic')}\n\n"
        f"Образование: {data.get('education')}\n\n"
        f"Опыт: {data.get('experience')}\n\n"
        f"Интересы: {data.get('interests')}\n\n"
        f"Предпочтения: {data.get('preferences')}\n\n"
        f"Цели: {data.get('goals')}"
    )
    await state.clear()
    result = await make_career_report(user_text)
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "resume_create")
async def start_resume(cb: CallbackQuery):
    text = (
        "📝 Создание резюме — 199₽\n\n"
        "Подходит, если нужно нормальное резюме под конкретную должность.\n"
        "Бот задаст ряд вопросов и соберёт из ваших ответов готовый текст резюме.\n\n"
        "Можно оплатить позже и пройти услугу сейчас."
    )
    await cb.message.edit_text(
        text,
        reply_markup=service_start_keyboard("RESUME_CREATE_199", 199)
    )


@dp.callback_query(F.data == "start_RESUME_CREATE_199")
async def begin_resume(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ResumeCreateState.waiting_for_position)
    await cb.message.edit_text(
        "Для начала: под какую должность или направление делаем резюме?",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_position)
async def resume_position(message: Message, state: FSMContext):
    await state.update_data(position=message.text)
    await state.set_state(ResumeCreateState.waiting_for_contacts)
    await message.answer(
        "Теперь укажите город и контакты: телефон, email, Telegram (что готовы указать в резюме).",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_contacts)
async def resume_contacts(message: Message, state: FSMContext):
    await state.update_data(contacts=message.text)
    await state.set_state(ResumeCreateState.waiting_for_experience)
    await message.answer(
        "Опишите опыт: работа, стажировки, подработки. Для каждого места: где, когда, кем и что делали.",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_experience)
async def resume_experience(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(ResumeCreateState.waiting_for_education)
    await message.answer(
        "Расскажите про образование: вуз/колледж/курсы, направления, годы.",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_education)
async def resume_education(message: Message, state: FSMContext):
    await state.update_data(education=message.text)
    await state.set_state(ResumeCreateState.waiting_for_skills)
    await message.answer(
        "Теперь перечислите ваши ключевые навыки: и технические (hard), и личные (soft).",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_skills)
async def resume_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(ResumeCreateState.waiting_for_projects)
    await message.answer(
        "Есть ли проекты или достижения, которыми вы гордитесь? Учебные, личные, рабочие — опишите.",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_projects)
async def resume_projects(message: Message, state: FSMContext):
    await state.update_data(projects=message.text)
    await state.set_state(ResumeCreateState.waiting_for_extra)
    await message.answer(
        "Добавьте дополнительную информацию: языки, важные курсы, формат работы, что хотите подчеркнуть.",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_extra)
async def resume_extra(message: Message, state: FSMContext):
    await state.update_data(extra=message.text)
    data = await state.get_data()
    user_text = (
        f"Целевая должность: {data.get('position')}\n\n"
        f"Контакты и город: {data.get('contacts')}\n\n"
        f"Опыт: {data.get('experience')}\n\n"
        f"Образование: {data.get('education')}\n\n"
        f"Навыки: {data.get('skills')}\n\n"
        f"Проекты и достижения: {data.get('projects')}\n\n"
        f"Дополнительно: {data.get('extra')}"
    )
    await state.clear()
    result = await make_resume(user_text)
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "resume_check")
async def start_resume_check(cb: CallbackQuery):
    await cb.message.edit_text(
        "🔍 Проверка резюме — 149₽\n\n"
        "Пришлите текст резюме, бот разберёт его как HR: сильные и слабые стороны, риски и улучшенный вариант.",
        reply_markup=service_start_keyboard("RESUME_CHECK_149", 149)
    )


@dp.callback_query(F.data == "start_RESUME_CHECK_149")
async def begin_resume_check(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ResumeCheckState.waiting_for_resume)
    await cb.message.edit_text(
        "Отправьте текст резюме одним сообщением.",
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
        "🎤 HR-мок интервью — 199₽\n\n"
        "Вы присылаете пример диалога: вопросы HR и ваши ответы. Бот разбирает, где вы проседаете и как отвечать сильнее.",
        reply_markup=service_start_keyboard("MOCK_INTERVIEW_199", 199)
    )


@dp.callback_query(F.data == "start_MOCK_INTERVIEW_199")
async def mock_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(MockInterviewState.waiting_for_dialog)
    await cb.message.edit_text(
        "Скопируйте сюда пример диалога: вопросы HR и ваши ответы.",
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
        "📘 План поведения — 149₽\n\n"
        "Помогает понять, как вести себя на собеседовании, что говорить, чего избегать и к каким вопросам готовиться.",
        reply_markup=service_start_keyboard("INTERVIEW_PLAN_149", 149)
    )


@dp.callback_query(F.data == "start_INTERVIEW_PLAN_149")
async def plan_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(InterviewPlanState.waiting_for_info)
    await cb.message.edit_text(
        "Опишите: должность, тип компании, ваши сильные стороны и страхи перед собеседованием.",
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
        "💬 Soft skills анализ — 129₽\n\n"
        "Разбираем, как вы ведёте себя в команде, в стрессовых ситуациях и конфликтах.",
        reply_markup=service_start_keyboard("SOFT_ANALYSIS_129", 129)
    )


@dp.callback_query(F.data == "start_SOFT_ANALYSIS_129")
async def soft_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(SoftSkillsState.waiting_for_answers)
    await cb.message.edit_text(
        "Опишите несколько ситуаций: работа в команде, конфликт, дедлайн, критика. Как вы себя вели?",
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
        "📄 Анализ вакансии — 129₽\n\n"
        "Смотрим текст вакансии и ваш профиль, оцениваем соответствие и показываем, чего не хватает.",
        reply_markup=service_start_keyboard("VACANCY_MATCH_129", 129)
    )


@dp.callback_query(F.data == "start_VACANCY_MATCH_129")
async def vacancy_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
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
        "Теперь опишите ваш опыт и навыки, которые вы хотите сопоставить с этой вакансией.",
        reply_markup=process_keyboard()
    )


@dp.message(VacancyMatchState.waiting_for_profile)
async def vacancy_part2(message: Message, state: FSMContext):
    data = await state.get_data()
    joined = f"Вакансия:\n{data['vacancy']}\n\nПрофиль:\n{message.text}"
    await state.clear()
    result = await vacancy_match(joined)
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "courses")
async def courses_start(cb: CallbackQuery):
    await cb.message.edit_text(
        "🎓 Подбор обучения — 129₽\n\n"
        "Понимаем, откуда вы стартуете и куда хотите прийти, и даём понятный план обучения и мини-проектов.",
        reply_markup=service_start_keyboard("COURSE_RECOMMEND_129", 129)
    )


@dp.callback_query(F.data == "start_COURSE_RECOMMEND_129")
async def courses_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CoursesState.waiting_for_info)
    await cb.message.edit_text(
        "Опишите ваш текущий уровень и цель: кем хотите работать или какие задачи уметь решать.",
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
