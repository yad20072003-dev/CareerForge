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
MAX_MOCK_STEPS = 30

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def is_answer_too_short(text: str) -> bool:
    if not text:
        return True
    t = text.strip()
    if len(t) < 10:
        return True
    return False


@dp.message(CommandStart())
async def start_cmd(message: Message):
    text = (
        "👋 Это «Кузница карьеры».\n\n"
        "Бот помогает:\n"
        "• выбрать направление по интересам и сильным сторонам;\n"
        "• собрать рабочее резюме под конкретную должность;\n"
        "• подготовиться к собеседованию и сложным вопросам HR.\n\n"
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
    text = (
        "🎯 Выбор профессии.\n\n"
        "Здесь можно:\n"
        "• разобраться с направлением и ролями,\n"
        "• посмотреть, какие сферы вам ближе,\n"
        "• подобрать обучение и мягко зайти в профессию."
    )
    await cb.message.edit_text(text, reply_markup=scenario_profession_keyboard())


@dp.callback_query(F.data == "scenario_job")
async def scenario_job(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "💼 Поиск работы.\n\n"
        "Здесь бот помогает:\n"
        "• собрать резюме под вакансию,\n"
        "• проверить текущее резюме,\n"
        "• разобраться с вакансиями и обучением под цель."
    )
    await cb.message.edit_text(text, reply_markup=scenario_job_keyboard())


@dp.callback_query(F.data == "scenario_interview")
async def scenario_interview(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "🗣 Подготовка к собеседованию.\n\n"
        "Здесь можно:\n"
        "• пройти HR-мок интервью,\n"
        "• получить план поведения и ответов,\n"
        "• проверить резюме и вакансию перед выходом."
    )
    await cb.message.edit_text(text, reply_markup=scenario_interview_keyboard())


@dp.callback_query(F.data == "free_menu")
async def free_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "🆓 Бесплатный раздел.\n\n"
        "Здесь собраны базовые материалы:\n"
        "• мини-советы по резюме,\n"
        "• чек-лист к собеседованию,\n"
        "• рекомендации по поиску работы."
    )
    await cb.message.edit_text(text, reply_markup=free_keyboard())


@dp.callback_query(F.data == "free_mini_resume")
async def free_mini_resume(cb: CallbackQuery):
    text = (
        "⚡ Мини-советы по резюме:\n\n"
        "1) Один понятный заголовок под должность.\n"
        "2) В опыте: задачи и результаты, а не только обязанности.\n"
        "3) Уберите воду: «ответственный, коммуникабельный» без примеров.\n"
        "4) Навыки разделите на hard и soft.\n"
        "5) Проверьте, совпадает ли резюме с вакансиями, куда откликаетесь."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "free_checklist")
async def free_checklist(cb: CallbackQuery):
    text = (
        "📌 Чек-лист к собеседованию:\n\n"
        "• могу спокойно рассказать о себе за 1–2 минуты;\n"
        "• есть 2–3 примера задач и достижений;\n"
        "• знаю, почему хочу именно в эту компанию;\n"
        "• могу назвать свои сильные и слабые стороны без клише;\n"
        "• подготовил вопросы работодателю;\n"
        "• проверил технику и связь, если собес онлайн."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "free_tips")
async def free_tips(cb: CallbackQuery):
    text = (
        "🔎 Советы по поиску:\n\n"
        "• откликайтесь не только на «мечту», но и на смежные роли;\n"
        "• подгоняйте резюме под тип вакансий, а не под одну штуку;\n"
        "• сохраняйте интересные компании и пишите им напрямую;\n"
        "• фиксируйте, где откликались и что ответили;\n"
        "• не делайте выводы по 3–5 откликам, это слишком маленькая выборка."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "services_menu")
async def services_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Выберите услугу:", reply_markup=services_keyboard())


@dp.callback_query(F.data == "info")
async def info_block(cb: CallbackQuery):
    text = (
        "ℹ️ О боте «Кузница карьеры»\n\n"
        "Бот создан, чтобы закрыть три задачи:\n"
        "1) Понять, куда двигаться по карьере.\n"
        "2) Собрать резюме, которое не стыдно отправить.\n"
        "3) Не провалиться на собеседовании.\n\n"
        "Все разборы делаются в формате живого диалога, а не сухих чек-листов."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "terms")
async def terms_block(cb: CallbackQuery):
    text = (
        "📜 Условия использования\n\n"
        "1. Бот даёт информационные консультации, а не юридические гарантии трудоустройства.\n"
        "2. Оплата происходит через официальные платёжные сервисы.\n"
        "3. Возврат возможен, если услуга фактически не была оказана.\n"
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
        "Оплата через ЮKassa будет доступна позже. Сейчас можно протестировать услугу без оплаты.",
        reply_markup=back_button()
    )


@dp.callback_query(F.data == "back_step")
async def back_step(cb: CallbackQuery, state: FSMContext):
    current = await state.get_state()
    if current is None:
        await cb.message.edit_text("Главное меню:", reply_markup=main_keyboard())
        return

    if current == CareerState.waiting_for_education.state:
        await state.set_state(CareerState.waiting_for_basic)
        await cb.message.edit_text(
            "Сколько вам лет и чем вы сейчас занимаетесь (учёба, работа, перерыв)?",
            reply_markup=process_keyboard()
        )
    elif current == CareerState.waiting_for_experience.state:
        await state.set_state(CareerState.waiting_for_education)
        await cb.message.edit_text(
            "Расскажите про образование: вуз/колледж/курсы, направление, годы.",
            reply_markup=process_keyboard()
        )
    elif current == CareerState.waiting_for_interests.state:
        await state.set_state(CareerState.waiting_for_experience)
        await cb.message.edit_text(
            "Опишите ваш опыт: работа, стажировки, подработки, проекты. Что делали и что больше всего понравилось.",
            reply_markup=process_keyboard()
        )
    elif current == CareerState.waiting_for_preferences.state:
        await state.set_state(CareerState.waiting_for_interests)
        await cb.message.edit_text(
            "Что вам реально интересно по жизни и учёбе? Какие темы, задачи или активности вас цепляют.",
            reply_markup=process_keyboard()
        )
    elif current == CareerState.waiting_for_goals.state:
        await state.set_state(CareerState.waiting_for_preferences)
        await cb.message.edit_text(
            "Какая работа вам ближе: с людьми, с цифрами, с текстами, с техникой, с креативом? Нравится стабильность или постоянные изменения?",
            reply_markup=process_keyboard()
        )
    elif current == ResumeCreateState.waiting_for_contacts.state:
        await state.set_state(ResumeCreateState.waiting_for_position)
        await cb.message.edit_text(
            "Под какую должность или направление делаем резюме? Можно указать пример вакансии.",
            reply_markup=process_keyboard()
        )
    elif current == ResumeCreateState.waiting_for_experience.state:
        await state.set_state(ResumeCreateState.waiting_for_contacts)
        await cb.message.edit_text(
            "Укажите город и контакты: телефон, email, Telegram (то, что готовы указать в резюме).",
            reply_markup=process_keyboard()
        )
    elif current == ResumeCreateState.waiting_for_education.state:
        await state.set_state(ResumeCreateState.waiting_for_experience)
        await cb.message.edit_text(
            "Опишите опыт: все места работы/стажировок. Для каждого: период, компания, должность, задачи и результаты.",
            reply_markup=process_keyboard()
        )
    elif current == ResumeCreateState.waiting_for_skills.state:
        await state.set_state(ResumeCreateState.waiting_for_education)
        await cb.message.edit_text(
            "Расскажите про образование: вуз/колледж, направление, годы. Плюс важные курсы, если есть.",
            reply_markup=process_keyboard()
        )
    elif current == ResumeCreateState.waiting_for_projects.state:
        await state.set_state(ResumeCreateState.waiting_for_skills)
        await cb.message.edit_text(
            "Перечислите ваши ключевые навыки: отдельными блоками hard (профнавыки) и soft (личные).",
            reply_markup=process_keyboard()
        )
    elif current == ResumeCreateState.waiting_for_extra.state:
        await state.set_state(ResumeCreateState.waiting_for_projects)
        await cb.message.edit_text(
            "Опишите проекты и достижения, которыми вы гордитесь: учебные, рабочие, личные.",
            reply_markup=process_keyboard()
        )
    elif current in (
        MockInterviewState.waiting_for_position.state,
        MockInterviewState.waiting_for_experience.state,
        MockInterviewState.waiting_for_goals.state,
        MockInterviewState.in_interview.state,
    ):
        await cb.answer("В мок-интервью шаг назад недоступен, продолжайте отвечать.", show_alert=True)
    else:
        await state.clear()
        await cb.message.edit_text("Главное меню:", reply_markup=main_keyboard())


@dp.callback_query(F.data == "career")
async def start_career(cb: CallbackQuery):
    text = (
        "🧭 Профориентация — 149₽\n\n"
        "Подходит, если вы не до конца понимаете, куда двигаться по карьере.\n"
        "Итог: разбор сильных сторон, рисков и направлений, где вы можете раскрыться."
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
        "Сколько вам лет и чем вы сейчас занимаетесь (учёба, работа, перерыв)?",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_basic)
async def career_basic(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно чуть подробнее, чтобы я мог понять вашу ситуацию.", reply_markup=process_keyboard())
        return
    await state.update_data(basic=message.text)
    await state.set_state(CareerState.waiting_for_education)
    await message.answer(
        "Расскажите про образование: вуз/колледж/курсы, направление, годы. Что вам там нравилось, а что нет.",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_education)
async def career_education(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте немного деталей: место, направление, годы, что запомнилось.", reply_markup=process_keyboard())
        return
    await state.update_data(education=message.text)
    await state.set_state(CareerState.waiting_for_experience)
    await message.answer(
        "Опишите ваш опыт: работа, стажировки, подработки, проекты. Для каждого: чем занимались и что получилось лучше всего.",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_experience)
async def career_experience(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Опишите опыт чуть подробнее: где, кем, какие задачи и результаты.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(CareerState.waiting_for_interests)
    await message.answer(
        "Что вам реально интересно по жизни и учёбе? Темы, задачи или активности, от которых вы ловите кайф.",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_interests)
async def career_interests(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Напишите честно, что вас цепляет, даже если это кажется несерьёзным.", reply_markup=process_keyboard())
        return
    await state.update_data(interests=message.text)
    await state.set_state(CareerState.waiting_for_preferences)
    await message.answer(
        "Какая работа вам ближе: с людьми, с цифрами, с текстами, с техникой, с креативом? Нравится стабильность или постоянные изменения?",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_preferences)
async def career_preferences(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Чуть конкретнее: с чем вы точно не хотите работать и что вам кажется комфортным.", reply_markup=process_keyboard())
        return
    await state.update_data(preferences=message.text)
    await state.set_state(CareerState.waiting_for_goals)
    await message.answer(
        "Какие у вас цели на ближайшие 1–3 года по карьере или учёбе? Чего хотите добиться, без цензуры.",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.waiting_for_goals)
async def career_goals(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Опишите цели подробнее: должности, уровень дохода, стиль жизни.", reply_markup=process_keyboard())
        return
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
        "✏️ Создание резюме — 199₽\n\n"
        "Бот задаст серию вопросов и соберёт из ваших ответов готовый текст резюме под конкретную должность."
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
        "Под какую должность или направление делаем резюме? Можно указать пример вакансии.",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_position)
async def resume_position(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Уточните должность или направление чуть подробнее, чтобы резюме попало в цель.", reply_markup=process_keyboard())
        return
    await state.update_data(position=message.text)
    await state.set_state(ResumeCreateState.waiting_for_contacts)
    await message.answer(
        "Укажите город и контакты: телефон, email, Telegram. То, что готовы показывать работодателю.",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_contacts)
async def resume_contacts(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно указать хотя бы город и один способ связи.", reply_markup=process_keyboard())
        return
    await state.update_data(contacts=message.text)
    await state.set_state(ResumeCreateState.waiting_for_experience)
    await message.answer(
        "Опишите опыт: все места работы/стажировок. Для каждого: период, компания, должность, ключевые задачи и результаты.",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_experience)
async def resume_experience(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте детали по опыту: где, кем, какие задачи и конкретные результаты.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(ResumeCreateState.waiting_for_education)
    await message.answer(
        "Расскажите про образование: основное и доп. образование. ВУЗ/колледж, направление, годы, важные курсы.",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_education)
async def resume_education(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Чуть подробнее: список мест обучения, направления и годы.", reply_markup=process_keyboard())
        return
    await state.update_data(education=message.text)
    await state.set_state(ResumeCreateState.waiting_for_skills)
    await message.answer(
        "Перечислите ваши ключевые навыки. Сначала hard (инструменты, технологии, профумения), потом soft (коммуникация, ответственность и т.п.).",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_skills)
async def resume_skills(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно перечислить хотя бы несколько hard и soft навыков.", reply_markup=process_keyboard())
        return
    await state.update_data(skills=message.text)
    await state.set_state(ResumeCreateState.waiting_for_projects)
    await message.answer(
        "Опишите проекты и достижения, которыми вы гордитесь: рабочие, учебные, личные. Что именно сделали и какой был результат.",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_projects)
async def resume_projects(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте хотя бы пару примеров проектов или достижений.", reply_markup=process_keyboard())
        return
    await state.update_data(projects=message.text)
    await state.set_state(ResumeCreateState.waiting_for_extra)
    await message.answer(
        "Дополнительно: языки, формат работы, желаемые задачи, что хотите подчеркнуть или скрыть в резюме.",
        reply_markup=process_keyboard()
    )


@dp.message(ResumeCreateState.waiting_for_extra)
async def resume_extra(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Напишите пару фраз о ваших ожиданиях и важных деталях, которые стоит учесть.", reply_markup=process_keyboard())
        return
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
    if is_answer_too_short(message.text):
        await message.answer("Пришлите полный текст резюме, чтобы разбор был точным.", reply_markup=process_keyboard())
        return
    text = message.text
    result = await check_resume(text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "mock")
async def mock_start(cb: CallbackQuery):
    await cb.message.edit_text(
        "🎤 HR-мок интервью — 199₽\n\n"
        "Тренировочное собеседование: живые вопросы как у реального HR, разбор ответов и финальная оценка.",
        reply_markup=service_start_keyboard("MOCK_INTERVIEW_199", 199)
    )


@dp.callback_query(F.data == "start_MOCK_INTERVIEW_199")
async def mock_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(MockInterviewState.waiting_for_position)
    await cb.message.edit_text(
        "На какую должность вы готовитесь проходить собеседование? Можно скинуть краткий текст вакансии.",
        reply_markup=process_keyboard()
    )


@dp.message(MockInterviewState.waiting_for_position)
async def mock_position(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Опишите должность или сферу чуть подробнее, чтобы вопросы были точными.", reply_markup=process_keyboard())
        return
    await state.update_data(position=message.text)
    await state.set_state(MockInterviewState.waiting_for_experience)
    await message.answer(
        "Опишите ваш реальный опыт под эту должность: работа, стажировки, проекты. Чем занимались и какие результаты были.",
        reply_markup=process_keyboard()
    )


@dp.message(MockInterviewState.waiting_for_experience)
async def mock_experience(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно описать хотя бы пару примеров задач и результатов.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(MockInterviewState.waiting_for_goals)
    await message.answer(
        "Какие у вас цели и страхи перед собеседованием? Чего хотите добиться и чего боитесь больше всего?",
        reply_markup=process_keyboard()
    )


@dp.message(MockInterviewState.waiting_for_goals)
async def mock_goals(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Напишите честно, чего хотите и чего боитесь от собеседования.", reply_markup=process_keyboard())
        return
    data = await state.get_data()
    position = data.get("position")
    experience = data.get("experience")
    goals = message.text

    await state.update_data(goals=goals, dialog="", step=1)

    payload = (
        "РЕЖИМ: start\n\n"
        f"Целевая должность: {position}\n\n"
        f"Опыт кандидата: {experience}\n\n"
        f"Цели и страхи кандидата: {goals}\n\n"
        "Сформируй короткое приветствие и первый вопрос для тренировочного интервью. "
        "Веди себя как живой HR: вопросы могут быть прямыми, сложными и неудобными."
    )

    reply = await hr_mock_interview(payload)

    await state.set_state(MockInterviewState.in_interview)
    await state.update_data(last_question=reply)
    await message.answer(reply, reply_markup=process_keyboard())


@dp.message(MockInterviewState.in_interview)
async def mock_interview_step(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Попробуйте ответить так, как на реальном собеседовании: развёрнуто и по сути.", reply_markup=process_keyboard())
        return

    data = await state.get_data()
    position = data.get("position")
    experience = data.get("experience")
    goals = data.get("goals")
    step = data.get("step", 1)
    dialog = data.get("dialog", "")

    dialog += f"Ответ кандидата на шаге {step}:\n{message.text}\n\n"

    if step >= MAX_MOCK_STEPS:
        payload = (
            "РЕЖИМ: summary\n\n"
            f"Целевая должность: {position}\n\n"
            f"Опыт кандидата: {experience}\n\n"
            f"Цели и страхи кандидата: {goals}\n\n"
            f"История ответов кандидата:\n{dialog}\n\n"
            "Сделай итоговое резюме собеседования: сильные стороны, слабые места, риски и конкретные рекомендации. "
            "Пиши как опытный HR после реального интервью."
        )
        reply = await hr_mock_interview(payload)
        await state.clear()
        await message.answer(reply, reply_markup=main_keyboard())
        return

    payload = (
        "РЕЖИМ: step\n\n"
        f"Текущий шаг: {step}\n\n"
        f"Целевая должность: {position}\n\n"
        f"Опыт кандидата: {experience}\n\n"
        f"Цели и страхи кандидата: {goals}\n\n"
        f"История ответов кандидата:\n{dialog}\n\n"
        "Оцени последний ответ кандидата, дай честный, но конструктивный разбор и задай следующий вопрос. "
        "Формулировки вопросов меняй, не повторяйся, веди себя как живой HR. "
        "Если информации уже достаточно для выводов, вместо следующего вопроса сделай итоговое резюме собеседования "
        "и в самом конце ответа отдельной строкой напиши маркер: ИНТЕРВЬЮ_ЗАВЕРШЕНО."
    )

    reply = await hr_mock_interview(payload)

    if "ИНТЕРВЬЮ_ЗАВЕРШЕНО" in reply:
        cleaned = reply.replace("ИНТЕРВЬЮ_ЗАВЕРШЕНО", "").strip()
        await state.clear()
        await message.answer(cleaned, reply_markup=main_keyboard())
    else:
        await state.update_data(step=step + 1, dialog=dialog, last_question=reply)
        await message.answer(reply, reply_markup=process_keyboard())


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
    if is_answer_too_short(message.text):
        await message.answer("Нужно больше деталей по должности, компании и вашим переживаниям.", reply_markup=process_keyboard())
        return
    result = await interview_plan(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "soft")
async def soft_start(cb: CallbackQuery):
    await cb.message.edit_text(
        "💬 Soft-skills анализ — 99₽\n\n"
        "Разбираем, как вы ведёте себя в команде, в стрессовых ситуациях и конфликтах.",
        reply_markup=service_start_keyboard("SOFT_ANALYSIS_99", 99)
    )


@dp.callback_query(F.data == "start_SOFT_ANALYSIS_99")
async def soft_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(SoftSkillsState.waiting_for_answers)
    await cb.message.edit_text(
        "Опишите несколько ситуаций: работа в команде, конфликт, дедлайн, критика. Как вы себя вели?",
        reply_markup=process_keyboard()
    )


@dp.message(SoftSkillsState.waiting_for_answers)
async def soft_process(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Важно описать реальные ситуации и ваше поведение в них.", reply_markup=process_keyboard())
        return
    result = await soft_analysis(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "vacancy")
async def vacancy_start(cb: CallbackQuery):
    await cb.message.edit_text(
        "📄 Анализ вакансии — 99₽\n\n"
        "Смотрим текст вакансии и ваш профиль, оцениваем соответствие и показываем, чего не хватает.",
        reply_markup=service_start_keyboard("VACANCY_MATCH_99", 99)
    )


@dp.callback_query(F.data == "start_VACANCY_MATCH_99")
async def vacancy_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(VacancyMatchState.waiting_for_vacancy)
    await cb.message.edit_text(
        "Отправьте текст вакансии.",
        reply_markup=process_keyboard()
    )


@dp.message(VacancyMatchState.waiting_for_vacancy)
async def vacancy_part1(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Пришлите полный текст вакансии.", reply_markup=process_keyboard())
        return
    await state.update_data(vacancy=message.text)
    await state.set_state(VacancyMatchState.waiting_for_profile)
    await message.answer(
        "Теперь опишите ваш опыт и навыки, которые вы хотите сопоставить с этой вакансией.",
        reply_markup=process_keyboard()
    )


@dp.message(VacancyMatchState.waiting_for_profile)
async def vacancy_part2(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Опишите опыт и навыки подробнее, чтобы сравнение было точным.", reply_markup=process_keyboard())
        return
    data = await state.get_data()
    joined = f"Вакансия:\n{data['vacancy']}\n\nПрофиль:\n{message.text}"
    await state.clear()
    result = await vacancy_match(joined)
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "courses")
async def courses_start(cb: CallbackQuery):
    await cb.message.edit_text(
        "🎓 Подбор обучения — 99₽\n\n"
        "Понимаем, откуда вы стартуете и куда хотите прийти, и даём понятный план обучения и мини-проектов.",
        reply_markup=service_start_keyboard("COURSE_RECOMMEND_99", 99)
    )


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
        await message.answer("Чуть подробнее про ваш уровень и цели.", reply_markup=process_keyboard())
        return
    result = await course_recommendations(message.text)
    await state.clear()
    await message.answer(result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "pack_start_career")
async def pack_start_career(cb: CallbackQuery):
    text = (
        "🎁 Пакет «Старт карьеры» — 399₽\n\n"
        "Включает:\n"
        "• профориентацию,\n"
        "• создание резюме,\n"
        "• план на собеседование.\n\n"
        "Сейчас можно пройти эти шаги по отдельности через бот. Пакетным оформлением займёмся позже."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "pack_before_interview")
async def pack_before_interview(cb: CallbackQuery):
    text = (
        "🎯 Пакет «Перед собесом» — 449₽\n\n"
        "Включает:\n"
        "• проверку резюме,\n"
        "• анализ вакансии,\n"
        "• план на собеседование,\n"
        "• HR-мок интервью.\n\n"
        "Сейчас эти услуги доступны по отдельности в разделе «Собеседование»."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


@dp.callback_query(F.data == "pack_max")
async def pack_max(cb: CallbackQuery):
    text = (
        "🏆 Пакет «Максимум» — 699₽\n\n"
        "Полный цикл: от выбора направления до подготовки к выходу на рынок.\n\n"
        "Пока что пакет оформляется вручную: можно пройти все услуги через меню бота."
    )
    await cb.message.edit_text(text, reply_markup=back_button())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
