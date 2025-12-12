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
        "• выбрать направление и сильные стороны,\n"
        "• собрать резюме под вакансию,\n"
        "• подготовиться к собеседованию.\n\n"
        "Выберите, что у вас сейчас актуально."
    )
    await message.answer(text, reply_markup=main_keyboard())


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Главное меню:", reply_markup=main_keyboard())


@dp.callback_query(F.data == "scenario_profession")
async def scenario_profession(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "🎯 Выбор направления.\n\nДля тех, кто хочет понять, где он будет расти быстрее всего."
    await cb.message.edit_text(text, reply_markup=scenario_profession_keyboard())


@dp.callback_query(F.data == "scenario_job")
async def scenario_job(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "💼 Поиск работы.\n\nРезюме, проверка, вакансии и обучение под цель."
    await cb.message.edit_text(text, reply_markup=scenario_job_keyboard())


@dp.callback_query(F.data == "scenario_interview")
async def scenario_interview(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "🗣 Подготовка к собеседованию.\n\nТренировки, план поведения, разбор слабых мест."
    await cb.message.edit_text(text, reply_markup=scenario_interview_keyboard())


@dp.callback_query(F.data == "free_menu")
async def free_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "🆓 Бесплатные материалы.\n\nВыберите категорию:"
    await cb.message.edit_text(text, reply_markup=free_keyboard())


@dp.callback_query(F.data == "free_mini_resume")
async def free_mini_resume(cb: CallbackQuery):
    text = (
        "⚡ Мини-советы по резюме:\n\n"
        "• один заголовок под должность;\n"
        "• опыт = задачи + результаты;\n"
        "• без воды в навыках;\n"
        "• hard и soft отдельно;\n"
        "• адаптируйте резюме под вакансии."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "free_checklist")
async def free_checklist(cb: CallbackQuery):
    text = (
        "📌 Чек-лист к собеседованию:\n\n"
        "• коротко рассказываю о себе;\n"
        "• есть примеры задач и достижений;\n"
        "• понимаю, почему хочу в эту компанию;\n"
        "• подготовил вопросы работодателю;\n"
        "• проверил технику, если онлайн."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "free_tips")
async def free_tips(cb: CallbackQuery):
    text = (
        "🔎 Советы по поиску работы:\n\n"
        "• откликайтесь на смежные роли;\n"
        "• ведите учёт откликов;\n"
        "• пишите в интересные компании напрямую;\n"
        "• не делайте выводы по 3–5 отказам."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "services_menu")
async def services_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Выберите услугу:", reply_markup=services_keyboard())


@dp.callback_query(F.data == "info")
async def info_block(cb: CallbackQuery):
    text = (
        "ℹ️ О боте.\n\n"
        "«Кузница карьеры» помогает понять направление, собрать резюме и подготовиться к собеседованию.\n"
        "Формат — живые разборы и понятные рекомендации."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "terms")
async def terms_block(cb: CallbackQuery):
    text = (
        "📜 Условия использования:\n\n"
        "1. Бот даёт информационные консультации.\n"
        "2. Оплата будет подключена через официальные сервисы.\n"
        "3. Возврат возможен, если услуга фактически не оказана.\n"
        "4. Данные пользователей не передаются третьим лицам."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "back_step")
async def back_step(cb: CallbackQuery, state: FSMContext):
    current = await state.get_state()
    if not current:
        await cb.message.edit_text("Главное меню:", reply_markup=main_keyboard())
        return

    mapping = {
        CareerState.waiting_for_education.state: (
            CareerState.waiting_for_basic,
            "Сколько вам лет и чем вы занимаетесь?"
        ),
        CareerState.waiting_for_experience.state: (
            CareerState.waiting_for_education,
            "Расскажите про образование."
        ),
        CareerState.waiting_for_interests.state: (
            CareerState.waiting_for_experience,
            "Опишите ваш опыт подробнее."
        ),
        CareerState.waiting_for_preferences.state: (
            CareerState.waiting_for_interests,
            "Что вам интересно по жизни?"
        ),
        CareerState.waiting_for_goals.state: (
            CareerState.waiting_for_preferences,
            "Какая работа вам ближе?"
        ),
        ResumeCreateState.waiting_for_contacts.state: (
            ResumeCreateState.waiting_for_position,
            "Под какую должность делаем резюме?"
        ),
        ResumeCreateState.waiting_for_experience.state: (
            ResumeCreateState.waiting_for_contacts,
            "Укажите город и контакты."
        ),
        ResumeCreateState.waiting_for_education.state: (
            ResumeCreateState.waiting_for_experience,
            "Опишите ваш опыт."
        ),
        ResumeCreateState.waiting_for_skills.state: (
            ResumeCreateState.waiting_for_education,
            "Расскажите про образование."
        ),
        ResumeCreateState.waiting_for_projects.state: (
            ResumeCreateState.waiting_for_skills,
            "Перечислите ваши навыки."
        ),
        ResumeCreateState.waiting_for_extra.state: (
            ResumeCreateState.waiting_for_projects,
            "Опишите проекты и достижения."
        ),
    }

    if current in (
        MockInterviewState.waiting_for_position.state,
        MockInterviewState.waiting_for_experience.state,
        MockInterviewState.waiting_for_goals.state,
        MockInterviewState.in_interview.state,
    ):
        await cb.answer("В мок-интервью возврат недоступен.", show_alert=True)
        return

    if current in mapping:
        new_state, question = mapping[current]
        await state.set_state(new_state)
        await cb.message.edit_text(question, reply_markup=process_keyboard())
        return

    await state.clear()
    await cb.message.edit_text("Главное меню:", reply_markup=main_keyboard())


@dp.callback_query(F.data == "career")
async def start_career(cb: CallbackQuery):
    product = PRODUCTS["CAREER_ANALYSIS_149"]
    text = (
        f"{product['title']} — {product['amount']}₽\n\n"
        "Разбор ваших сильных сторон, интересов и направлений, где вы быстрее всего вырастете и начнёте зарабатывать."
    )
    await cb.message.edit_text(
        text,
        reply_markup=service_start_keyboard(product["code"], product["amount"])
    )


@dp.callback_query(F.data == "start_CAREER_ANALYSIS_149")
async def start_career_input(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CareerState.waiting_for_basic)
    await cb.message.edit_text(
        "Сколько вам лет и чем вы сейчас занимаетесь (учёба, работа, перерыв)?",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_basic)
async def career_basic(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Напишите чуть подробнее, чтобы было за что зацепиться.", reply_markup=process_keyboard())
        return
    await state.update_data(basic=message.text)
    await state.set_state(CareerState.waiting_for_education)
    await message.answer("Расскажите про образование: где, на кого, какие годы.", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_education)
async def career_education(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте деталей по образованию.", reply_markup=process_keyboard())
        return
    await state.update_data(education=message.text)
    await state.set_state(CareerState.waiting_for_experience)
    await message.answer("Опишите ваш опыт: работа, стажировки, подработки, проекты.", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_experience)
async def career_experience(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно немного подробнее по опыту.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(CareerState.waiting_for_interests)
    await message.answer("Что вам реально интересно по жизни и учёбе?", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_interests)
async def career_interests(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Попробуйте описать, от чего вы по-хорошему загораетесь.", reply_markup=process_keyboard())
        return
    await state.update_data(interests=message.text)
    await state.set_state(CareerState.waiting_for_preferences)
    await message.answer("Какая работа вам ближе: с людьми, цифрами, текстами, техникой, креативом?", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_preferences)
async def career_preferences(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Чуть конкретнее по предпочтениям.", reply_markup=process_keyboard())
        return
    await state.update_data(preferences=message.text)
    await state.set_state(CareerState.waiting_for_goals)
    await message.answer("Какие у вас цели на 1–3 года по деньгам и по жизни?", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_goals)
async def career_goals(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Опишите цели подробнее: уровень дохода, стиль жизни, роль.", reply_markup=process_keyboard())
        return
    await state.update_data(goals=message.text)
    data = await state.get_data()
    user_text = (
        f"Базовая информация: {data['basic']}\n\n"
        f"Образование: {data['education']}\n\n"
        f"Опыт: {data['experience']}\n\n"
        f"Интересы: {data['interests']}\n\n"
        f"Предпочтения: {data['preferences']}\n\n"
        f"Цели на 1–3 года: {data['goals']}"
    )
    await state.clear()
    result = await make_career_report(user_text)
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "resume_create")
async def start_resume(cb: CallbackQuery):
    product = PRODUCTS["RESUME_CREATE_199"]
    text = (
        f"{product['title']} — {product['amount']}₽\n\n"
        "Соберём резюме под конкретную цель: структура, формулировки, достижения и навыки."
    )
    await cb.message.edit_text(text, reply_markup=service_start_keyboard(product["code"], product["amount"]))


@dp.callback_query(F.data == "start_RESUME_CREATE_199")
async def begin_resume(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ResumeCreateState.waiting_for_position)
    await cb.message.edit_text("Под какую должность или направление делаем резюме?", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_position)
async def resume_position(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Чуть детальнее опишите должность или тип вакансии.", reply_markup=process_keyboard())
        return
    await state.update_data(position=message.text)
    await state.set_state(ResumeCreateState.waiting_for_contacts)
    await message.answer("Укажите город и контакты (телефон, почта, Telegram).", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_contacts)
async def resume_contacts(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно указать хотя бы город и один контакт.", reply_markup=process_keyboard())
        return
    await state.update_data(contacts=message.text)
    await state.set_state(ResumeCreateState.waiting_for_experience)
    await message.answer("Опишите ваш опыт: места работы, период, задачи и результаты.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_experience)
async def resume_experience(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте чуть больше деталей по опыту.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(ResumeCreateState.waiting_for_education)
    await message.answer("Расскажите про образование и важные курсы.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_education)
async def resume_education(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно чуть подробнее по образованию.", reply_markup=process_keyboard())
        return
    await state.update_data(education=message.text)
    await state.set_state(ResumeCreateState.waiting_for_skills)
    await message.answer("Перечислите ваши ключевые навыки: hard и soft.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_skills)
async def resume_skills(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно указать хотя бы несколько навыков.", reply_markup=process_keyboard())
        return
    await state.update_data(skills=message.text)
    await state.set_state(ResumeCreateState.waiting_for_projects)
    await message.answer("Опишите проекты и достижения, которыми вы гордитесь.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_projects)
async def resume_projects(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте пару примеров проектов или достижений.", reply_markup=process_keyboard())
        return
    await state.update_data(projects=message.text)
    await state.set_state(ResumeCreateState.waiting_for_extra)
    await message.answer("Дополнительно: форматы работы, языки, ожидания и важные детали.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_extra)
async def resume_extra(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Напишите ещё немного, чтобы было, что подчеркнуть.", reply_markup=process_keyboard())
        return
    await state.update_data(extra=message.text)
    data = await state.get_data()
    user_text = (
        f"Целевая должность: {data['position']}\n\n"
        f"Контакты и город: {data['contacts']}\n\n"
        f"Опыт: {data['experience']}\n\n"
        f"Образование: {data['education']}\n\n"
        f"Навыки: {data['skills']}\n\n"
        f"Проекты и достижения: {data['projects']}\n\n"
        f"Дополнительные детали: {data['extra']}"
    )
    await state.clear()
    result = await make_resume(user_text)
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "resume_check")
async def start_resume_check(cb: CallbackQuery):
    product = PRODUCTS["RESUME_CHECK_149"]
    text = (
        f"{product['title']} — {product['amount']}₽\n\n"
        "Пришлите текст резюме, а я разберу его как HR: сильные стороны, ошибки и примеры улучшений."
    )
    await cb.message.edit_text(text, reply_markup=service_start_keyboard(product["code"], product["amount"]))


@dp.callback_query(F.data == "start_RESUME_CHECK_149")
async def begin_resume_check(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ResumeCheckState.waiting_for_resume)
    await cb.message.edit_text("Пришлите текст вашего резюме одним сообщением.", reply_markup=process_keyboard())


@dp.message(ResumeCheckState.waiting_for_resume)
async def resume_check_step(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно прислать полный текст резюме.", reply_markup=process_keyboard())
        return
    result = await check_resume(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "mock")
async def mock_start(cb: CallbackQuery):
    product = PRODUCTS["MOCK_INTERVIEW_199"]
    text = (
        f"{product['title']} — {product['amount']}₽\n\n"
        "Реалистичное тренировочное собеседование: вопросы, разбор ответов и финальное резюме от HR."
    )
    await cb.message.edit_text(text, reply_markup=service_start_keyboard(product["code"], product["amount"]))


@dp.callback_query(F.data == "start_MOCK_INTERVIEW_199")
async def mock_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(MockInterviewState.waiting_for_position)
    await cb.message.edit_text(
        "На какую должность вы готовитесь и какой примерно уровень компании?",
        reply_markup=process_keyboard()
    )


@dp.message(MockInterviewState.waiting_for_position)
async def mock_position(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Опишите должность и уровень компании подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(position=message.text)
    await state.set_state(MockInterviewState.waiting_for_experience)
    await message.answer(
        "Опишите ваш реальный опыт под эту роль: работа, стажировки, проекты и результаты.",
        reply_markup=process_keyboard()
    )


@dp.message(MockInterviewState.waiting_for_experience)
async def mock_experience(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно привести хотя бы пару примеров задач и результатов.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(MockInterviewState.waiting_for_goals)
    await message.answer(
        "Какие у вас цели и страхи перед собеседованием? Чего хотите добиться и чего боитесь?",
        reply_markup=process_keyboard()
    )


@dp.message(MockInterviewState.waiting_for_goals)
async def mock_goals(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Опишите честно свои ожидания и переживания.", reply_markup=process_keyboard())
        return
    data = await state.get_data()
    position = data["position"]
    experience = data["experience"]
    goals = message.text
    await state.update_data(goals=goals, dialog="", step=1)
    payload = (
        "РЕЖИМ: start\n\n"
        f"Целевая должность: {position}\n\n"
        f"Опыт кандидата: {experience}\n\n"
        f"Цели и страхи кандидата: {goals}\n\n"
        "Сформируй короткое приветствие и первый вопрос для тренировочного интервью."
    )
    reply = await hr_mock_interview(payload)
    await state.set_state(MockInterviewState.in_interview)
    await message.answer(reply, reply_markup=process_keyboard())


@dp.message(MockInterviewState.in_interview)
async def mock_step(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Попробуйте ответить так, как на реальном собеседовании.", reply_markup=process_keyboard())
        return
    data = await state.get_data()
    step = data["step"]
    position = data["position"]
    experience = data["experience"]
    goals = data["goals"]
    dialog = data["dialog"] + f"Ответ кандидата на шаге {step}:\n{message.text}\n\n"
    if step < MAX_MOCK_STEPS:
        payload = (
            "РЕЖИМ: step\n\n"
            f"Текущий шаг: {step}\n\n"
            f"Целевая должность: {position}\n\n"
            f"Опыт кандидата: {experience}\n\n"
            f"Цели и страхи кандидата: {goals}\n\n"
            f"История ответов кандидата:\n{dialog}\n\n"
            "Оцени последний ответ кандидата, дай честный, но конструктивный разбор и задай следующий вопрос."
        )
        reply = await hr_mock_interview(payload)
        await state.update_data(step=step + 1, dialog=dialog)
        await message.answer(reply, reply_markup=process_keyboard())
    else:
        payload = (
            "РЕЖИМ: summary\n\n"
            f"Целевая должность: {position}\n\n"
            f"Опыт кандидата: {experience}\n\n"
            f"Цели и страхи кандидата: {goals}\n\n"
            f"История ответов кандидата:\n{dialog}\n\n"
            "Сделай итоговое резюме собеседования: сильные стороны, слабые места, риски и конкретные рекомендации."
        )
        reply = await hr_mock_interview(payload)
        await state.clear()
        await message.answer(reply, reply_markup=main_keyboard())


@dp.callback_query(F.data == "interview_plan")
async def plan_start(cb: CallbackQuery):
    product = PRODUCTS["INTERVIEW_PLAN_149"]
    text = (
        f"{product['title']} — {product['amount']}₽\n\n"
        "План, как вести себя на собеседовании: ответы, акценты, ошибки, вопросы работодателю."
    )
    await cb.message.edit_text(text, reply_markup=service_start_keyboard(product["code"], product["amount"]))


@dp.callback_query(F.data == "start_INTERVIEW_PLAN_149")
async def plan_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(InterviewPlanState.waiting_for_info)
    await cb.message.edit_text(
        "Опишите должность, компанию, свои сильные стороны и страхи перед собеседованием.",
        reply_markup=process_keyboard()
    )


@dp.message(InterviewPlanState.waiting_for_info)
async def plan_process(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно чуть больше деталей по вакансии и вам.", reply_markup=process_keyboard())
        return
    result = await interview_plan(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "soft")
async def soft_start(cb: CallbackQuery):
    product = PRODUCTS["SOFT_ANALYSIS_99"]
    text = (
        f"{product['title']} — {product['amount']}₽\n\n"
        "Разберём, как вы ведёте себя в команде, при конфликтах, дедлайнах и критике."
    )
    await cb.message.edit_text(text, reply_markup=service_start_keyboard(product["code"], product["amount"]))


@dp.callback_query(F.data == "start_SOFT_ANALYSIS_99")
async def soft_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(SoftSkillsState.waiting_for_answers)
    await cb.message.edit_text(
        "Опишите несколько ситуаций: работа в команде, конфликт, жёсткий дедлайн, критика. Как вы себя вели?",
        reply_markup=process_keyboard()
    )


@dp.message(SoftSkillsState.waiting_for_answers)
async def soft_process(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Важно описать реальные ситуации и ваше поведение.", reply_markup=process_keyboard())
        return
    result = await soft_analysis(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "vacancy")
async def vacancy_start(cb: CallbackQuery):
    product = PRODUCTS["VACANCY_MATCH_99"]
    text = (
        f"{product['title']} — {product['amount']}₽\n\n"
        "Разберём текст вакансии и ваш профиль: совпадения, пробелы, риски и как усилиться."
    )
    await cb.message.edit_text(text, reply_markup=service_start_keyboard(product["code"], product["amount"]))


@dp.callback_query(F.data == "start_VACANCY_MATCH_99")
async def vacancy_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(VacancyMatchState.waiting_for_vacancy)
    await cb.message.edit_text("Пришлите текст вакансии.", reply_markup=process_keyboard())


@dp.message(VacancyMatchState.waiting_for_vacancy)
async def vacancy_part1(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно прислать полный текст вакансии.", reply_markup=process_keyboard())
        return
    await state.update_data(vacancy=message.text)
    await state.set_state(VacancyMatchState.waiting_for_profile)
    await message.answer("Теперь опишите ваш опыт и навыки под эту вакансию.", reply_markup=process_keyboard())


@dp.message(VacancyMatchState.waiting_for_profile)
async def vacancy_part2(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно чуть подробнее по вашему опыту и навыкам.", reply_markup=process_keyboard())
        return
    data = await state.get_data()
    full = f"Вакансия:\n{data['vacancy']}\n\nПрофиль кандидата:\n{message.text}"
    await state.clear()
    result = await vacancy_match(full)
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "courses")
async def courses_start(cb: CallbackQuery):
    product = PRODUCTS["COURSE_RECOMMEND_99"]
    text = (
        f"{product['title']} — {product['amount']}₽\n\n"
        "Подберём стратегию обучения под вашу цель: темы, форматы, мини-проекты и как это продать работодателю."
    )
    await cb.message.edit_text(text, reply_markup=service_start_keyboard(product["code"], product["amount"]))


@dp.callback_query(F.data == "start_COURSE_RECOMMEND_99")
async def courses_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CoursesState.waiting_for_info)
    await cb.message.edit_text(
        "Опишите ваш текущий уровень и цель: кем хотите работать или какие задачи уметь решать.",
        reply_markup=process_keyboard()
    )


@dp.message(CoursesState.waiting_for_info)
async def courses_process(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно немного подробнее по уровню и цели.", reply_markup=process_keyboard())
        return
    result = await course_recommendations(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "pack_start_career")
async def pack_start_career(cb: CallbackQuery):
    text = (
        "🎁 Пакет «Старт карьеры» — 399₽\n\n"
        "Профориентация, создание резюме и план на собеседование.\n"
        "Пока услуги доступны по отдельности, позже добавим оплату пакетом."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "pack_before_interview")
async def pack_before_interview(cb: CallbackQuery):
    text = (
        "🎯 Пакет «Перед собесом» — 449₽\n\n"
        "Проверка резюме, анализ вакансии, план и мок-интервью.\n"
        "Сейчас можно пройти эти шаги отдельными услугами."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "pack_max")
async def pack_max(cb: CallbackQuery):
    text = (
        "🏆 Пакет «Максимум» — 699₽\n\n"
        "Полный цикл от выбора направления до подготовки к выходу на рынок.\n"
        "Пока реализован через набор отдельных услуг."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
