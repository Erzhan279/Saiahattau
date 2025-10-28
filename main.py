"""
Telegram Travel Bot 🇰🇿
Стартта жылы қарсы алу мәтіні:
👋 Сәлем! Мен саяхаттау тур агенті көмекшісімін.
🌍 Саяхатқа бірге шығайық!
Қай ел туралы білгің келеді?

[Дубай 🏝️]   [Түркия 🇹🇷]
"""

import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# =======================================================
# 🔐 Мұнда өз токендеріңді қой:
# -------------------------------------------------------
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
# =======================================================

SYSTEM_PROMPT = """
Сен — саяхаттау бойынша тур агент көмекшісісің.
Тек екі ел туралы ақпарат бересің: Дубай және Түркия.
Баға, маусым, виза, көрікті жерлер туралы қысқа әрі жылы жауап бер.
Басқа тақырыптарға жауап берме.
"""

SAMPLE_RESPONSES = {
    "dubai": (
        "🌴 **Дубай** туралы қысқаша:\n\n"
        "• Орташа тур (7 күн) — шамамен *900–1400 USD* адам басына.\n"
        "• Виза: электронды түрде оңай алынады.\n"
        "• Маусым: *қазан–сәуір* ең жайлы.\n"
        "• Көрікті жерлер: Бурж Халифа, шөл сафари, Дубай Молл.\n\n"
        "_Нақты күн айтсаң, тура ұсыныстар беремін._"
    ),
    "turkey": (
        "🇹🇷 **Түркия** туралы қысқаша:\n\n"
        "• Орташа тур (7 күн) — шамамен *450–900 USD* адам басына.\n"
        "• Виза: көптеген ел азаматтарына жеңілдетілген немесе визасыз.\n"
        "• Маусым: *маусым–қыркүйек* — жағажай маусымы.\n"
        "• Көрікті жерлер: Анталия, Каппадокия, Стамбул.\n\n"
        "_Күніңді айтсаң, нақты баға есептей аламын._"
    ),
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Старт командасы — қарсы алу және екі батырма."""
    keyboard = [
        [
            InlineKeyboardButton("Дубай 🏝️", callback_data="country:dubai"),
            InlineKeyboardButton("Түркия 🇹🇷", callback_data="country:turkey"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "👋 Сәлем! Мен саяхаттау тур агенті көмекшісімін.\n\n"
        "🌍 Саяхатқа бірге шығайық!\n"
        "Қай ел туралы білгің келеді?"
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пайдаланушы елді таңдағанда жауап беру."""
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    if not data.startswith("country:"):
        await query.edit_message_text("Қайта /start басып көріңіз 🙂")
        return

    country = data.split(":")[1].lower()

    # Егер Gemini API бар болса — сол арқылы жауап алуға болады
    if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        try:
            text = call_llm(country)
        except Exception:
            text = SAMPLE_RESPONSES.get(country, "Ақпарат табылмады.")
    else:
        text = SAMPLE_RESPONSES.get(country, "Ақпарат табылмады.")

    await query.edit_message_text(text, parse_mode="Markdown")


def call_llm(country: str) -> str:
    """Gemini API шақыру үлгісі (нақты URL мен форматты өзіңнің API құжатына сай өзгертіңдер)."""
    endpoint = "https://api.example.com/v1/generate"
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "system": SYSTEM_PROMPT,
        "prompt": f"Пайдаланушы {country} туралы ақпарат сұрайды.",
        "temperature": 0.3,
        "max_tokens": 400,
    }

    r = requests.post(endpoint, json=payload, headers=headers, timeout=10)
    if r.status_code != 200:
        raise Exception(f"LLM error {r.status_code}: {r.text}")
    data = r.json()
    return data.get("text", "Жауап табылмады.")


def main():
    logging.basicConfig(level=logging.INFO)
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("⚠️ Telegram токенін енгізуді ұмытпадың ба?")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("✅ Тур агент бот іске қосылды! /start басып көр.")
    app.run_polling()


if __name__ == "__main__":
    main()
