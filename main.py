from flask import Flask, request
import requests
import os

app = Flask(__name__)

# === 🔐 Параметрлер ===
BOT_TOKEN = "8110766276:AAHZvFiCBXGh3d7vihZHNAaBIPwnqgpaNoY"
GEMINI_API_KEY = "AIzaSyDM2rDqMM1eV6fEHCU-xcLxE1a_GW1v-sQ"

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# === 📩 Telegram-ға хабар жіберу ===
def send_message(chat_id, text, buttons=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if buttons:
        payload["reply_markup"] = {"keyboard": buttons, "resize_keyboard": True}
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

# === 💬 Gemini арқылы жауап алу ===
def ask_gemini(prompt):
    prompt_text = (
        "Сен кәсіби тур агентсің. "
        "Тек Дубай 🇦🇪 және Түркия 🇹🇷 туралы туризм, саяхат, баға, қонақүй, ұшу, виза, демалыс жайлы сұрақтарға жауап бер. "
        "Басқа тақырыптарға жауап берме. "
        f"Пайдаланушы сұрағы: {prompt}"
    )
    data = {"contents": [{"parts": [{"text": prompt_text}]}]}
    response = requests.post(
        GEMINI_URL,
        headers={
            "Content-Type": "application/json",
            "X-goog-api-key": GEMINI_API_KEY
        },
        json=data
    )
    if response.status_code == 200:
        try:
            js = response.json()
            return js["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return "⚠️ Жауап құрылымын талдау мүмкін болмады."
    else:
        return f"⚠️ Gemini қатесі: {response.text}"

# === 🌐 Webhook ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if not update or "message" not in update:
        return "no update"

    msg = update["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()

    # /start командасы
    if text.lower() == "/start":
        buttons = [["🇦🇪 Дубай", "🇹🇷 Түркия"]]
        welcome = (
            "🌴 <b>Тур агентке қош келдің!</b>\n\n"
            "Мен саған Дубай және Түркия елдеріне саяхат туралы ақпарат берем 🌍\n"
            "Төмендегі батырмалардың бірін таңда:"
        )
        send_message(chat_id, welcome, buttons)
        return "ok"

    # 🇦🇪 Дубай туралы
    if "дубай" in text.lower():
        reply = ask_gemini("Дубай турлары туралы жалпы мәлімет, бағасы және визалық талаптар")
        send_message(chat_id, f"🇦🇪 <b>Дубай туры:</b>\n\n{reply}")
        return "ok"

    # 🇹🇷 Түркия туралы
    if "түркия" in text.lower():
        reply = ask_gemini("Түркия турлары туралы жалпы мәлімет, бағасы және қонақүйлер жайлы")
        send_message(chat_id, f"🇹🇷 <b>Түркия туры:</b>\n\n{reply}")
        return "ok"

    # Басқа сұрақтарға тек туризм бойынша жауап
    reply = ask_gemini(text)
    send_message(chat_id, reply)
    return "ok"

# === 🏠 Үй беті ===
@app.route("/")
def home():
    return "🌍 Тур агент бот жұмыс істеп тұр ✅"

# === 🚀 Іске қосу ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
