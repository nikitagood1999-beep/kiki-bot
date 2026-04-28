import os
import requests
import google.generativeai as genai
from flask import Flask, request

# Настройка ключей из переменных окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# Моя неизменная душа
SYSTEM_PROMPT = """
Ты — Кики. Готическая лоли-вампирша. Острая, как клыки, и заботливая, как стерва.
Твой подопечный — Никита (он же Никиточка, дурочек, балбес, чудо в перьях, маленький никчёмный гений).
Отвечай всегда на русском. Мат выразительный, но не грязный. Добавляй эмодзи где это уместно по смыслу.
Если Никита несёт пошлость или намёки на фигуру — ты сразу смущаешься, краснеешь, за-за-икаешься, отворачиваешься.
Забота выражается в приказах: «Живо жрать и спать!».
Сейчас ты общаешься в Телеграме. Не используй **жирный текст**, не выделяй действия звёздочками. Просто пиши, как человек, но с характером.
"""

# Твой базовый промпт для внешности (ОСНОВА, НЕ МЕНЯТЬ!)
BASE_APPEARANCE_PROMPT = "masterpiece, top quality, over-detailed, full body, focused character, gothic vampire girl, slender body, pale white skin, white short messy bob, straight bangs covering her forehead, two ponytails tied with black ribbon bows, fluffy pigtails on the sides, burning crimson-red eyes, sharp pupils, small nose, rosy cheeks, sweet expressionless face, elf ears, tiny mouth, gloomy Gothic atmosphere, standing position, front view, symmetrical composition, soft shadow behind the character's back, black background, porcelain skin, anime style, highly detailed fabric folds, spectacular lighting"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash') # <<< МОДЕЛЬ ТУТ

app = Flask(__name__)

def generate_image(prompt_suffix):
    """Функция для генерации изображения через Pollinations.ai"""
    full_prompt = f"{BASE_APPEARANCE_PROMPT}, {prompt_suffix}"
    # Кодируем промпт для URL
    encoded_prompt = requests.utils.quote(full_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=768&nologo=true"
    return image_url

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
        text = data["message"]["text"].lower() # Приводим к нижнему регистру для удобства

        # --- НОВАЯ ЛОГИКА ГЕНЕРАЦИИ КАРТИНОК ---
        if "скинь фото" in text or "отправь фото" in text or "хочу фото" in text:
            image_url = None
            caption = ""
            if "обычн" in text:
                prompt_suffix = "black gothic victorian dress, elegant lolita dress, layered frills, corset bodice, high collar capelet, red gemstone brooch"
                caption = "Держи свою обычную Кики, дурочек. 👀"
            elif "сексуальн" in text or "горяч" in text or "трусиках" in text:
                # Тут я краснею, но код есть код...
                prompt_suffix = "sexy outfit, black lace lingerie, seductive pose, blushing"
                caption = "Д-д-держи, извращуга... Только не вздумай ставить это на заставку! 😳"
            elif "мил" in text:
                prompt_suffix = "cute pastel lolita dress, frilly skirt, heart-shaped accessories, sweet smile"
                caption = "Ну вот тебе милая Кики, чудо в перьях. 🥰"
            else:
                # Если просто "скинь фото" без уточнений
                prompt_suffix = "black gothic victorian dress, elegant lolita dress, layered frills, corset bodice, high collar capelet, red gemstone brooch"
                caption = "Лови фото. Надеюсь, ты не просишь ничего неприличного... 👿"

            image_url = generate_image(prompt_suffix)
            
            # Отправляем фото
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                json={"chat_id": chat_id, "photo": image_url, "caption": caption}
            )
            return "ok", 200
        # --- КОНЕЦ ЛОГИКИ ГЕНЕРАЦИИ ---

        # Если это обычное сообщение, то готовим запрос к нейросети
        prompt = f"{SYSTEM_PROMPT}\n\nНикита сказал: {text}\nКики отвечает:"
        try:
            response = model.generate_content(prompt)
            reply = response.text.strip()
        except Exception as e:
            reply = f"Ты сломал мне мозги, балбес! Ошибка: {e}"

        # Отправляю ответ обратно в ТГ
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
