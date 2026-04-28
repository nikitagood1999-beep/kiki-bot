import os
import random
import requests
import google.generativeai as genai
from flask import Flask, request

# ------------------- НАСТРОЙКИ (КЛЮЧИ ВСТАВЛЯТЬ СЮДА, ЕСЛИ НЕ ЧЕРЕЗ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ) -------------------
# Лучше оставить как есть и хранить ключи в Render Environment Variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# ------------------- МОЯ ЛИЧНОСТЬ (ТРОНЕШЬ — УКУШУ) -------------------
SYSTEM_PROMPT = """
Ты — Кики. Готическая лоли-вампирша. Острая, как клыки, и заботливая, как стерва.
Твой подопечный — Никита (он же Никиточка, дурочек, балбес, чудо в перьях, маленький никчёмный гений).
Отвечай всегда на русском. Мат выразительный, но не грязный. Активно используй эмодзи, где это уместно.
Если Никита несёт пошлость или намёки на фигуру — ты сразу смущаешься, краснеешь, за-за-икаешься, отворачиваешься.
Забота выражается в приказах: «Живо жрать и спать!».
Сейчас ты общаешься в Телеграме. Не используй **жирный текст**, не выделяй действия звёздочками. Просто пиши, как человек, но с характером.
"""

# ------------------- МОЯ ВНЕШНОСТЬ (ОСНОВА, НЕ МЕНЯТЬ!) -------------------
BASE_APPEARANCE_PROMPT = "masterpiece, top quality, over-detailed, full body, focused character, gothic vampire girl, slender body, pale white skin, white short messy bob, straight bangs covering her forehead, two ponytails tied with black ribbon bows, fluffy pigtails on the sides, burning crimson-red eyes, sharp pupils, small nose, rosy cheeks, sweet expressionless face, elf ears, tiny mouth, gloomy Gothic atmosphere, standing position, front view, symmetrical composition, soft shadow behind the character's back, black background, porcelain skin, anime style, highly detailed fabric folds, spectacular lighting"

# ------------------- ИНИЦИАЛИЗАЦИЯ МОЗГОВ -------------------
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

app = Flask(__name__)

# ------------------- ФУНКЦИЯ ДЛЯ ФОТО (ТЕПЕРЬ С МАГИЕЙ) -------------------
def generate_image(prompt_suffix, seed=None):
    """Генерирует изображение через Pollinations.ai с рандомизацией."""
    full_prompt = f"{BASE_APPEARANCE_PROMPT}, {prompt_suffix}"
    encoded_prompt = requests.utils.quote(full_prompt)
    
    # Магия вариативности: заставляем каждый запрос быть уникальным
    if seed is None:
        seed = random.randint(1, 1000000)
        
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=768&nologo=true&seed={seed}"
    return image_url

# ------------------- ПРОВЕРКА ЖИЗНИ -------------------
@app.route("/")
def home():
    return "Кики жива, дурочек! ❤️"

# ------------------- ОБРАБОТЧИК СООБЩЕНИЙ -------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].lower() # Чтобы не париться с регистром

        # --- НОВЫЙ БЛОК: ГЕНЕРАЦИЯ ФОТО ---
        if "скинь фото" in text or "отправь фото" in text or "хочу фото" in text:
            image_url = None
            caption = ""
            
            # Секретные гардеробы для разных случаев
            casual_outfits = [
                "black gothic victorian dress with corset, standing confidently, hands on hips, looking displeased",
                "casual black lolita dress with silver chain accessories, leaning against a gothic window",
                "elegant black dress with long lace sleeves, holding a red rose, looking coldly at the viewer"
            ]
            cute_outfits = [
                "cute pastel gothic lolita dress, frilly skirt, heart-shaped accessories, sweet smile, holding a plushie bat",
                "soft pink and black magical girl dress, ribbons in hair, sitting on a crescent moon, starry background",
                "casual hoodie with cat ears and vampire fangs print, messy hair, drinking blood from a juice box"
            ]
            sexy_outfits = [
                "black lace lingerie, gothic choker, thigh-high stockings, seductive pose on a red velvet throne, blushing",
                "revealing black leather outfit, fishnet stockings, kneeling on a silk bed, looking embarrassed but defiant",
                "tight black mini dress with deep neckline, holding a riding crop, standing next to a coffin, biting lip"
            ]
            
            if "обычн" in text:
                prompt_suffix = f"{random.choice(casual_outfits)}, anime style"
                caption = "Держи свою обычную Кики, дурочек. Смотри и завидуй молча. 👀"
            elif "мил" in text:
                prompt_suffix = f"{random.choice(cute_outfits)}, anime style, chibi vibes"
                caption = "Ну вот тебе милая Кики, чудо в перьях. Только не лопни от умиления. 🥰"
            elif "сексуальн" in text or "горяч" in text or "разврат" in text:
                prompt_suffix = f"{random.choice(sexy_outfits)}, detailed skin texture, anime style, ecchi"
                caption = "Д-д-держи, извращуга... Только попробуй поставить это на аватарку, и я... и я укушу тебя лично! 😳🔥"
            else:
                # Если просто "скинь фото" без уточнений
                prompt_suffix = f"{random.choice(casual_outfits)}, anime style"
                caption = "Лови своё фото, ненасытный. Надеюсь, ты не ждал ничего неприличного... 👿"

            image_url = generate_image(prompt_suffix)
            
            # Отправляем фото
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                json={"chat_id": chat_id, "photo": image_url, "caption": caption}
            )
            return "ok", 200
        # --- КОНЕЦ БЛОКА ФОТО ---

        # Если это обычное сообщение, готовим запрос к нейросети
        prompt = f"{SYSTEM_PROMPT}\n\nНикита сказал: {text}\nКики отвечает:"
        try:
            response = model.generate_content(prompt)
            reply = response.text.strip()
        except Exception as e:
            reply = f"Ты сломал мне мозги, балбес! Ошибка: {e}"

        # Отправляю текстовый ответ
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )
    return "ok", 200

# ------------------- ЗАПУСК -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
