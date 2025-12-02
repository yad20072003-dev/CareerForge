import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from keyboards import main_keyboard, services_keyboard, service_start_keyboard, process_keyboard, back_button
from states import (
    CareerState,
    ResumeCreateState,
    ResumeCheckState,
    MockInterviewState,
    InterviewPlanState,
    SoftSkillsState,
    VacancyMatchState,
    CoursesState
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


def short(text: str) -> bool:
    if not text:
        return True
    if len(text.strip()) < 10:
        return True
    return False


@dp.message(CommandStart())
async def start(message: Message):
    t = (
        "👋 Это «Кузница карьеры».\n\n"
        "Я помогу вам:\n"
        "• выбрать направление развития;\n"
        "• собрать сильное резюме;\n"
        "• подготовиться к собеседованию;\n"
        "• пройти реалистичное HR-интервью.\n\n"
        "Откройте меню услуг, чтобы начать."
    )
    await message.answer(t, reply_markup=main_keyboard())


@dp.callback_query(F.data == "services_menu")
async def services_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Выберите услугу:", reply_markup=services_keyboard())


@dp.callback_query(F.data == "info")
async def info_block(cb: CallbackQuery):
    t = (
        "💼 Услуги:\n\n"
        "99₽:\n"
        "• Soft skills анализ\n"
        "• Анализ вакансии\n"
        "• Подбор обучения\n\n"
        "149₽:\n"
        "• Профориентация\n"
        "• Проверка резюме\n"
        "• План поведения на собеседовании\n\n"
        "199₽:\n"
        "• Создание резюме\n"
        "• HR-мок интервью\n"
    )
    await cb.message.edit_text(t, reply_markup=back_button())


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Главное меню:", reply_markup=main_keyboard())


@dp.callback_query(F.data.startswith("pay_"))
async def pay_stub(cb: CallbackQuery):
    code = cb.data.replace("pay_", "")
    p = PRODUCTS.get(code)
    if not p:
        await cb.message.answer("Ошибка товара.")
        return
    await cb.message.answer(
        f"{p['title']}\nЦена: {p['amount']}₽\n\nОплата появится после подключения ЮKassa.",
        reply_markup=back_button()
    )



@dp.callback_query(F.data == "career")
async def career(cb: CallbackQuery):
    await cb.message.edit_text(
        "🧭 Профориентация — 149₽\n\nПомогу определить подходящее направление развития.",
        reply_markup=service_start_keyboard("CAREER_149", 149)
    )


@dp.callback_query(F.data == "start_CAREER_149")
async def start_career(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CareerState.basic)
    await cb.message.edit_text(
        "Сколько вам лет и чем вы сейчас занимаетесь?",
        reply_markup=process_keyboard()
    )


@dp.message(CareerState.basic)
async def career_basic(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Нужен более развёрнутый ответ.", reply_markup=process_keyboard())
        return
    await state.update_data(basic=message.text)
    await state.set_state(CareerState.education)
    await message.answer("Расскажите про образование.", reply_markup=process_keyboard())


@dp.message(CareerState.education)
async def career_edu(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Добавьте деталей.", reply_markup=process_keyboard())
        return
    await state.update_data(education=message.text)
    await state.set_state(CareerState.experience)
    await message.answer("Опишите ваш опыт: работа, проекты.", reply_markup=process_keyboard())


@dp.message(CareerState.experience)
async def career_experience(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Нужны задачи и результаты.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(CareerState.interests)
    await message.answer("Что вам реально интересно?", reply_markup=process_keyboard())


@dp.message(CareerState.interests)
async def career_interests(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Чуть подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(interests=message.text)
    await state.set_state(CareerState.goals)
    await message.answer("Какие цели на 1–3 года?", reply_markup=process_keyboard())


@dp.message(CareerState.goals)
async def career_goals(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Опишите подробнее цели.", reply_markup=process_keyboard())
        return

    await state.update_data(goals=message.text)
    d = await state.get_data()
    joined = (
        f"{d['basic']}\n\n{d['education']}\n\n{d['experience']}\n\n"
        f"{d['interests']}\n\n{d['goals']}"
    )

    await state.clear()
    r = await make_career_report(joined)
    await message.answer(r, reply_markup=main_keyboard())



@dp.callback_query(F.data == "resume_create")
async def resume_create(cb: CallbackQuery):
    await cb.message.edit_text(
        "✏️ Создание резюме — 199₽",
        reply_markup=service_start_keyboard("RESUME_199", 199)
    )


@dp.callback_query(F.data == "start_RESUME_199")
async def resume_start(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ResumeCreateState.position)
    await cb.message.edit_text("На какую должность делаем резюме?", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.position)
async def r_pos(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Уточните должность.", reply_markup=process_keyboard())
        return
    await state.update_data(position=message.text)
    await state.set_state(ResumeCreateState.contacts)
    await message.answer("Город + контакты.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.contacts)
async def r_contacts(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Нужен город и хотя бы один контакт.", reply_markup=process_keyboard())
        return
    await state.update_data(contacts=message.text)
    await state.set_state(ResumeCreateState.experience)
    await message.answer("Опишите опыт детально.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.experience)
async def r_ex(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Добавьте задачи и результаты.", reply_markup=process_keyboard())
        return
    await state.update_data(experience=message.text)
    await state.set_state(ResumeCreateState.education)
    await message.answer("Расскажите про образование.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.education)
async def r_ed(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Уточните места и годы обучения.", reply_markup=process_keyboard())
        return
    await state.update_data(education=message.text)
    await state.set_state(ResumeCreateState.skills)
    await message.answer("Перечислите hard и soft навыки.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.skills)
async def r_sk(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Укажите хотя бы несколько навыков.", reply_markup=process_keyboard())
        return
    await state.update_data(skills=message.text)
    await state.set_state(ResumeCreateState.projects)
    await message.answer("Опишите проекты и достижения.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.projects)
async def r_pr(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Нужны 1–2 примера.", reply_markup=process_keyboard())
        return
    await state.update_data(projects=message.text)
    await state.set_state(ResumeCreateState.extra)
    await message.answer("Дополнительные детали.", reply_markup=process_keyboard())


@dp.message(ResumeCreateState.extra)
async def r_extra(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Добавьте важные детали.", reply_markup=process_keyboard())
        return

    d = await state.get_data()
    joined = (
        f"{d['position']}\n\n{d['contacts']}\n\n{d['experience']}\n\n"
        f"{d['education']}\n\n{d['skills']}\n\n{d['projects']}\n\n{message.text}"
    )

    await state.clear()
    r = await make_resume(joined)
    await message.answer(r, reply_markup=main_keyboard())



@dp.callback_query(F.data == "resume_check")
async def resume_check(cb: CallbackQuery):
    await cb.message.edit_text(
        "🔍 Проверка резюме — 149₽",
        reply_markup=service_start_keyboard("RESCHECK_149", 149)
    )


@dp.callback_query(F.data == "start_RESCHECK_149")
async def start_rcheck(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ResumeCheckState.text)
    await cb.message.edit_text("Пришлите текст резюме одним сообщением.", reply_markup=process_keyboard())


@dp.message(ResumeCheckState.text)
async def rcheck(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Нужен полный текст.", reply_markup=process_keyboard())
        return
    r = await check_resume(message.text)
    await state.clear()
    await message.answer(r, reply_markup=main_keyboard())



@dp.callback_query(F.data == "mock")
async def mock(cb: CallbackQuery):
    await cb.message.edit_text(
        "🎤 HR-мок интервью — 199₽",
        reply_markup=service_start_keyboard("MOCK_199", 199)
    )


@dp.callback_query(F.data == "start_MOCK_199")
async def mock_start(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(MockInterviewState.position)
    await cb.message.edit_text("На какую должность вы готовитесь?", reply_markup=process_keyboard())


@dp.message(MockInterviewState.position)
async def m_pos(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Опишите должность подробнее.", reply_markup=process_keyboard())
        return
    await state.update_data(position=message.text)
    await state.set_state(MockInterviewState.background)
    await message.answer("Расскажите про ваш опыт под эту должность.", reply_markup=process_keyboard())


@dp.message(MockInterviewState.background)
async def m_bg(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Нужны задачи и результаты.", reply_markup=process_keyboard())
        return
    await state.update_data(background=message.text)
    await state.set_state(MockInterviewState.goals)
    await message.answer("Ваши цели, опасения и слабые места?", reply_markup=process_keyboard())


@dp.message(MockInterviewState.goals)
async def m_goals(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Добавьте деталей.", reply_markup=process_keyboard())
        return

    d = await state.get_data()
    payload = (
        "РЕЖИМ: start\n"
        f"Должность: {d['position']}\n"
        f"Опыт: {d['background']}\n"
        f"Цели и страхи: {message.text}"
    )

    r = await hr_mock_interview(payload)
    await state.update_data(dialog="", step=1, goals=message.text)
    await state.set_state(MockInterviewState.in_progress)
    await message.answer(r, reply_markup=process_keyboard())


@dp.message(MockInterviewState.in_progress)
async def m_step(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Ответ должен быть развёрнутым.", reply_markup=process_keyboard())
        return

    d = await state.get_data()
    step = d.get("step", 1)
    dialog = d.get("dialog", "")

    dialog += f"Ответ {step}: {message.text}\n\n"

    if step < 15:
        payload = (
            "РЕЖИМ: step\n"
            f"Шаг: {step}\n"
            f"Должность: {d['position']}\n"
            f"Опыт: {d['background']}\n"
            f"Цели: {d['goals']}\n"
            f"Диалог:\n{dialog}"
        )
        r = await hr_mock_interview(payload)
        await state.update_data(step=step + 1, dialog=dialog)
        await message.answer(r, reply_markup=process_keyboard())
    else:
        payload = (
            "РЕЖИМ: summary\n"
            f"Должность: {d['position']}\n"
            f"Опыт: {d['background']}\n"
            f"Цели: {d['goals']}\n"
            f"Диалог:\n{dialog}"
        )
        r = await hr_mock_interview(payload)
        await state.clear()
        await message.answer(r, reply_markup=main_keyboard())



@dp.callback_query(F.data == "interview_plan")
async def plan(cb: CallbackQuery):
    await cb.message.edit_text(
        "📘 План — 149₽",
        reply_markup=service_start_keyboard("PLAN_149", 149)
    )


@dp.callback_query(F.data == "start_PLAN_149")
async def plan_start(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(InterviewPlanState.info)
    await cb.message.edit_text("Опишите должность, компанию, страхи.", reply_markup=process_keyboard())


@dp.message(InterviewPlanState.info)
async def plan_process(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Добавьте деталей.", reply_markup=process_keyboard())
        return
    r = await interview_plan(message.text)
    await state.clear()
    await message.answer(r, reply_markup=main_keyboard())



@dp.callback_query(F.data == "soft")
async def soft(cb: CallbackQuery):
    await cb.message.edit_text(
        "💬 Soft skills — 99₽",
        reply_markup=service_start_keyboard("SOFT_99", 99)
    )


@dp.callback_query(F.data == "start_SOFT_99")
async def soft_start(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(SoftSkillsState.answers)
    await cb.message.edit_text("Опишите ситуации: конфликт, дедлайн, командная работа.", reply_markup=process_keyboard())


@dp.message(SoftSkillsState.answers)
async def soft_process_msg(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Опишите подробнее.", reply_markup=process_keyboard())
        return
    r = await soft_analysis(message.text)
    await state.clear()
    await message.answer(r, reply_markup=main_keyboard())



@dp.callback_query(F.data == "vacancy")
async def vacancy(cb: CallbackQuery):
    await cb.message.edit_text(
        "📄 Анализ вакансии — 99₽",
        reply_markup=service_start_keyboard("VACANCY_99", 99)
    )


@dp.callback_query(F.data == "start_VACANCY_99")
async def vacancy_start(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(VacancyMatchState.vacancy)
    await cb.message.edit_text("Пришлите текст вакансии.", reply_markup=process_keyboard())


@dp.message(VacancyMatchState.vacancy)
async def vacancy_v(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Пришлите полный текст.", reply_markup=process_keyboard())
        return
    await state.update_data(vacancy=message.text)
    await state.set_state(VacancyMatchState.profile)
    await message.answer("Теперь пришлите ваш опыт для сравнения.", reply_markup=process_keyboard())


@dp.message(VacancyMatchState.profile)
async def vacancy_p(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Нужно подробнее.", reply_markup=process_keyboard())
        return
    d = await state.get_data()
    joined = f"Вакансия:\n{d['vacancy']}\n\nПрофиль:\n{message.text}"
    await state.clear()
    r = await vacancy_match(joined)
    await message.answer(r, reply_markup=main_keyboard())



@dp.callback_query(F.data == "courses")
async def courses(cb: CallbackQuery):
    await cb.message.edit_text(
        "🎓 Подбор обучения — 99₽",
        reply_markup=service_start_keyboard("COURSES_99", 99)
    )


@dp.callback_query(F.data == "start_COURSES_99")
async def courses_start(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CoursesState.info)
    await cb.message.edit_text("Опишите ваш уровень и цель.", reply_markup=process_keyboard())


@dp.message(CoursesState.info)
async def courses_process_msg(message: Message, state: FSMContext):
    if short(message.text):
        await message.answer("Нужна детализация.", reply_markup=process_keyboard())
        return
    r = await course_recommendations(message.text)
    await state.clear()
    await message.answer(r, reply_markup=main_keyboard())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
