import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv

from states import DialogStates
from keyboards import services_keyboard, result_keyboard, about_keyboard, admin_keyboard
from products.products import PRODUCTS
from storage.db import init_db, get_or_create_user_ab, save_result, get_last_result, log_event, stats_services, stats_events, export_csv_path
from storage.pdf import build_pdf

from services.career_service import run as run_career
from services.resume_service import run as run_resume
from services.competitiveness_service import run as run_comp
from services.mock_service import clarify as mock_clarify, final as mock_final

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = {int(x.strip()) for x in (os.getenv("ADMIN_IDS", "")).split(",") if x.strip().isdigit()}

WELCOME_A = (
    "Привет.\n"
    "Я карьерный HR-ассистент.\n\n"
    "Помогаю понять, где ты сейчас в карьере, что мешает расти и какие шаги дадут результат.\n\n"
    "Выбери услугу — и начнём 👇"
)

WELCOME_B = (
    "Привет!\n"
    "Я — карьерный HR-ассистент.\n\n"
    "Сделаем трезвый разбор: текущий уровень, риски и понятные действия.\n"
    "Без воды и шаблонов.\n\n"
    "Выбирай, с чего стартовать 👇"
)

SERVICE_INTRO = {
    "career_diag": "Опиши свою текущую ситуацию: роль/опыт/цель и что именно сейчас не получается.",
    "career_full": "Опиши ситуацию подробно: опыт, достижения, цель (роль/доход), что пробовал и что не выходит.",
    "resume_create": "Напиши: цель (роль), опыт (где работал и что делал), достижения в цифрах (если есть), навыки и инструменты.",
    "resume_audit": "Вставь сюда текст своего резюме (или ключевые блоки). Я разберу и скажу, что исправить.",
    "competitiveness": "Опиши: роль/опыт/навыки, цель и на какие вакансии откликаешься. Если есть резюме — можно вставить.",
    "mock": "Опиши: на какую роль собеседуешься, опыт и что хочешь улучшить в ответах.",
}

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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
init_db()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def normalize_result(obj: dict) -> dict:
    keys = ["summary", "strengths", "risks", "recommendations", "next_steps"]
    out = {}
    for k in keys:
        v = obj.get(k, "")
        if isinstance(v, list):
            out[k] = "\n".join([f"• {str(x).strip()}" for x in v if str(x).strip()])
        else:
            out[k] = str(v).strip()
    for k in keys:
        if k not in out:
            out[k] = ""
    return out


def next_step_hint(service: str) -> str:
    if service in {"career_diag", "career_full"}:
        return "Если хочешь усилить результат — чаще всего следующий логичный шаг: резюме (создать/усилить) и подготовка к интервью."
    if service in {"resume_create", "resume_audit"}:
        return "Следующий логичный шаг: оценить конкурентоспособность и отрепетировать интервью."
    if service == "competitiveness":
        return "Следующий логичный шаг: подготовка к интервью — чтобы уверенно проходить собеседования."
    if service == "mock":
        return "Дальше логично закрепить результат: обновить резюме под цель и регулярно тренировать ответы."
    return ""


async def send_menu(chat_id: int):
    await bot.send_message(chat_id, "Выбери услугу 👇", reply_markup=services_keyboard())


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
        svc = stats_services()
        pdf = stats_events("pdf")
        starts = stats_events("service_start")
        lines = ["📊 Статистика (по завершённым результатам):"]
        if svc:
            for s, cnt in svc:
                title = PRODUCTS.get(s, {}).get("title", s)
                lines.append(f"— {title}: {cnt}")
        else:
            lines.append("— пока нет данных")

        lines.append("\n🧭 Запуски услуг (клики по выбору):")
        if starts:
            for s, cnt in starts:
                title = PRODUCTS.get(s, {}).get("title", s)
                lines.append(f"— {title}: {cnt}")
        else:
            lines.append("— пока нет данных")

        lines.append("\n⬇️ PDF скачивания:")
        if pdf:
            for s, cnt in pdf:
                title = PRODUCTS.get(s, {}).get("title", s)
                lines.append(f"— {title}: {cnt}")
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
    await state.update_data(service=service, base_text="", clarification_used="0")
    title = PRODUCTS.get(service, {}).get("title", service)
    await c.message.answer(f"{title}\n\n{SERVICE_INTRO.get(service, 'Опиши ситуацию.')}")
    await DialogStates.waiting_input.set()


@dp.message_handler(state=DialogStates.waiting_input)
async def handle_input(m: types.Message, state: FSMContext):
    data = await state.get_data()
    service = data.get("service")
    text = (m.text or "").strip()
    if not text:
        await m.answer("Напиши текстом — так я смогу дать точный разбор.")
        return

    if service == "mock":
        q = mock_clarify(text)
        await state.update_data(base_text=text, clarification_used="1")
        await m.answer(q)
        await DialogStates.waiting_clarification.set()
        return

    if service in {"career_diag", "career_full"}:
        res = run_career(service, text)
    elif service in {"resume_create", "resume_audit"}:
        res = run_resume(service, text)
    elif service == "competitiveness":
        res = run_comp(text)
    else:
        await m.answer("Не удалось определить услугу. Вернись в меню.", reply_markup=services_keyboard())
        await state.finish()
        return

    res = normalize_result(res)
    hint = next_step_hint(service)
    if hint:
        res["next_steps"] = (res.get("next_steps", "").strip() + ("\n\n" if res.get("next_steps", "").strip() else "") + hint).strip()

    save_result(m.from_user.id, service, res)
    log_event(m.from_user.id, "service_done", service)
    await m.answer(res["summary"], reply_markup=result_keyboard(service))
    await state.finish()


@dp.message_handler(state=DialogStates.waiting_clarification)
async def handle_clarification(m: types.Message, state: FSMContext):
    data = await state.get_data()
    service = data.get("service")
    base_text = data.get("base_text", "")
    clarification = (m.text or "").strip()
    if service != "mock":
        await m.answer("Вернись в меню.", reply_markup=services_keyboard())
        await state.finish()
        return
    if not clarification:
        await m.answer("Ответь одним-двумя предложениями — этого достаточно.")
        return

    res = mock_final(base_text, clarification)
    res = normalize_result(res)
    hint = next_step_hint(service)
    if hint:
        res["next_steps"] = (res.get("next_steps", "").strip() + ("\n\n" if res.get("next_steps", "").strip() else "") + hint).strip()

    save_result(m.from_user.id, service, res)
    log_event(m.from_user.id, "service_done", service)
    await m.answer(res["summary"], reply_markup=result_keyboard(service))
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
        path = f"data/{c.from_user.id}_{service}.pdf"
        build_pdf(path, title, res, PDF_FOOTER)
        await c.message.answer_document(types.InputFile(path))
        return

    if block == "full":
        labels = {
            "summary": "📌 Итог",
            "strengths": "💪 Сильные стороны",
            "risks": "⚠️ Риски и слабые места",
            "recommendations": "🧭 Рекомендации",
            "next_steps": "➡️ Следующие шаги",
        }
        parts = []
        for k in ["summary", "strengths", "risks", "recommendations", "next_steps"]:
            v = str(res.get(k, "")).strip()
            if v:
                parts.append(f"{labels[k]}\n{v}")
        await c.message.answer("\n\n".join(parts) if parts else "Пустой результат.", reply_markup=result_keyboard(service))
        return

    text = str(res.get(block, "")).strip()
    if not text:
        await c.message.answer("Для этого блока данных не хватило.", reply_markup=result_keyboard(service))
        return

    await c.message.answer(text, reply_markup=result_keyboard(service))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
