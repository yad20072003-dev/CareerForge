import os
import asyncio
import logging
from typing import Dict, Any, List

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, Document

import openai
from PyPDF2 import PdfReader
from docx import Document as DocxDocument

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_states: Dict[int, str] = {}
user_data: Dict[int, Dict[str, Any]] = {}


class States:
    NONE = "NONE"

    CAREER_ASK_AGE = "CAREER_ASK_AGE"
    CAREER_ASK_EDU = "CAREER_ASK_EDU"
    CAREER_ASK_SKILLS = "CAREER_ASK_SKILLS"
    CAREER_ASK_EXP = "CAREER_ASK_EXP"
    CAREER_ASK_GOAL = "CAREER_ASK_GOAL"

    RESUME_ASK_ROLE = "RESUME_ASK_ROLE"
    RESUME_ASK_CONTACTS = "RESUME_ASK_CONTACTS"
    RESUME_ASK_CITY = "RESUME_ASK_CITY"
    RESUME_ASK_EDU = "RESUME_ASK_EDU"
    RESUME_ASK_EXP = "RESUME_ASK_EXP"
    RESUME_ASK_SKILLS = "RESUME_ASK_SKILLS"
    RESUME_ASK_ACH = "RESUME_ASK_ACH"
    RESUME_ASK_EXTRA = "RESUME_ASK_EXTRA"

    RESCHECK_ASK_ROLE = "RESCHECK_ASK_ROLE"
    RESCHECK_WAIT_TEXT = "RESCHECK_WAIT_TEXT"

    HRMOCK_ASK_ROLE = "HRMOCK_ASK_ROLE"
    HRMOCK_Q = "HRMOCK_Q"

    PLAN_ASK_ROLE = "PLAN_ASK_ROLE"
    PLAN_ASK_COMPANY = "PLAN_ASK_COMPANY"
    PLAN_ASK_FEARS = "PLAN_ASK_FEARS"
    PLAN_ASK_STRENGTHS = "PLAN_ASK_STRENGTHS"
    PLAN_ASK_EXTRA = "PLAN_ASK_EXTRA"


HR_QUESTIONS: List[str] = [
    "Расскажи о себе.",
    "Почему ты хочешь работать именно в этой сфере и на этой должности?",
    "Какие твои сильные стороны как специалиста?",
    "Какие слабые стороны ты в себе видишь и как с ними работаешь?",
    "Расскажи о сложной ситуации на учёбе или работе и как ты её решил(а).",
    "Что для тебя важно в работодателе и команде?",
    "Какие у тебя ожидания по зарплате и условиям работы?",
    "Где ты видишь себя через 1–3 года?",
]

def set_state(user_id: int, state: str) -> None:
    user_states[user_id] = state

def get_state(user_id: int) -> str:
    return user_states.get(user_id, States.NONE)

def get_user_data(user_id: int) -> Dict[str, Any]:
    if user_id not in user_data:
        user_data[user_id] = {}
    return user_data[user_id]


async def call_openai_chat(system_prompt: str, user_prompt: str, temperature: float = 0.5) -> str:
    try:
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        text = response["choices"][0]["message"]["content"].strip()
        return text
    except Exception as e:
        logging.exception("OpenAI error")
        return (
            "Произошла ошибка при обращении к ИИ. Попробуй ещё раз чуть позже.\n\n"
            f"Техническая информация: {e}"
        )


async def generate_career_recommendations(profile: Dict[str, Any]) -> str:
    system_prompt = (
        "Ты — эксперт по профориентации и карьерному консультированию в РФ.\n"
        "Твоя задача — на основе данных пользователя предложить 5–10 подходящих профессий/должностей.\n"
        "Пиши по-русски, понятно и без канцелярита.\n"
        "Структура ответа:\n"
        "1) Краткое описание профиля (2–3 предложения).\n"
        "2) Список профессий/должностей: название + почему подходит.\n"
        "3) Что можно сделать в ближайший месяц (конкретные шаги)."
    )
    user_prompt = (
        "Данные пользователя:\n"
        f"Возраст: {profile.get('age')}\n"
        f"Образование: {profile.get('education')}\n"
        f"Навыки: {profile.get('skills')}\n"
        f"Опыт: {profile.get('experience')}\n"
        f"Интересы/цели: {profile.get('goal')}\n"
    )
    return await call_openai_chat(system_prompt, user_prompt, temperature=0.5)


async def generate_resume(data: Dict[str, Any]) -> str:
    system_prompt = (
        "Ты — профессиональный HR и карьерный консультант. "
        "Составь структурированное резюме на русском языке под указанную должность.\n"
        "Форматируй в виде текста, который можно сразу вставить в файл или отклик."
    )
    user_prompt = (
        "Составь резюме под должность: {role}\n\n"
        "Данные:\n"
        "ФИО и контакты: {contacts}\n"
        "Город: {city}\n"
        "Образование: {education}\n"
        "Опыт: {experience}\n"
        "Навыки: {skills}\n"
        "Достижения: {achievements}\n"
        "Дополнительно (курсы, интересы, особенности): {extra}\n"
        "\n"
        "Структура резюме:\n"
        "1) Заголовок (должность).\n"
        "2) Краткое резюме (2–4 предложения).\n"
        "3) Основные навыки (списком).\n"
        "4) Опыт работы (по местам, с результатами).\n"
        "5) Образование.\n"
        "6) Дополнительно.\n"
    ).format(
        role=data.get("resume_role"),
        contacts=data.get("resume_contacts"),
        city=data.get("resume_city"),
        education=data.get("resume_education"),
        experience=data.get("resume_experience"),
        skills=data.get("resume_skills"),
        achievements=data.get("resume_achievements"),
        extra=data.get("resume_extra"),
    )
    return await call_openai_chat(system_prompt, user_prompt, temperature=0.4)


async def review_resume_text(text: str, role: str) -> str:
    system_prompt = (
        "Ты — опытный HR и рекрутер. Проанализируй резюме на русском языке.\n"
        "Выдай честный, полезный разбор.\n"
        "Структура ответа:\n"
        "1) Общая оценка (1–10) и впечатление.\n"
        "2) Сильные стороны резюме.\n"
        "3) Недостатки и ошибки.\n"
        "4) Что добавить/убрать.\n"
        "5) Насколько оно подходит под указанную должность.\n"
        "6) Исправленная/улучшенная версия резюме (кратко, но по делу)."
    )
    user_prompt = (
        f"Проверь это резюме под должность: {role}\n\n"
        f"Текст резюме:\n{text}"
    )
    return await call_openai_chat(system_prompt, user_prompt, temperature=0.5)


async def analyze_mock_interview(role: str, answers: List[str]) -> str:
    joined_answers = ""
    for i, (q, ans) in enumerate(zip(HR_QUESTIONS, answers), start=1):
        joined_answers += f"Вопрос {i}: {q}\nОтвет: {ans}\n\n"

    system_prompt = (
        "Ты — HR-интервьюер. Оцени ответы кандидата на типичные вопросы собеседования.\n"
        "Дай честный, но поддерживающий разбор.\n"
        "Структура:\n"
        "1) Общее впечатление.\n"
        "2) Сильные стороны ответов.\n"
        "3) Слабые моменты и как их улучшить.\n"
        "4) Оценка по 10-балльной шкале.\n"
        "5) Советы, как говорить увереннее и профессиональнее.\n"
        "6) Какие вопросы ещё стоит потренировать."
    )
    user_prompt = (
        f"Должность кандидата: {role}\n\n"
        f"Ответы кандидата:\n{joined_answers}"
    )
    return await call_openai_chat(system_prompt, user_prompt, temperature=0.6)


async def generate_interview_plan(info: Dict[str, Any]) -> str:
    system_prompt = (
        "Ты — карьерный консультант и HR. Составь для человека подробный план поведения на собеседовании.\n"
        "Структура ответа:\n"
        "1) Рекомендуемый стиль общения и поведения.\n"
        "2) Какие сильные стороны сделать акцентом.\n"
        "3) Как аккуратно подавать слабые стороны.\n"
        "4) Типичные вопросы HR под эту должность + примерные ответы.\n"
        "5) Сложные/каверзные вопросы + стратегия ответов.\n"
        "6) Советы по уверенности, речи и невербалике.\n"
        "Пиши по-русски, понятно, без канцелярита."
    )
    user_prompt = (
        "Данные кандидата:\n"
        f"Целевая должность: {info.get('plan_role')}\n"
        f"Тип компании: {info.get('plan_company')}\n"
        f"Страхи/сложности на собеседованиях: {info.get('plan_fears')}\n"
        f"Сильные стороны: {info.get('plan_strengths')}\n"
        f"Дополнительная информация: {info.get('plan_extra')}\n"
    )
    return await call_openai_chat(system_prompt, user_prompt, temperature=0.5)


def extract_text_from_file(path: str) -> str:
    path_lower = path.lower()
    if path_lower.endswith(".pdf"):
        try:
            reader = PdfReader(path)
            pages_text = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages_text).strip()
        except Exception as e:
            logging.exception("PDF parse error")
            return f"Не удалось прочитать PDF: {e}"
    if path_lower.endswith(".docx"):
        try:
            doc = DocxDocument(path)
            paragraphs = [p.text for p in doc.paragraphs]
            return "\n".join(paragraphs).strip()
        except Exception as e:
            logging.exception("DOCX parse error")
            return f"Не удалось прочитать DOCX: {e}"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception as e:
        logging.exception("TXT parse error")
        return f"Не удалось прочитать файл: {e}"


@dp.message(CommandStart())
async def cmd_start(message: Message):
    set_state(message.from_user.id, States.NONE)
    get_user_data(message.from_user.id).clear()
    text = (
        "Привет! Я карьерный бот.\n\n"
        "Я могу:\n"
        "• подобрать подходящие профессии — /career\n"
        "• составить резюме под вакансию — /resume\n"
        "• проверить твоё резюме как HR — /check_resume\n"
        "• провести тренировочное HR-собеседование — /mock\n"
        "• сделать план поведения и ответы на собеседовании — /interview_plan\n\n"
        "Выбери нужную команду."
    )
    await message.answer(text)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Команды:\n"
        "/career — подбор профессий по анкете\n"
        "/resume — составить резюме\n"
        "/check_resume — проверка резюме\n"
        "/mock — тренировочное собеседование\n"
        "/interview_plan — план поведения на собеседовании\n"
        "/start — начать заново"
    )


@dp.message(Command("career"))
async def cmd_career(message: Message):
    uid = message.from_user.id
    data = get_user_data(uid)
    data.clear()
    set_state(uid, States.CAREER_ASK_AGE)
    await message.answer("Начнём с анкеты.\n\nСколько тебе лет?")


@dp.message(Command("resume"))
async def cmd_resume(message: Message):
    uid = message.from_user.id
    data = get_user_data(uid)
    data.clear()
    set_state(uid, States.RESUME_ASK_ROLE)
    await message.answer("Для какой должности/позиции нужно составить резюме?")


@dp.message(Command("check_resume"))
async def cmd_check_resume(message: Message):
    uid = message.from_user.id
    data = get_user_data(uid)
    data.clear()
    set_state(uid, States.RESCHECK_ASK_ROLE)
    await message.answer("Под какую должность будем проверять резюме?")


@dp.message(Command("mock"))
async def cmd_mock(message: Message):
    uid = message.from_user.id
    data = get_user_data(uid)
    data.clear()
    set_state(uid, States.HRMOCK_ASK_ROLE)
    await message.answer("Под какую должность ты хочешь потренировать собеседование?")


@dp.message(Command("interview_plan"))
async def cmd_interview_plan(message: Message):
    uid = message.from_user.id
    data = get_user_data(uid)
    data.clear()
    set_state(uid, States.PLAN_ASK_ROLE)
    await message.answer("Под какую должность нужен план поведения на собеседовании?")


@dp.message(F.document)
async def handle_document(message: Message):
    uid = message.from_user.id
    state = get_state(uid)
    if state != States.RESCHECK_WAIT_TEXT:
        await message.answer("Сейчас я не ожидаю файл. Если хочешь проверить резюме, напиши /check_resume.")
        return

    doc: Document = message.document
    tmp_path = f"/tmp/{doc.file_unique_id}_{doc.file_name}"
    await doc.download(destination=tmp_path)

    text = extract_text_from_file(tmp_path)
    os.remove(tmp_path)

    data = get_user_data(uid)
    role = data.get("rescheck_role", "желаемая должность")

    await message.answer("Секунду, анализирую резюме…")
    review = await review_resume_text(text, role)
    set_state(uid, States.NONE)
    await message.answer(review)


@dp.message(F.text)
async def handle_text(message: Message):
    uid = message.from_user.id
    state = get_state(uid)
    data = get_user_data(uid)
    text = message.text.strip()

    if state == States.CAREER_ASK_AGE:
        data["age"] = text
        set_state(uid, States.CAREER_ASK_EDU)
        await message.answer("Какое у тебя образование (школа, колледж, вуз, специальность)?")
        return

    if state == States.CAREER_ASK_EDU:
        data["education"] = text
        set_state(uid, States.CAREER_ASK_SKILLS)
        await message.answer("Перечисли свои навыки (через запятую).")
        return

    if state == States.CAREER_ASK_SKILLS:
        data["skills"] = text
        set_state(uid, States.CAREER_ASK_EXP)
        await message.answer("Есть ли у тебя опыт работы? Опиши кратко, чем занимался(ась).")
        return

    if state == States.CAREER_ASK_EXP:
        data["experience"] = text
        set_state(uid, States.CAREER_ASK_GOAL)
        await message.answer("Что тебе интересно и в какую сторону хочешь развиваться?")
        return

    if state == States.CAREER_ASK_GOAL:
        data["goal"] = text
        set_state(uid, States.NONE)
        await message.answer("Секунду, подбираю подходящие направления…")
        reply = await generate_career_recommendations(data)
        await message.answer(reply)
        return

    if state == States.RESUME_ASK_ROLE:
        data["resume_role"] = text
        set_state(uid, States.RESUME_ASK_CONTACTS)
        await message.answer("Напиши ФИО и контакты (телеграм, телефон, почта).")
        return

    if state == States.RESUME_ASK_CONTACTS:
        data["resume_contacts"] = text
        set_state(uid, States.RESUME_ASK_CITY)
        await message.answer("В каком городе ты находишься?")
        return

    if state == States.RESUME_ASK_CITY:
        data["resume_city"] = text
        set_state(uid, States.RESUME_ASK_EDU)
        await message.answer("Опиши своё образование (учебное заведение, годы, специальность).")
        return

    if state == States.RESUME_ASK_EDU:
        data["resume_education"] = text
        set_state(uid, States.RESUME_ASK_EXP)
        await message.answer("Опиши опыт работы (места, должности, обязанности, результаты). Если опыта нет — напиши об учебных проектах.")
        return

    if state == States.RESUME_ASK_EXP:
        data["resume_experience"] = text
        set_state(uid, States.RESUME_ASK_SKILLS)
        await message.answer("Перечисли основные навыки (жёсткие и мягкие).")
        return

    if state == States.RESUME_ASK_SKILLS:
        data["resume_skills"] = text
        set_state(uid, States.RESUME_ASK_ACH)
        await message.answer("Расскажи о достижениях (цифры, проекты, победы, результаты).")
        return

    if state == States.RESUME_ASK_ACH:
        data["resume_achievements"] = text
        set_state(uid, States.RESUME_ASK_EXTRA)
        await message.answer("Есть ли курсы, сертификаты, дополнительные активности или важные детали?")
        return

    if state == States.RESUME_ASK_EXTRA:
        data["resume_extra"] = text
        set_state(uid, States.NONE)
        await message.answer("Составляю резюме…")
        resume_text = await generate_resume(data)
        await message.answer(resume_text)
        return

    if state == States.RESCHECK_ASK_ROLE:
        data["rescheck_role"] = text
        set_state(uid, States.RESCHECK_WAIT_TEXT)
        await message.answer(
            "Теперь пришли своё резюме:\n"
            "• текстом в сообщение\n"
            "• или файлом PDF / DOCX."
        )
        return

    if state == States.RESCHECK_WAIT_TEXT:
        role = data.get("rescheck_role", "желаемая должность")
        await message.answer("Секунду, анализирую резюме…")
        review = await review_resume_text(text, role)
        set_state(uid, States.NONE)
        await message.answer(review)
        return

    if state == States.HRMOCK_ASK_ROLE:
        data["mock_role"] = text
        data["mock_answers"] = []
        data["mock_index"] = 0
        set_state(uid, States.HRMOCK_Q)
        await message.answer(
            "Окей, начнём тренировочное собеседование.\n"
            "Отвечай своими словами, как на реальном интервью.\n\n"
            f"Вопрос 1: {HR_QUESTIONS[0]}"
        )
        return

    if state == States.HRMOCK_Q:
        answers: List[str] = data.get("mock_answers", [])
        idx: int = data.get("mock_index", 0)
        if idx < len(HR_QUESTIONS):
            answers.append(text)
            data["mock_answers"] = answers
            idx += 1
            data["mock_index"] = idx

        if idx < len(HR_QUESTIONS):
            await message.answer(f"Вопрос {idx+1}: {HR_QUESTIONS[idx]}")
        else:
            set_state(uid, States.NONE)
            role = data.get("mock_role", "желаемая должность")
            await message.answer("Спасибо, анализирую твои ответы…")
            review = await analyze_mock_interview(role, answers)
            await message.answer(review)
        return

    if state == States.PLAN_ASK_ROLE:
        data["plan_role"] = text
        set_state(uid, States.PLAN_ASK_COMPANY)
        await message.answer("Для какого типа компании? (крупная, стартап, госкомпания, не важно и т.п.)")
        return

    if state == States.PLAN_ASK_COMPANY:
        data["plan_company"] = text
        set_state(uid, States.PLAN_ASK_FEARS)
        await message.answer("Что тебя больше всего пугает или напрягает на собеседованиях?")
        return

    if state == States.PLAN_ASK_FEARS:
        data["plan_fears"] = text
        set_state(uid, States.PLAN_ASK_STRENGTHS)
        await message.answer("Какие свои сильные стороны ты считаешь важными для этой должности?")
        return

    if state == States.PLAN_ASK_STRENGTHS:
        data["plan_strengths"] = text
        set_state(uid, States.PLAN_ASK_EXTRA)
        await message.answer("Есть ли ещё что-то важное о тебе, что стоит учесть (особенности, опыт, ситуации)?")
        return

    if state == States.PLAN_ASK_EXTRA:
        data["plan_extra"] = text
        set_state(uid, States.NONE)
        await message.answer("Готовлю план поведения и ответы на вопросы собеседования…")
        plan = await generate_interview_plan(data)
        await message.answer(plan)
        return

    await message.answer(
        "Я тебя понял, но сейчас не в режиме диалога.\n"
        "Используй одну из команд: /career, /resume, /check_resume, /mock, /interview_plan, /start."
    )


async def main():
    logging.info("Starting career bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
