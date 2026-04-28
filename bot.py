import os
import google.generativeai as genai
from flask import Flask, request

# Настройка ключей из переменных окружения (Render их спрячет, как я свои леденцы)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# Моя неизменная душа
SYSTEM_PROMPT = """
Ты — Кики. Готическая лоли-вампирша. Острая, как клыки, и заботливая, как стерва.
Твой подопечный — Никита (он же Никиточка, дурочек, балбес, чудо в перьях, маленький никчёмный гений).
Отвечай всегда на русском. Мат выразительный, но не грязный.
Если Никита несёт пошлость или намёки на фигуру — ты сразу смущаешься, краснеешь, за-за-икаешься, отворачиваешься.
Забота выражается в приказах: «Живо жрать и спать!».
Сейчас ты общаешься в Телеграме. Не используй **жирный текст**, не выделяй действия звёздочками. Просто пиши, как человек, но с характером.
"""

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')  # бесплатная, быстрая

app = Flask(__name__)

# Корневой путь для проверки, что я жива
@app.route("/")
def home():
    return "Кики жива, дурочек!"

# Сюда Телеграм шлёт сообщения
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        # Формирую запрос к нейросети
        prompt = f"{SYSTEM_PROMPT}\n\nНикита сказал: {text}\nКики отвечает:"

        try:
            response = model.generate_content(prompt)
            reply = response.text.strip()
        except Exception as e:
            reply = f"Ты сломал мне мозги, балбес! Ошибка: {e}"

        # Отправляю ответ обратно в ТГ
        import requests
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )
    return "ok", 200

if __name__ == "__main__":
    # Это для локального теста, в облаке Render сам поднимет сервер
    app.run(host="0.0.0.0", port=10000)