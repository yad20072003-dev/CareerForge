import os
import asyncio
import logging
from typing import Dict, Any, List

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    Document,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.filters import CommandStart, Command

import openai
from PyPDF2 import PdfReader
from docx import Document as DocxDocument

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY не задан")

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

    SYMBIO_ASK_NAME = "SYMBIO_ASK_NAME"
    SYMBIO_ASK_AGE = "SYMBIO_ASK_AGE"
    SYMBIO_ASK_ROLE = "SYMBIO_ASK_ROLE"
    SYMBIO_ASK_EXP = "SYMBIO_ASK_EXP"
    SYMBIO_ASK_SKILLS = "SYMBIO_ASK_SKILLS"
    SYMBIO_ASK_FEARS = "SYMBIO_ASK_FEARS"
    SYMBIO_ASK_EXTRA = "SYMBIO_ASK_EXTRA"


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

PROMPT_CAREER = """
Ты — эксперт по профориентации и карьерному консультированию в РФ.

Твоя задача — на основе данных пользователя:
1) Сформировать краткий портрет человека (2–3 предложения).
2) Предложить 7–12 подходящих профессий/должностей.
   Для каждой:
   • название должности,
   • 3–5 причин, почему она ему подходит,
   • примерный уровень входа: «без опыта», «начинающий», «средний».
3) Составить план действий на ближайшие 30 дней:
   • что изучать,
   • какие шаги предпринять,
   • как искать первые возможности.
4) Указать типичные ошибки, которых этому человеку лучше избегать.

Пиши по-русски, живым и понятным языком, без канцелярита и воды.
Не придумывай биографию — опирайся только на данные пользователя.
"""

PROMPT_RESUME = """
Ты — профессиональный HR и карьерный консультант. Твоя задача — составить сильное резюме на русском языке под конкретную должность.

Структура резюме:
1) Заголовок с должностью.
2) Краткое резюме-позиционирование (3–5 предложений): кто человек, его ключевая ценность для работодателя, чем полезен.
3) Ключевые навыки:
   • жёсткие (hard skills),
   • мягкие (soft skills).
4) Опыт работы:
   • по местам,
   • должность,
   • период,
   • 3–6 конкретных обязанностей и результатов,
   • по возможности — цифры (рост, экономия, показатели).
5) Образование.
6) Достижения.
7) Курсы, сертификаты, дополнительная активность.
8) Дополнительная информация (языки, особенности, готовность к переезду и др.).

Не используй сухой канцеляритет, но сохраняй деловой стиль. Не выдумывай факты, опирайся только на данные пользователя, при необходимости аккуратно структурируй и формулируй.
"""

PROMPT_RESCHECK = """
Ты — опытный HR и рекрутер. Проанализируй резюме кандидата.

Сделай:
1) Общую оценку резюме по 10-балльной шкале и краткое первое впечатление.
2) Сильные стороны резюме: что уже хорошо, что выгодно выделяет кандидата.
3) Недостатки и ошибки: структура, стиль, содержание, повторы, лишнее, пробелы.
4) Конкретные рекомендации по улучшению:
   • что удалить,
   • что переформулировать,
   • что добавить.
5) Оценку соответствия указанной должности: чего не хватает для этой роли.
6) Упрощённую исправленную версию резюме: структурированную, более сильную, но без выдуманных мест работы.

Пиши по-русски, честно, по делу, с уважением к кандидату.
"""

PROMPT_MOCK = """
Ты — профессиональный HR-интервьюер.

Перед тобой ответы кандидата на стандартные вопросы собеседования. Проанализируй их.

Сделай:
1) Общее впечатление от кандидата и стиля его ответов.
2) Сильные стороны ответов: где он звучит убедительно, профессионально, живо.
3) Слабые стороны:
   • где человек «плавает»,
   • где звучит неуверенно или слишком общо,
   • где можно подумать о доработке.
4) Конкретные рекомендации по улучшению:
   • как перефразировать,
   • какие примеры добавить,
   • какие акценты поменять.
5) Оценку кандидата по 10-балльной шкале как для HR.
6) Советы по поведению на собеседовании: голос, уверенность, структура ответов, работа с волнением.

Пиши по-русски, поддерживающе, но честно.
"""

PROMPT_PLAN = """
Ты — карьерный консультант и HR одновременно.

Требуется составить персональный план поведения на собеседовании.

Сделай:
1) Рекомендуемый стиль общения и поведения: как лучше держаться, как говорить.
2) На какие сильные стороны кандидата делать акцент и как именно их подавать.
3) Как аккуратно подавать слабые стороны и уязвимые места, не вредя себе.
4) 15 типичных вопросов HR под эту должность + примерные сильные ответы.
5) 10 каверзных/сложных вопросов + стратегия ответа.
6) Типичные ошибки, которые этому человеку лучше не допускать.
7) Советы по уверенности, невербалике, голосу и работе с волнением.

Пиши по-русски, понятно, структурировано и прикладно, чтобы человек мог прямо по тексту готовиться.
"""

PROMPT_SYMBIO = """
Ты — сильный карьерный консультант, HR и автор резюме в одном лице.

На основе данных пользователя сделай комплексный отчёт «путь кандидата»:

1) Краткий портрет человека (2–3 абзаца).
2) 5–10 подходящих профессий/должностей с аргументацией.
3) Черновик резюме под целевую должность.
4) Мини-проверка этого резюме: 3–5 пунктов, что хорошо и что улучшить.
5) План поведения на собеседовании:
   • стиль общения,
   • сильные стороны,
   • где быть аккуратнее.
6) 10 примерных вопросов HR под эту роль + примерные ответы для этого человека.
7) План действий на ближайшие 30 дней по поиску работы.

Не выдумывай факты: опирайся только на данные пользователя, но формулируй их максимально выгодно и честно.
Пиши по-русски, структурировано.
"""


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
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.exception("OpenAI error")
        return f"Произошла ошибка при обращении к ИИ: {e}"


def extract_text_from_file(path: str) -> str:
    path_lower = path.lower()
    try:
        if path_lower.endswith(".pdf"):
            reader = PdfReader(path)
            pages_text = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages_text).strip()
        if path_lower.endswith(".docx"):
            doc = DocxDocument(path)
            paragraphs = [p.text for p in doc.paragraphs]
            return "\n".join(paragraphs).strip()
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception as e:
        logging.exception("file parse error")
        return f"Не удалось прочитать файл: {e}"


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧭 Подбор профессий"), KeyboardButton(text="📄 Составить резюме")],
            [KeyboardButton(text="🧾 Проверка резюме"), KeyboardButton(text="🎤 HR-собеседование")],
            [KeyboardButton(text="🎯 План собеседования"), KeyboardButton(text="🌀 Симбиоз услуг")],
            [KeyboardButton(text="ℹ Инфо"), KeyboardButton(text="📜 Условия пользования")],
        ],
        resize_keyboard=True,
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    get_user_data(message.from_user.id).clear()
    set_state(message.from_user.id, States.NONE)
    await message.answer(
        "Привет! Я карьерный AI-бот.\n\n"
        "Помогу с выбором направления, резюме и подготовкой к собеседованиям.\n\n"
        "Выбери действие в меню ниже.",
        reply_markup=main_keyboard(),
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Я помогу тебе с карьерой:\n\n"
        "🧭 Подбор профессий — подберу направления по анкете.\n"
        "📄 Составить резюме — сделаю резюме под вакансию.\n"
        "🧾 Проверка резюме — разберу твой файл/текст как HR.\n"
        "🎤 HR-собеседование — потренируем ответы.\n"
        "🎯 План собеседования — дам стратегию поведения.\n"
        "🌀 Симбиоз услуг — сделаю всё вместе в одном отчёте.",
        reply_markup=main_keyboard(),
    )


@dp.message(F.text == "ℹ Инфо")
async def info(message: Message):
    await message.answer(
        "Мои услуги:\n\n"
        "🧭 Подбор профессий — анализ твоих данных и список подходящих должностей.\n"
        "📄 Составить резюме — грамотное резюме под конкретную роль.\n"
        "🧾 Проверка резюме — разбор сильных и слабых мест + улучшенная версия.\n"
        "🎤 HR-собеседование — тренировочное интервью с разбором.\n"
        "🎯 План собеседования — персональная стратегия поведения и ответы.\n"
        "🌀 Симбиоз услуг — комплексный отчёт: профессии, резюме, план, вопросы/ответы.",
        reply_markup=main_keyboard(),
    )


@dp.message(F.text == "📜 Условия пользования")
async def terms(message: Message):
    await message.answer(
        "📜 Условия пользования:\n\n"
        "• Бот не является юридическим лицом и официальным HR-агентством.\n"
        "• Все рекомендации носят информационный и консультационный характер.\n"
        "• Ты сам принимаешь решения о своём трудоустройстве и несёшь за них ответственность.\n"
        "• Данные используются только для формирования ответов и не предназначены для передачи третьим лицам.\n"
        "• Используя бота, ты соглашаешься с этими условиями.",
        reply_markup=main_keyboard(),
    )


@dp.message(F.text == "🧭 Подбор профессий")
async def btn_career(message: Message):
    uid = message.from_user.id
    data = get_user_data(uid)
    data.clear()
    set_state(uid, States.CAREER_ASK_AGE)
    await message.answer("Начнём с анкеты.\n\nСколько тебе лет?")


@dp.message(F.text == "📄 Составить резюме")
async def btn_resume(message: Message):
    uid = message.from_user.id
    data = get_user_data(uid)
    data.clear()
    set_state(uid, States.RESUME_ASK_ROLE)
    await message.answer("Для какой должности нужно составить резюме?")


@dp.message(F.text == "🧾 Проверка резюме")
async def btn_rescheck(message: Message):
    uid = message.from_user.id
    data = get_user_data(uid)
    data.clear()
    set_state(uid, States.RESCHECK_ASK_ROLE)
    await message.answer("Под какую должность будем проверять резюме?")


@dp.message(F.text == "🎤 HR-собеседование")
async def btn_mock(message: Message):
    uid = message.from_user.id
    data = get_user_data(uid)
    data.clear()
    set_state(uid, States.HRMOCK_ASK_ROLE)
    await message.answer("Для какой должности хочешь потренировать собеседование?")


@dp.message(F.text == "🎯 План собеседования")
async def btn_plan(message: Message):
    uid = message.from_user.id
    data = get_user_data(uid)
    data.clear()
    set_state(uid, States.PLAN_ASK_ROLE)
    await message.answer("Для какой должности нужен план поведения на собеседовании?")


@dp.message(F.text == "🌀 Симбиоз услуг")
async def btn_symbio(message: Message):
    uid = message.from_user.id
    data = get_user_data(uid)
    data.clear()
    set_state(uid, States.SYMBIO_ASK_NAME)
    await message.answer("Как тебя зовут? Можно имя или ник.")


@dp.message(F.document)
async def handle_document(message: Message):
    uid = message.from_user.id
    state = get_state(uid)
    if state != States.RESCHECK_WAIT_TEXT:
        await message.answer("Сейчас я не ожидаю файл. Если хочешь проверить резюме, выбери «🧾 Проверка резюме».")
        return

    doc: Document = message.document
    tmp_path = f"/tmp/{doc.file_unique_id}_{doc.file_name}"
    await doc.download(destination=tmp_path)

    text = extract_text_from_file(tmp_path)
    try:
        os.remove(tmp_path)
    except Exception:
        pass

    data = get_user_data(uid)
    role = data.get("rescheck_role", "желаемая должность")

    await message.answer("Анализирую резюме как HR…")
    user_prompt = f"Должность: {role}\n\nТекст резюме:\n{text}"
    review = await call_openai_chat(PROMPT_RESCHECK, user_prompt, temperature=0.5)
    set_state(uid, States.NONE)
    await message.answer(review, reply_markup=main_keyboard())


@dp.message(F.text)
async def handle_text(message: Message):
    uid = message.from_user.id
    state = get_state(uid)
    data = get_user_data(uid)
    text = message.text.strip()

    if state == States.CAREER_ASK_AGE:
        data["age"] = text
        set_state(uid, States.CAREER_ASK_EDU)
        await message.answer("Какое у тебя образование? (школа, колледж, вуз, специальность)")
        return

    if state == States.CAREER_ASK_EDU:
        data["education"] = text
        set_state(uid, States.CAREER_ASK_SKILLS)
        await message.answer("Перечисли свои основные навыки через запятую.")
        return

    if state == States.CAREER_ASK_SKILLS:
        data["skills"] = text
        set_state(uid, States.CAREER_ASK_EXP)
        await message.answer("Расскажи коротко про опыт работы или учебные проекты. Если опыта нет — так и напиши.")
        return

    if state == States.CAREER_ASK_EXP:
        data["experience"] = text
        set_state(uid, States.CAREER_ASK_GOAL)
        await message.answer("В какую сторону хочешь развиваться? Что тебе интересно по ощущениям?")
        return

    if state == States.CAREER_ASK_GOAL:
        data["goal"] = text
        set_state(uid, States.NONE)
        await message.answer("Думаю над твоим профилем…")
        user_prompt = (
            f"Возраст: {data.get('age')}\n"
            f"Образование: {data.get('education')}\n"
            f"Навыки: {data.get('skills')}\n"
            f"Опыт: {data.get('experience')}\n"
            f"Цели и интересы: {data.get('goal')}\n"
        )
        reply = await call_openai_chat(PROMPT_CAREER, user_prompt, temperature=0.5)
        await message.answer(reply, reply_markup=main_keyboard())
        return

    if state == States.RESUME_ASK_ROLE:
        data["resume_role"] = text
        set_state(uid, States.RESUME_ASK_CONTACTS)
        await message.answer("Напиши ФИО (если хочешь) и контакты: телефон, почта, телеграм.")
        return

    if state == States.RESUME_ASK_CONTACTS:
        data["resume_contacts"] = text
        set_state(uid, States.RESUME_ASK_CITY)
        await message.answer("В каком городе ты находишься?")
        return

    if state == States.RESUME_ASK_CITY:
        data["resume_city"] = text
        set_state(uid, States.RESUME_ASK_EDU)
        await message.answer("Опиши своё образование: учебные заведения, годы, специальности.")
        return

    if state == States.RESUME_ASK_EDU:
        data["resume_education"] = text
        set_state(uid, States.RESUME_ASK_EXP)
        await message.answer("Опиши опыт работы: места, должности, обязанности, результаты. Если опыта нет — напиши про учебные/личные проекты.")
        return

    if state == States.RESUME_ASK_EXP:
        data["resume_experience"] = text
        set_state(uid, States.RESUME_ASK_SKILLS)
        await message.answer("Перечисли свои ключевые навыки: и жёсткие, и мягкие.")
        return

    if state == States.RESUME_ASK_SKILLS:
        data["resume_skills"] = text
        set_state(uid, States.RESUME_ASK_ACH)
        await message.answer("Расскажи о достижениях: проекты, результаты, цифры, победы.")
        return

    if state == States.RESUME_ASK_ACH:
        data["resume_achievements"] = text
        set_state(uid, States.RESUME_ASK_EXTRA)
        await message.answer("Есть ли курсы, сертификаты, дополнительная активность или важные детали?")
        return

    if state == States.RESUME_ASK_EXTRA:
        data["resume_extra"] = text
        set_state(uid, States.NONE)
        await message.answer("Составляю резюме…")
        user_prompt = (
            f"Целевая должность: {data.get('resume_role')}\n\n"
            f"ФИО и контакты: {data.get('resume_contacts')}\n"
            f"Город: {data.get('resume_city')}\n"
            f"Образование: {data.get('resume_education')}\n"
            f"Опыт: {data.get('resume_experience')}\n"
            f"Навыки: {data.get('resume_skills')}\n"
            f"Достижения: {data.get('resume_achievements')}\n"
            f"Дополнительно: {data.get('resume_extra')}\n"
        )
        resume_text = await call_openai_chat(PROMPT_RESUME, user_prompt, temperature=0.4)
        await message.answer(resume_text, reply_markup=main_keyboard())
        return

    if state == States.RESCHECK_ASK_ROLE:
        data["rescheck_role"] = text
        set_state(uid, States.RESCHECK_WAIT_TEXT)
        await message.answer(
            "Теперь пришли своё резюме:\n"
            "• либо текстом в следующем сообщении,\n"
            "• либо файлом PDF / DOCX.",
        )
        return

    if state == States.RESCHECK_WAIT_TEXT:
        role = data.get("rescheck_role", "желаемая должность")
        await message.answer("Анализирую резюме как HR…")
        user_prompt = f"Должность: {role}\n\nТекст резюме:\n{text}"
        review = await call_openai_chat(PROMPT_RESCHECK, user_prompt, temperature=0.5)
        set_state(uid, States.NONE)
        await message.answer(review, reply_markup=main_keyboard())
        return

    if state == States.HRMOCK_ASK_ROLE:
        data["mock_role"] = text
        data["mock_answers"] = []
        data["mock_index"] = 0
        set_state(uid, States.HRMOCK_Q)
        await message.answer(
            "Окей, проведём тренировочное HR-собеседование.\n"
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
            await message.answer(f"Вопрос {idx + 1}: {HR_QUESTIONS[idx]}")
        else:
            set_state(uid, States.NONE)
            role = data.get("mock_role", "желаемая должность")
            await message.answer("Спасибо, анализирую твои ответы…")
            joined_answers = ""
            for i, (q, ans) in enumerate(zip(HR_QUESTIONS, answers), start=1):
                joined_answers += f"Вопрос {i}: {q}\nОтвет: {ans}\n\n"
            user_prompt = f"Должность кандидата: {role}\n\nОтветы кандидата:\n{joined_answers}"
            review = await call_openai_chat(PROMPT_MOCK, user_prompt, temperature=0.6)
            await message.answer(review, reply_markup=main_keyboard())
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
        await message.answer("Есть ли ещё что-то важное о тебе, что стоит учесть?")
        return

    if state == States.PLAN_ASK_EXTRA:
        data["plan_extra"] = text
        set_state(uid, States.NONE)
        await message.answer("Готовлю план поведения и ответы на собеседовании…")
        user_prompt = (
            f"Целевая должность: {data.get('plan_role')}\n"
            f"Тип компании: {data.get('plan_company')}\n"
            f"Страхи и сложности: {data.get('plan_fears')}\n"
            f"Сильные стороны: {data.get('plan_strengths')}\n"
            f"Дополнительно: {data.get('plan_extra')}\n"
        )
        plan = await call_openai_chat(PROMPT_PLAN, user_prompt, temperature=0.5)
        await message.answer(plan, reply_markup=main_keyboard())
        return

    if state == States.SYMBIO_ASK_NAME:
        data["sym_name"] = text
        set_state(uid, States.SYMBIO_ASK_AGE)
        await message.answer("Сколько тебе лет?")
        return

    if state == States.SYMBIO_ASK_AGE:
        data["sym_age"] = text
        set_state(uid, States.SYMBIO_ASK_ROLE)
        await message.answer("Какая у тебя целевая должность или направление? (например: маркетолог, аналитик, разработчик, менеджер продаж)")
        return

    if state == States.SYMBIO_ASK_ROLE:
        data["sym_role"] = text
        set_state(uid, States.SYMBIO_ASK_EXP)
        await message.answer("Расскажи кратко про свой опыт: работа, подработки, проекты, учёба.")
        return

    if state == States.SYMBIO_ASK_EXP:
        data["sym_exp"] = text
        set_state(uid, States.SYMBIO_ASK_SKILLS)
        await message.answer("Перечисли свои ключевые навыки через запятую.")
        return

    if state == States.SYMBIO_ASK_SKILLS:
        data["sym_skills"] = text
        set_state(uid, States.SYMBIO_ASK_FEARS)
        await message.answer("Что тебя больше всего волнует/пугает в поиске работы и собеседованиях?")
        return

    if state == States.SYMBIO_ASK_FEARS:
        data["sym_fears"] = text
        set_state(uid, States.SYMBIO_ASK_EXTRA)
        await message.answer("Есть ли ещё важная информация о тебе, которую стоит учесть? (особенности, ограничения, цели)")
        return

    if state == States.SYMBIO_ASK_EXTRA:
        data["sym_extra"] = text
        set_state(uid, States.NONE)
        await message.answer("Готовлю для тебя комплексный карьерный отчёт…")
        user_prompt = (
            f"Имя: {data.get('sym_name')}\n"
            f"Возраст: {data.get('sym_age')}\n"
            f"Целевая должность/направление: {data.get('sym_role')}\n"
            f"Опыт: {data.get('sym_exp')}\n"
            f"Навыки: {data.get('sym_skills')}\n"
            f"Страхи и волнения: {data.get('sym_fears')}\n"
            f"Дополнительно: {data.get('sym_extra')}\n"
        )
        report = await call_openai_chat(PROMPT_SYMBIO, user_prompt, temperature=0.5)
        await message.answer(report, reply_markup=main_keyboard())
        return

    await message.answer(
        "Я тебя понял, но сейчас не в режиме диалога.\n"
        "Выбери действие в меню или напиши /start.",
        reply_markup=main_keyboard(),
    )


async def main():
    logging.info("Запуск карьерного бота…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
