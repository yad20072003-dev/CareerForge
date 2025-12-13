import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from keyboards import (
    main_keyboard,
    back_to_menu_keyboard,
    process_keyboard,
    services_keyboard,
    service_start_keyboard,
    scenario_direction_keyboard,
    scenario_job_keyboard,
    scenario_interview_keyboard,
    free_keyboard,
    mock_keyboard,
)
from states import (
    CareerState,
    ResumeCreateState,
    ResumeCheckState,
    MockInterviewState,
    MockClarifyState,
    InterviewPlanState,
    VacancyMatchState,
    CompetitivenessState,
)
from products.products import PRODUCTS

from services.career_service import make_career_report
from services.resume_service import make_resume
from services.rescheck_service import check_resume
from services.mock_service import hr_mock_interview
from services.plan_service import interview_plan
from services.vacancy_service import vacancy_match
from services.competitiveness_service import competitiveness_check


BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

MAX_MSG_CHARS = 3500
MAX_MOCK_FULL_STEPS = 18
MAX_MOCK_SHORT_STEPS = 8


def is_answer_too_short(text: str) -> bool:
    if not text:
        return True
    t = text.strip()
    return len(t) < 10


def split_text(text: str, chunk: int = MAX_MSG_CHARS) -> list[str]:
    if not text:
        return [""]
    parts = []
    s = text.strip()
    while len(s) > chunk:
        cut = s.rfind("\n", 0, chunk)
        if cut < 800:
            cut = chunk
        parts.append(s[:cut].rstrip())
        s = s[cut:].lstrip()
    if s:
        parts.append(s)
    return parts


async def send_long(message: Message, text: str, reply_markup=None):
    parts = split_text(text)
    if not parts:
        parts = [text]
    for i, part in enumerate(parts):
        if i == 0:
            await message.answer(part, reply_markup=reply_markup)
        else:
            await message.answer(part)


async def safe_edit(cb: CallbackQuery, text: str, reply_markup=None):
    try:
        await cb.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await cb.message.answer(text, reply_markup=reply_markup)
        else:
            raise


@dp.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "Кузница карьеры.\n\n"
        "Помогает выбрать направление, усилить резюме, понять требования вакансий и подготовиться к собеседованию.\n"
        "Без обещаний и гарантий. Только практичные рекомендации и тексты, которые можно использовать сразу.\n\n"
        "Выберите, что актуально сейчас."
    )
    await message.answer(text, reply_markup=main_keyboard())


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit(cb, "Главное меню:", reply_markup=main_keyboard())


@dp.callback_query(F.data == "info")
async def info_block(cb: CallbackQuery):
    text = (
        "О боте.\n\n"
        "Это карьерный помощник, который:\n"
        "1) собирает вводные короткими шагами,\n"
        "2) даёт структурный разбор и конкретные формулировки,\n"
        "3) помогает усилить резюме и подготовиться к интервью.\n\n"
        "Бот не обещает трудоустройство и не заменяет работодателя. "
        "Он помогает повысить качество вашей самопрезентации и ясность следующего шага."
    )
    await safe_edit(cb, text, reply_markup=back_to_menu_keyboard())


@dp.callback_query(F.data == "services_menu")
async def services_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit(cb, "Выберите услугу:", reply_markup=services_keyboard())


@dp.callback_query(F.data == "scenario_direction")
async def scenario_direction(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "Выбор направления и быстрый план действий под ваши вводные."
    await safe_edit(cb, text, reply_markup=scenario_direction_keyboard())


@dp.callback_query(F.data == "scenario_job")
async def scenario_job(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "Поиск работы: резюме, проверка, анализ вакансии и понятный следующий шаг."
    await safe_edit(cb, text, reply_markup=scenario_job_keyboard())


@dp.callback_query(F.data == "scenario_interview")
async def scenario_interview(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "Подготовка к собеседованию: тренировка с HR-логикой и план поведения."
    await safe_edit(cb, text, reply_markup=scenario_interview_keyboard())


@dp.callback_query(F.data == "free_menu")
async def free_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "Бесплатные материалы и диагностики."
    await safe_edit(cb, text, reply_markup=free_keyboard())


@dp.callback_query(F.data == "free_mini_resume")
async def free_mini_resume(cb: CallbackQuery):
    text = (
        "Мини-советы по резюме.\n\n"
        "1) Заголовок резюме должен совпадать с целевой ролью.\n"
        "2) Опыт: сначала задача, затем результат (что изменилось, в цифрах или фактах).\n"
        "3) Навыки: отдельно hard и отдельно soft, только то, что подтверждается опытом.\n"
        "4) Уберите общие слова без доказательств.\n"
        "5) Одно резюме под одну роль: адаптация под вакансию повышает отклик."
    )
    await safe_edit(cb, text, reply_markup=back_to_menu_keyboard())


@dp.callback_query(F.data == "free_checklist")
async def free_checklist(cb: CallbackQuery):
    text = (
        "Чек-лист к собеседованию.\n\n"
        "1) Самопрезентация на 40–60 секунд.\n"
        "2) 3 сильные стороны с примерами.\n"
        "3) 2 кейса: сложная ситуация и результат.\n"
        "4) Понимаю требования вакансии и могу сопоставить со своим опытом.\n"
        "5) Подготовил 5 вопросов работодателю.\n"
        "6) Знаю свою вилку по зарплате и аргументы."
    )
    await safe_edit(cb, text, reply_markup=back_to_menu_keyboard())


@dp.callback_query(F.data == "free_competitiveness")
async def free_competitiveness(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CompetitivenessState.q1)
    await safe_edit(cb, "Быстрая диагностика. Есть ли у вас резюме под конкретную должность? (да/нет)", reply_markup=process_keyboard())


@dp.message(CompetitivenessState.q1)
async def comp_q1(message: Message, state: FSMContext):
    await state.update_data(q1=message.text)
    await state.set_state(CompetitivenessState.q2)
    await message.answer("Есть ли в резюме цифры и результаты, а не только обязанности? (да/нет)", reply_markup=process_keyboard())


@dp.message(CompetitivenessState.q2)
async def comp_q2(message: Message, state: FSMContext):
    await state.update_data(q2=message.text)
    await state.set_state(CompetitivenessState.q3)
    await message.answer("Вы откликаетесь выборочно или на всё подряд? (коротко)", reply_markup=process_keyboard())


@dp.message(CompetitivenessState.q3)
async def comp_q3(message: Message, state: FSMContext):
    await state.update_data(q3=message.text)
    await state.set_state(CompetitivenessState.q4)
    await message.answer("Вы понимаете требования вакансий, на которые идёте? (да/нет/частично)", reply_markup=process_keyboard())


@dp.message(CompetitivenessState.q4)
async def comp_q4(message: Message, state: FSMContext):
    await state.update_data(q4=message.text)
    await state.set_state(CompetitivenessState.q5)
    await message.answer("Звали ли вас на собеседования за последние 2–4 недели? (да/нет)", reply_markup=process_keyboard())


@dp.message(CompetitivenessState.q5)
async def comp_q5(message: Message, state: FSMContext):
    await state.update_data(q5=message.text)
    await state.set_state(CompetitivenessState.q6)
    await message.answer("Какая цель сейчас: работа срочно / рост дохода / смена сферы? (коротко)", reply_markup=process_keyboard())


@dp.message(CompetitivenessState.q6)
async def comp_q6(message: Message, state: FSMContext):
    await state.update_data(q6=message.text)
    data = await state.get_data()
    payload = (
        f"1) Резюме под роль: {data.get('q1','')}\n"
        f"2) Цифры и результаты: {data.get('q2','')}\n"
        f"3) Стратегия откликов: {data.get('q3','')}\n"
        f"4) Понимание требований: {data.get('q4','')}\n"
        f"5) Собеседования в последние недели: {data.get('q5','')}\n"
        f"6) Цель: {data.get('q6','')}\n"
    )
    await state.clear()
    result = await competitiveness_check(payload)
    await send_long(message, result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "back_step")
async def back_step(cb: CallbackQuery, state: FSMContext):
    current = await state.get_state()
    if not current:
        await safe_edit(cb, "Главное меню:", reply_markup=main_keyboard())
        return

    mapping = {
        CareerState.waiting_for_education.state: (CareerState.waiting_for_basic, "Сколько вам лет и чем вы занимаетесь?"),
        CareerState.waiting_for_experience.state: (CareerState.waiting_for_education, "Расскажите про образование."),
        CareerState.waiting_for_interests.state: (CareerState.waiting_for_experience, "Опишите ваш опыт подробнее."),
        CareerState.waiting_for_preferences.state: (CareerState.waiting_for_interests, "Что вам интересно по жизни?"),
        CareerState.waiting_for_goals.state: (CareerState.waiting_for_preferences, "Какая работа вам ближе и почему?"),

        ResumeCreateState.waiting_for_contacts.state: (ResumeCreateState.waiting_for_position, "Под какую должность делаем резюме?"),
        ResumeCreateState.waiting_for_experience.state: (ResumeCreateState.waiting_for_contacts, "Город и контакты (телефон/почта/телеграм)."),
        ResumeCreateState.waiting_for_education.state: (ResumeCreateState.waiting_for_experience, "Опишите опыт: где работали и что делали."),
        ResumeCreateState.waiting_for_skills.state: (ResumeCreateState.waiting_for_education, "Образование: где и что изучали."),
        ResumeCreateState.waiting_for_projects.state: (ResumeCreateState.waiting_for_skills, "Навыки: hard и инструменты, которые реально используете."),
        ResumeCreateState.waiting_for_extra.state: (ResumeCreateState.waiting_for_projects, "Проекты/достижения: 2–5 пунктов, можно без цифр."),

        ResumeCheckState.waiting_for_resume.state: (None, None),

        InterviewPlanState.waiting_for_info.state: (None, None),

        VacancyMatchState.waiting_for_vacancy.state: (None, None),
        VacancyMatchState.waiting_for_profile.state: (VacancyMatchState.waiting_for_vacancy, "Пришлите текст вакансии."),

        CompetitivenessState.q2.state: (CompetitivenessState.q1, "Есть ли у вас резюме под конкретную должность? (да/нет)"),
        CompetitivenessState.q3.state: (CompetitivenessState.q2, "Есть ли в резюме цифры и результаты, а не только обязанности? (да/нет)"),
        CompetitivenessState.q4.state: (CompetitivenessState.q3, "Вы откликаетесь выборочно или на всё подряд? (коротко)"),
        CompetitivenessState.q5.state: (CompetitivenessState.q4, "Вы понимаете требования вакансий, на которые идёте? (да/нет/частично)"),
        CompetitivenessState.q6.state: (CompetitivenessState.q5, "Звали ли вас на собеседования за последние 2–4 недели? (да/нет)"),
    }

    if current in (MockInterviewState.waiting_for_position.state, MockInterviewState.waiting_for_experience.state, MockInterviewState.waiting_for_goals.state, MockInterviewState.in_interview.state, MockClarifyState.waiting_for_clarify.state):
        await cb.answer("В режиме интервью возврат шага отключён.", show_alert=True)
        return

    if current in mapping and mapping[current][0] is not None:
        new_state, question = mapping[current]
        await state.set_state(new_state)
        await safe_edit(cb, question, reply_markup=process_keyboard())
        return

    await state.clear()
    await safe_edit(cb, "Главное меню:", reply_markup=main_keyboard())


@dp.callback_query(F.data == "career")
async def start_career(cb: CallbackQuery):
    product = PRODUCTS["CAREER_ORIENTATION"]
    await safe_edit(cb, product["description"], reply_markup=service_start_keyboard(product["code"]))


@dp.callback_query(F.data == "start_CAREER_ORIENTATION")
async def start_career_input(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CareerState.waiting_for_basic)
    await safe_edit(cb, "Сколько вам лет и чем вы занимаетесь сейчас?", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_basic)
async def career_basic(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Ответьте чуть подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(basic=message.text)
    await state.set_state(CareerState.waiting_for_education)
    await message.answer("Образование: что изучали и что сейчас умеете?", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_education)
async def career_education(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте деталей.", reply_markup=process_keyboard())
        return
    await state.update_data(education=message.text)
    await state.set_state(CareerState.waiting_for_experience)
    await message.answer("Опыт: где работали/что пробовали/какие задачи делали?", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_experience)
async def career_experience(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Чуть подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(CareerState.waiting_for_interests)
    await message.answer("Что вам реально нравится делать: темы, задачи, формат работы?", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_interests)
async def career_interests(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Раскройте мысль.", reply_markup=process_keyboard())
        return
    await state.update_data(interests=message.text)
    await state.set_state(CareerState.waiting_for_preferences)
    await message.answer("Какая работа вам ближе: люди/цифры/креатив/процессы/продажи/техника? Почему?", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_preferences)
async def career_preferences(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте причин и примеров.", reply_markup=process_keyboard())
        return
    await state.update_data(preferences=message.text)
    await state.set_state(CareerState.waiting_for_goals)
    await message.answer("Цель: деньги/стабильность/рост/срочно найти работу/смена сферы? Опишите кратко.", reply_markup=process_keyboard())


@dp.message(CareerState.waiting_for_goals)
async def career_goals(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Опишите цель чуть подробнее.", reply_markup=process_keyboard())
        return

    await state.update_data(goals=message.text)
    data = await state.get_data()

    user_text = (
        f"Базовая информация: {data['basic']}\n\n"
        f"Образование и навыки: {data['education']}\n\n"
        f"Опыт: {data['experience']}\n\n"
        f"Интересы: {data['interests']}\n\n"
        f"Предпочтения: {data['preferences']}\n\n"
        f"Цель: {data['goals']}"
    )

    await state.clear()
    result = await make_career_report(user_text)
    await send_long(message, result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "resume_create")
async def start_resume(cb: CallbackQuery):
    product = PRODUCTS["RESUME_CREATE"]
    await safe_edit(cb, product["description"], reply_markup=service_start_keyboard(product["code"]))


@dp.callback_query(F.data == "start_RESUME_CREATE")
async def begin_resume(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ResumeCreateState.waiting_for_position)
    await safe_edit(cb, "Под какую должность делаем резюме? Укажите роль и уровень.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_position)
async def resume_position(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Уточните роль и уровень.", reply_markup=process_keyboard())
        return
    await state.update_data(position=message.text)
    await state.set_state(ResumeCreateState.waiting_for_contacts)
    await message.answer("Город и контакты (телефон/почта/телеграм).", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_contacts)
async def resume_contacts(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте хотя бы один контакт.", reply_markup=process_keyboard())
        return
    await state.update_data(contacts=message.text)
    await state.set_state(ResumeCreateState.waiting_for_experience)
    await message.answer("Опыт: компании/роли/задачи. Можно списком.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_experience)
async def resume_experience(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно чуть подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(ResumeCreateState.waiting_for_education)
    await message.answer("Образование: где учились, специальность, годы (если помните).", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_education)
async def resume_education(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте деталей.", reply_markup=process_keyboard())
        return
    await state.update_data(education=message.text)
    await state.set_state(ResumeCreateState.waiting_for_skills)
    await message.answer("Навыки: hard, инструменты, технологии, подходы. Только реальное.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_skills)
async def resume_skills(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Перечислите несколько навыков.", reply_markup=process_keyboard())
        return
    await state.update_data(skills=message.text)
    await state.set_state(ResumeCreateState.waiting_for_projects)
    await message.answer("Достижения/проекты: 2–6 пунктов. Что сделали и какой эффект.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_projects)
async def resume_projects(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Дайте пару примеров.", reply_markup=process_keyboard())
        return
    await state.update_data(projects=message.text)
    await state.set_state(ResumeCreateState.waiting_for_extra)
    await message.answer("Дополнительно: языки, формат работы, портфолио/ссылки, важные детали.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.waiting_for_extra)
async def resume_extra(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Если нечего добавить, напишите: нет.", reply_markup=process_keyboard())
        return

    await state.update_data(extra=message.text)
    data = await state.get_data()

    user_text = (
        f"Целевая роль: {data['position']}\n\n"
        f"Контакты: {data['contacts']}\n\n"
        f"Опыт: {data['experience']}\n\n"
        f"Образование: {data['education']}\n\n"
        f"Навыки: {data['skills']}\n\n"
        f"Достижения и проекты: {data['projects']}\n\n"
        f"Дополнительно: {data['extra']}"
    )

    await state.clear()
    result = await make_resume(user_text)
    await send_long(message, result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "resume_check")
async def start_resume_check(cb: CallbackQuery):
    product = PRODUCTS["RESUME_CHECK"]
    await safe_edit(cb, product["description"], reply_markup=service_start_keyboard(product["code"]))


@dp.callback_query(F.data == "start_RESUME_CHECK")
async def begin_resume_check(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ResumeCheckState.waiting_for_resume)
    await safe_edit(cb, "Пришлите текст резюме одним сообщением.", reply_markup=process_keyboard())


@dp.message(ResumeCheckState.waiting_for_resume)
async def resume_check_step(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Пришлите полный текст резюме.", reply_markup=process_keyboard())
        return
    await state.clear()
    result = await check_resume(message.text)
    await send_long(message, result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "vacancy")
async def vacancy_start(cb: CallbackQuery):
    product = PRODUCTS["VACANCY_ANALYSIS"]
    await safe_edit(cb, product["description"], reply_markup=service_start_keyboard(product["code"]))


@dp.callback_query(F.data == "start_VACANCY_ANALYSIS")
async def vacancy_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(VacancyMatchState.waiting_for_vacancy)
    await safe_edit(cb, "Пришлите текст вакансии.", reply_markup=process_keyboard())


@dp.message(VacancyMatchState.waiting_for_vacancy)
async def vacancy_part1(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Пришлите полный текст вакансии.", reply_markup=process_keyboard())
        return
    await state.update_data(vacancy=message.text)
    await state.set_state(VacancyMatchState.waiting_for_profile)
    await message.answer("Теперь опишите свой опыт под эту вакансию: 5–12 строк.", reply_markup=process_keyboard())


@dp.message(VacancyMatchState.waiting_for_profile)
async def vacancy_part2(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Нужно чуть подробнее.", reply_markup=process_keyboard())
        return

    data = await state.get_data()
    full = f"Вакансия:\n{data['vacancy']}\n\nПрофиль кандидата:\n{message.text}"
    await state.clear()
    result = await vacancy_match(full)
    await send_long(message, result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "interview_plan")
async def plan_start(cb: CallbackQuery):
    product = PRODUCTS["INTERVIEW_PLAN"]
    await safe_edit(cb, product["description"], reply_markup=service_start_keyboard(product["code"]))


@dp.callback_query(F.data == "start_INTERVIEW_PLAN")
async def plan_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(InterviewPlanState.waiting_for_info)
    await safe_edit(cb, "Опишите: роль, компания/ниша, ваш опыт, сильные стороны, страхи и цель.", reply_markup=process_keyboard())


@dp.message(InterviewPlanState.waiting_for_info)
async def plan_process(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте деталей.", reply_markup=process_keyboard())
        return
    await state.clear()
    result = await interview_plan(message.text)
    await send_long(message, result, reply_markup=main_keyboard())


@dp.callback_query(F.data == "mock_short")
async def mock_short_start(cb: CallbackQuery):
    product = PRODUCTS["MOCK_INTERVIEW_SHORT"]
    await safe_edit(cb, product["description"], reply_markup=service_start_keyboard(product["code"]))


@dp.callback_query(F.data == "mock_full")
async def mock_full_start(cb: CallbackQuery):
    product = PRODUCTS["MOCK_INTERVIEW_FULL"]
    await safe_edit(cb, product["description"], reply_markup=service_start_keyboard(product["code"]))


@dp.callback_query(F.data == "start_MOCK_INTERVIEW_SHORT")
async def mock_short_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(MockInterviewState.waiting_for_position)
    await state.update_data(mode="short", max_steps=MAX_MOCK_SHORT_STEPS)
    await safe_edit(cb, "На какую должность вы готовитесь? Укажите роль и уровень.", reply_markup=process_keyboard())


@dp.callback_query(F.data == "start_MOCK_INTERVIEW_FULL")
async def mock_full_begin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(MockInterviewState.waiting_for_position)
    await state.update_data(mode="full", max_steps=MAX_MOCK_FULL_STEPS)
    await safe_edit(cb, "На какую должность вы готовитесь? Укажите роль и уровень.", reply_markup=process_keyboard())


@dp.message(MockInterviewState.waiting_for_position)
async def mock_position(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Уточните роль и уровень.", reply_markup=process_keyboard())
        return

    await state.update_data(position=message.text)
    await state.set_state(MockInterviewState.waiting_for_experience)
    await message.answer("Опишите опыт под эту роль: 6–12 строк, с задачами и результатами.", reply_markup=process_keyboard())


@dp.message(MockInterviewState.waiting_for_experience)
async def mock_experience(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Добавьте примеров задач и результатов.", reply_markup=process_keyboard())
        return

    await state.update_data(experience=message.text)
    await state.set_state(MockInterviewState.waiting_for_goals)
    await message.answer("Цель и страх: чего хотите добиться и чего боитесь больше всего? 2–6 строк.", reply_markup=process_keyboard())


@dp.message(MockInterviewState.waiting_for_goals)
async def mock_goals(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Ответьте чуть подробнее.", reply_markup=process_keyboard())
        return

    data = await state.get_data()
    position = data["position"]
    experience = data["experience"]
    max_steps = data.get("max_steps", MAX_MOCK_FULL_STEPS)

    await state.update_data(goals=message.text, dialog="", step=1, last_question="")
    payload = (
        "MODE: start\n\n"
        f"MAX_STEPS: {max_steps}\n\n"
        f"Target role: {position}\n\n"
        f"Candidate experience: {experience}\n\n"
        f"Goal and fear: {message.text}\n\n"
        "Generate a short greeting and the first warm-up question."
    )

    reply = await hr_mock_interview(payload)
    await state.set_state(MockInterviewState.in_interview)
    await state.update_data(last_question=reply)
    await send_long(message, reply, reply_markup=mock_keyboard())


@dp.callback_query(F.data == "mock_clarify")
async def mock_clarify(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data or not data.get("last_question"):
        await cb.answer("Нет вопроса для уточнения.", show_alert=True)
        return
    await state.set_state(MockClarifyState.waiting_for_clarify)
    await safe_edit(cb, "Напишите уточняющий вопрос по последнему вопросу HR одним сообщением.", reply_markup=mock_keyboard())


@dp.message(MockClarifyState.waiting_for_clarify)
async def mock_clarify_message(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Сформулируйте уточнение конкретнее.", reply_markup=mock_keyboard())
        return

    data = await state.get_data()
    position = data.get("position", "")
    experience = data.get("experience", "")
    goals = data.get("goals", "")
    dialog = data.get("dialog", "")
    step = data.get("step", 1)
    last_q = data.get("last_question", "")
    max_steps = data.get("max_steps", MAX_MOCK_FULL_STEPS)

    payload = (
        "MODE: clarify\n\n"
        f"MAX_STEPS: {max_steps}\n\n"
        f"Step: {step}\n\n"
        f"Target role: {position}\n\n"
        f"Candidate experience: {experience}\n\n"
        f"Goal and fear: {goals}\n\n"
        f"Interview history:\n{dialog}\n\n"
        f"Last HR question:\n{last_q}\n\n"
        f"Candidate clarification question:\n{message.text}\n\n"
        "Clarify what the HR meant, provide 2-3 good answer directions, and ask the candidate to answer the original HR question."
    )

    reply = await hr_mock_interview(payload)
    await state.set_state(MockInterviewState.in_interview)
    await state.update_data(last_question=reply)
    await send_long(message, reply, reply_markup=mock_keyboard())


@dp.callback_query(F.data == "mock_finish")
async def mock_finish(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await cb.answer("Интервью не запущено.", show_alert=True)
        return
    position = data.get("position", "")
    experience = data.get("experience", "")
    goals = data.get("goals", "")
    dialog = data.get("dialog", "")
    max_steps = data.get("max_steps", MAX_MOCK_FULL_STEPS)

    payload = (
        "MODE: summary\n\n"
        f"MAX_STEPS: {max_steps}\n\n"
        f"Target role: {position}\n\n"
        f"Candidate experience: {experience}\n\n"
        f"Goal and fear: {goals}\n\n"
        f"Full interview log:\n{dialog}\n\n"
        "Create a final HR conclusion: strengths, risks, concrete fixes, and a short prep plan."
    )
    reply = await hr_mock_interview(payload)
    await state.clear()
    await safe_edit(cb, "Интервью завершено. Итог ниже.")
    await send_long(cb.message, reply, reply_markup=main_keyboard())


@dp.message(MockInterviewState.in_interview)
async def mock_step(message: Message, state: FSMContext):
    if is_answer_too_short(message.text):
        await message.answer("Ответьте развёрнуто: что сделали, почему, результат.", reply_markup=mock_keyboard())
        return

    data = await state.get_data()
    step = int(data.get("step", 1))
    position = data.get("position", "")
    experience = data.get("experience", "")
    goals = data.get("goals", "")
    dialog = data.get("dialog", "")
    max_steps = int(data.get("max_steps", MAX_MOCK_FULL_STEPS))

    dialog = dialog + f"Answer {step}: {message.text}\n\n"

    if step < max_steps:
        payload = (
            "MODE: step\n\n"
            f"MAX_STEPS: {max_steps}\n\n"
            f"Step: {step}\n\n"
            f"Target role: {position}\n\n"
            f"Candidate experience: {experience}\n\n"
            f"Goal and fear: {goals}\n\n"
            f"Interview history:\n{dialog}\n\n"
            "Analyze the answer in a realistic HR manner and ask the next question. Keep it concise and practical."
        )
        reply = await hr_mock_interview(payload)
        await state.update_data(step=step + 1, dialog=dialog, last_question=reply)
        await send_long(message, reply, reply_markup=mock_keyboard())
    else:
        payload = (
            "MODE: summary\n\n"
            f"MAX_STEPS: {max_steps}\n\n"
            f"Target role: {position}\n\n"
            f"Candidate experience: {experience}\n\n"
            f"Goal and fear: {goals}\n\n"
            f"Full interview log:\n{dialog}\n\n"
            "Create a final HR conclusion: strengths, risks, concrete fixes, and a short prep plan."
        )
        reply = await hr_mock_interview(payload)
        await state.clear()
        await send_long(message, reply, reply_markup=main_keyboard())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
