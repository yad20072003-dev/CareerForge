import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv

from states import DialogStates
from keyboards import services_keyboard, result_keyboard, about_keyboard, admin_keyboard, mock_mode_keyboard
from products.products import PRODUCTS
from storage.db import (
    init_db,
    get_or_create_user_ab,
    save_result,
    get_last_result,
    log_event,
    stats_results_by_service,
    stats_events_by_service,
    export_csv_path,
)
from storage.pdf import build_pdf

from services.career_service import run as run_career
from services.resume_service import run as run_resume
from services.competitiveness_service import run as run_comp
from services.mock_service import generate_questions as mock_generate_questions, evaluate as mock_evaluate
from services.utils import bullets_to_text, score_to_text

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")

DEFAULT_ADMIN_ID = 8237054647
_raw_admins = os.getenv("ADMIN_IDS", "").strip()
if _raw_admins:
    ADMIN_IDS = {int(x.strip()) for x in _raw_admins.split(",") if x.strip().isdigit()}
else:
    ADMIN_IDS = {DEFAULT_ADMIN_ID}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
init_db()

WELCOME_A = (
    "Привет.\n"
    "Я карьерный HR-ассистент.\n\n"
    "Помогаю понять, где ты сейчас в карьере, что мешает расти и какие шаги дадут результат.\n\n"
    "Выбери услугу — и начнём 👇"
)

WELCOME_B = (
    "Привет!\n"
    "Я — карьерный HR-ассистент.\n\n"
    "Сделаем трезвый разбор: уровень, риски и понятные действия.\n"
    "Без воды и шаблонов.\n\n"
    "Выбирай, с чего стартовать 👇"
)

POLICY_TEXT = (
    "🔒 Политика конфиденциальности\n\n"
    "Бот обрабатывает только данные, необходимые для оказания услуги:\n"
    "— ваш Telegram ID\n"
    "— тексты, которые вы добровольно вводите\n"
    "— результаты анализа и отчёты\n\n"
    "Данные не продаются и не передаются третьим лицам, кроме случаев, предусмотренных законом.\n"
    "Сервис не запрашивает паспортные данные, номера телефонов и банковскую информацию.\n\n"
    "Используя бота, вы соглашаетесь на обработку данных, необходимых для его работы."
)

DISCLAIMER_TEXT = (
    "⚠️ Дисклеймер\n\n"
    "Рекомендации носят справочный и рекомендательный характер.\n"
    "Бот не гарантирует трудоустройство, повышение дохода или получение оффера.\n"
    "Цель — помочь трезво оценить ситуацию и принять более осознанные карьерные решения."
)

PDF_FOOTER = (
    "Дисклеймер: рекомендации носят рекомендательный характер и не являются гарантией трудоустройства.\n"
    "Если вы передавали в бота личные данные, вы сделали это добровольно в рамках получения услуги."
)

SERVICE_INTRO = {
    "career_diag": "Опиши текущую ситуацию: роль/опыт/цель и что именно сейчас не получается.",
    "career_full": "Опиши подробно: опыт, достижения, цель (роль/доход), что пробовал и что не выходит.",
    "resume_create": "Напиши: цель (роль), опыт (где работал и что делал), достижения в цифрах, навыки и инструменты.",
    "resume_audit": "Вставь текст своего резюме (или ключевые блоки). Я разберу и скажу, что исправить.",
    "competitiveness": "Опиши: роль/опыт/навыки, цель и на какие вакансии откликаешься. Если есть резюме — можно вставить.",
}

MICRO_STEPS = ["Анализирую ответы…", "Сопоставляю с ожиданиями HR…", "Формирую выводы и рекомендации…"]


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def send_menu(chat_id: int):
    await bot.send_message(chat_id, "Выбери услугу 👇", reply_markup=services_keyboard())


async def micro_progress(chat_id: int):
    for s in MICRO_STEPS:
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        await bot.send_message(chat_id, s)


def normalize_result(obj: dict) -> dict:
    out = {}
    out["summary"] = str(obj.get("summary", "") or "").strip()
    out["verdict"] = str(obj.get("verdict", "") or "").strip()
    out["strengths"] = bullets_to_text(obj.get("strengths", ""))
    out["risks"] = bullets_to_text(obj.get("risks", ""))
    out["recommendations"] = bullets_to_text(obj.get("recommendations", ""))
    out["next_steps"] = bullets_to_text(obj.get("next_steps", ""))

    score_total = obj.get("score_total", None)
    if score_total is not None:
        try:
            score_total = int(score_total)
        except Exception:
            score_total = None
    out["score_total"] = score_total
    out["score_breakdown"] = obj.get("score_breakdown", None) if isinstance(obj.get("score_breakdown", None), dict) else None
    out["score_interpretation"] = str(obj.get("score_interpretation", "") or "").strip()
    out["transcript"] = str(obj.get("transcript", "") or "").strip()

    out["score_text"] = score_to_text(out)
    return out


def next_step_hint(service: str) -> str:
    if service in {"career_diag", "career_full"}:
        return "• Если цель — больше откликов: сначала резюме (создать/усилить), затем mock-интервью."
    if service in {"resume_create", "resume_audit"}:
        return "• Дальше логично: оценка конкурентоспособности и тренировка интервью."
    if service == "competitiveness":
        return "• Следующий логичный шаг: mock-интервью — чтобы уверенно проходить собеседования."
    if service in {"mock_short", "mock_full"}:
        return "• Дальше логично: обновить резюме под цель и повторить mock через 3–7 дней."
    return ""


def mock_progress_line(i: int, n: int) -> str:
    extra = ""
    if n >= 10 and i == (n // 2):
        extra = " — экватор интервью"
    return f"Вопрос {i}/{n}{extra}"


@dp.message_handler(commands=["start"])
async def cmd_start(m: types.Message):
    ab = get_or_create_user_ab(m.from_user.id)
    log_event(m.from_user.id, "start", None)
    await m.answer(WELCOME_A if ab == "A" else WELCOME_B, reply_markup=services_keyboard())


@dp.message_handler(commands=["admin"])
async def cmd_admin(m: types.Message):
    if not is_admin(m.from_user.id):
        return
    await m.answer("Админ-панель", reply_markup=admin_keyboard())


@dp.callback_query_handler(lambda c: c.data == "menu")
async def cb_menu(c: types.CallbackQuery):
    await c.answer()
    await send_menu(c.message.chat.id)


@dp.callback_query_handler(lambda c: c.data == "about")
async def cb_about(c: types.CallbackQuery):
    await c.answer()
    await c.message.answer("О сервисе", reply_markup=about_keyboard())


@dp.callback_query_handler(lambda c: c.data == "policy")
async def cb_policy(c: types.CallbackQuery):
    await c.answer()
    await c.message.answer(POLICY_TEXT, reply_markup=about_keyboard())


@dp.callback_query_handler(lambda c: c.data == "disclaimer")
async def cb_disclaimer(c: types.CallbackQuery):
    await c.answer()
    await c.message.answer(DISCLAIMER_TEXT, reply_markup=about_keyboard())


@dp.callback_query_handler(lambda c: c.data.startswith("admin:"))
async def cb_admin(c: types.CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer()
        return

    action = c.data.split(":")[1]
    await c.answer()

    if action == "stats":
        done = stats_results_by_service()
        starts = stats_events_by_service("service_start")
        pdf = stats_events_by_service("pdf")

        def title_for(s: str) -> str:
            if s == "mock_short":
                return "🔴 Mock-интервью — быстро (5)"
            if s == "mock_full":
                return "🔴 Mock-интервью — полное (15)"
            return PRODUCTS.get(s, {}).get("title", s)

        lines = ["📊 Статистика (завершённые результаты):"]
        if done:
            for s, cnt in done:
                lines.append(f"— {title_for(s)}: {cnt}")
        else:
            lines.append("— пока нет данных")

        lines.append("\n🧭 Запуски услуг (клики):")
        if starts:
            for s, cnt in starts:
                lines.append(f"— {title_for(s)}: {cnt}")
        else:
            lines.append("— пока нет данных")

        lines.append("\n⬇️ PDF скачивания:")
        if pdf:
            for s, cnt in pdf:
                lines.append(f"— {title_for(s)}: {cnt}")
        else:
            lines.append("— пока нет данных")

        await c.message.answer("\n".join(lines), reply_markup=admin_keyboard())
        return

    if action == "export":
        path = "data/export_results.csv"
        export_csv_path(path)
        await c.message.answer_document(types.InputFile(path), reply_markup=admin_keyboard())
        return


@dp.callback_query_handler(lambda c: c.data.startswith("service:"))
async def cb_service(c: types.CallbackQuery, state: FSMContext):
    service = c.data.split(":")[1]
    await c.answer()

    log_event(c.from_user.id, "service_start", service)

    if service == "mock":
        await state.finish()
        await state.update_data(
            service="mock",
            mock_mode="",
            mock_n=0,
            mock_service_id="",
            mock_context="",
            mock_questions=[],
            mock_answers=[],
            mock_idx=0,
        )
        await c.message.answer("Выбери формат mock-интервью 👇", reply_markup=mock_mode_keyboard())
        return

    await state.update_data(service=service)
    title = PRODUCTS.get(service, {}).get("title", service)
    intro = SERVICE_INTRO.get(service, "Опиши ситуацию.")
    await c.message.answer(f"{title}\n\n{intro}")
    await DialogStates.waiting_input.set()


@dp.callback_query_handler(lambda c: c.data.startswith("mockmode:"))
async def cb_mockmode(c: types.CallbackQuery, state: FSMContext):
    await c.answer()
    mode = c.data.split(":")[1]
    if mode == "short":
        n = 5
        service_id = "mock_short"
        label = "⚡ Быстрое mock-интервью (5 вопросов)"
    else:
        n = 15
        service_id = "mock_full"
        label = "🧠 Полное mock-интервью (15 вопросов)"

    await state.update_data(service="mock", mock_mode=mode, mock_n=n, mock_service_id=service_id)
    await c.message.answer(
        f"{label}\n\nОпиши контекст:\n— на какую роль собеседуешься\n— кратко опыт и масштабы\n— что для тебя самое сложное на интервью",
    )
    await DialogStates.waiting_mock_context.set()


@dp.message_handler(state=DialogStates.waiting_input)
async def handle_input(m: types.Message, state: FSMContext):
    data = await state.get_data()
    service = data.get("service")
    text = (m.text or "").strip()
    if not text:
        await m.answer("Напиши текстом — так я смогу дать точный разбор.")
        return

    await micro_progress(m.chat.id)

    try:
        if service in {"career_diag", "career_full"}:
            raw = run_career(service, text)
        elif service in {"resume_create", "resume_audit"}:
            raw = run_resume(service, text)
        elif service == "competitiveness":
            raw = run_comp(text)
        else:
            await m.answer("Не удалось определить услугу. Вернись в меню.", reply_markup=services_keyboard())
            await state.finish()
            return
    except Exception:
        await m.answer("Ошибка при анализе. Попробуй ещё раз или сократи текст.", reply_markup=services_keyboard())
        await state.finish()
        return

    res = normalize_result(raw)
    hint = next_step_hint(service)
    if hint:
        res["next_steps"] = (res["next_steps"] + ("\n" if res["next_steps"] else "") + hint).strip()

    save_result(m.from_user.id, service, res)
    log_event(m.from_user.id, "service_done", service)
    await m.answer(res["summary"] if res["summary"] else "Готово.", reply_markup=result_keyboard(service))
    await state.finish()


@dp.message_handler(state=DialogStates.waiting_mock_context)
async def handle_mock_context(m: types.Message, state: FSMContext):
    data = await state.get_data()
    mode = data.get("mock_mode", "")
    n = int(data.get("mock_n", 0) or 0)
    service_id = data.get("mock_service_id", "")

    context = (m.text or "").strip()
    if not context:
        await m.answer("Опиши контекст текстом — так вопросы будут точнее.")
        return
    if mode not in {"short", "full"} or n not in {5, 15} or service_id not in {"mock_short", "mock_full"}:
        await m.answer("Режим не выбран. Вернись в меню.", reply_markup=services_keyboard())
        await state.finish()
        return

    await bot.send_chat_action(m.chat.id, types.ChatActions.TYPING)
    await m.answer("Готовлю вопросы интервью…")

    try:
        questions = mock_generate_questions(context, n)
    except Exception:
        questions = []

    if len(questions) < n:
        await m.answer("Не удалось подготовить вопросы. Попробуй ещё раз.", reply_markup=services_keyboard())
        await state.finish()
        return

    await state.update_data(mock_context=context, mock_questions=questions, mock_answers=[], mock_idx=0)

    await m.answer(f"{mock_progress_line(1, n)}\n\n{questions[0]}")
    await DialogStates.waiting_mock_answer.set()


@dp.message_handler(state=DialogStates.waiting_mock_answer)
async def handle_mock_answer(m: types.Message, state: FSMContext):
    data = await state.get_data()
    context = data.get("mock_context", "")
    questions = data.get("mock_questions", [])
    answers = data.get("mock_answers", [])
    idx = int(data.get("mock_idx", 0) or 0)
    n = int(data.get("mock_n", 0) or 0)
    service_id = data.get("mock_service_id", "")

    a = (m.text or "").strip()
    if not a:
        await m.answer("Ответь текстом — можно коротко, но по делу.")
        return

    if not isinstance(questions, list) or n not in {5, 15} or service_id not in {"mock_short", "mock_full"}:
        await m.answer("Сессия интервью сбилась. Вернись в меню.", reply_markup=services_keyboard())
        await state.finish()
        return

    answers = list(answers) if isinstance(answers, list) else []
    answers.append(a)
    idx += 1

    if idx < n:
        await state.update_data(mock_answers=answers, mock_idx=idx)
        await m.answer(f"{mock_progress_line(idx + 1, n)}\n\n{questions[idx]}")
        return

    await micro_progress(m.chat.id)

    try:
        raw = mock_evaluate(context, questions, answers)
    except Exception:
        await m.answer("Ошибка при оценке интервью. Попробуй ещё раз.", reply_markup=services_keyboard())
        await state.finish()
        return

    res = normalize_result(raw)
    hint = next_step_hint(service_id)
    if hint:
        res["next_steps"] = (res["next_steps"] + ("\n" if res["next_steps"] else "") + hint).strip()

    save_result(m.from_user.id, service_id, res)
    log_event(m.from_user.id, "service_done", service_id)
    await m.answer(res["summary"] if res["summary"] else "Интервью завершено.", reply_markup=result_keyboard(service_id))
    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith("result:"))
async def cb_result(c: types.CallbackQuery):
    await c.answer()
    _, service, block = c.data.split(":")
    res = get_last_result(c.from_user.id, service)
    if not res:
        await c.message.answer("Результат не найден. Сначала пройди услугу.", reply_markup=services_keyboard())
        return

    if block == "pdf":
        log_event(c.from_user.id, "pdf", service)
        title = PRODUCTS.get(service, {}).get("title", service)
        if service == "mock_short":
            title = "🔴 Mock-интервью — быстро (5 вопросов)"
        elif service == "mock_full":
            title = "🔴 Mock-интервью — полное (15 вопросов)"
        path = f"data/{c.from_user.id}_{service}.pdf"
        build_pdf(path, title, res, PDF_FOOTER)
        await c.message.answer_document(types.InputFile(path))
        return

    if block == "full":
        labels = {
            "verdict": "🧾 HR-вердикт",
            "score_text": "📊 Оценка",
            "summary": "📌 Итог",
            "strengths": "💪 Сильные стороны",
            "risks": "⚠️ Риски",
            "recommendations": "🧭 Рекомендации",
            "next_steps": "➡️ Следующие шаги",
            "transcript": "🗣 Диалог",
        }
        parts = []
        for k in ["verdict", "score_text", "summary", "strengths", "risks", "recommendations", "next_steps", "transcript"]:
            v = str(res.get(k, "") or "").strip()
            if v:
                parts.append(f"{labels[k]}\n{v}")
        await c.message.answer("\n\n".join(parts) if parts else "Пустой результат.", reply_markup=result_keyboard(service))
        return

    if block == "score":
        t = str(res.get("score_text", "") or "").strip()
        await c.message.answer(t if t else "Оценка доступна только в mock-интервью.", reply_markup=result_keyboard(service))
        return

    t = str(res.get(block, "") or "").strip()
    if not t:
        await c.message.answer("Для этого блока данных не хватило.", reply_markup=result_keyboard(service))
        return
    await c.message.answer(t, reply_markup=result_keyboard(service))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
