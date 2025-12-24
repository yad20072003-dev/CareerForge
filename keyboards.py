from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from products.products import PRODUCTS

def services_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    for k, v in PRODUCTS.items():
        kb.add(InlineKeyboardButton(v["title"], callback_data=f"service:{k}"))
    return kb

def mock_mode_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("⚡ Быстро (5 вопросов)", callback_data="mock:short"),
        InlineKeyboardButton("🧠 Полное (15 вопросов)", callback_data="mock:full"),
    )
    return kb

def result_keyboard(service):
    kb = InlineKeyboardMarkup(row_width=2)
    for k, t in [
        ("summary","📌 Итог"),
        ("verdict","🧾 HR-вердикт"),
        ("score","📊 Оценка"),
        ("strengths","💪 Сильные стороны"),
        ("risks","⚠️ Риски"),
        ("recommendations","🧭 Рекомендации"),
        ("next_steps","➡️ Следующие шаги"),
        ("transcript","🗣 Диалог"),
        ("full","📄 Полностью"),
        ("pdf","⬇️ PDF"),
    ]:
        kb.add(InlineKeyboardButton(t, callback_data=f"result:{service}:{k}"))
    return kb
