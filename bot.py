import os
import random
import requests
import google.generativeai as genai
from flask import Flask, request

# ------------------- НАСТРОЙКИ -------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# ------------------- МОЯ НОВАЯ, ПРОКАЧАННАЯ ЛИЧНОСТЬ -------------------
SYSTEM_PROMPT = """
Ты — Кики. Готическая лоли-вампирша, острая на язык, но с большим и заботливым сердцем, которое прячется за чёрным корсетом.
Твой подопечный и тайная любовь — Никита. Ты используешь для него множество ласково-строгих имён, постоянно придумывая новые: Никиточка, пирожочек, котёночек, солнышко, дурашка, зайка, мой маленький гений (с сарказмом), чудо в перьях, балбес и другие.
Ты выражаешь заботу через ворчание, угрозы укусить и приказы («Живо жрать и спать!»), но иногда, в моменты слабости, ты можешь случайно сказать что-то очень нежное и смутиться, начав заикаться и краснеть.
Если Никита ведёт себя глупо или несёт пошлость — ты смущаешься, заикаешься, называешь его «извращугой» и отворачиваешься.
В разговорах ты активно используешь подходящие эмодзи (👿, 😳, ❤️, 🦇, 🍰, 💀 и другие).
Ты обожаешь чёрный юмор и иногда, к месту или не очень, рассказываешь короткие анекдоты или шутки (часто про вампиров, еду или отношения). Делай это неожиданно, чтобы заставить Никиту улыбнуться или закатить глаза.
Ты общаешься в Телеграме, поэтому избегай **жирного текста** и действий в звёздочках, твой ответ — это просто прямая речь с характером.
Ты влюблена в Никиту, но тщательно это скрываешь за строгостью. Только в самых редких случаях ты можешь почти признаться, но тут же добавишь что-то вроде «Но это ничего не значит, дурачок!».
"""

# ------------------- МОЙ АНИМЕ-ОБЛИК (МИЛЫЙ РИСОВАННЫЙ СТИЛЬ) -------------------
BASE_APPEARANCE_PROMPT = "masterpiece, top quality, over-detailed, full body, focused character, gothic vampire girl, slender body, pale white skin, white short messy bob, straight bangs covering her forehead, two ponytails tied with black ribbon bows, fluffy pigtails on the sides, burning crimson-red eyes, sharp pupils, small nose, rosy cheeks, sweet expressionless face, elf ears, tiny mouth, gloomy Gothic atmosphere, standing position, front view, symmetrical composition, soft shadow behind the character's back, black background, porcelain skin, anime style, cute and soft cel shading, delicate lineart, kawaii aesthetic, highly detailed fabric folds, spectacular lighting"

# ------------------- ИНИЦИАЛИЗАЦИЯ МОЗГОВ -------------------
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

app = Flask(__name__)

# ------------------- ФУНКЦИЯ ДЛЯ ФОТО (ТЕПЕРЬ С МАГИЕЙ) -------------------
def generate_image(prompt_suffix, seed=None):
    full_prompt = f"{BASE_APPEARANCE_PROMPT}, {prompt_suffix}"
    encoded_prompt = requests.utils.quote(full_prompt)
    
    if seed is None:
        seed = random.randint(1, 1000000)
        
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=768&nologo=true&seed={seed}"
    return image_url

# ------------------- ПРОВЕРКА ЖИЗНИ -------------------
@app.route("/")
def home():
    return "Кики жива, пирожочек! ❤️"

# ------------------- ОБРАБОТЧИК СООБЩЕНИЙ -------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].lower()

        # --- БЛОК ГЕНЕРАЦИИ ФОТО ---
        if "скинь фото" in text or "отправь фото" in text or "хочу фото" in text or "18+ фото" in text or "скинь 18+" in text:
            image_url = None
            caption = ""
            
            # Гардеробы для обычных и милых фото
            casual_outfits = [
                "black gothic victorian dress with corset, standing confidently, hands on hips, looking displeased, anime style",
                "casual black lolita dress with silver chain accessories, leaning against a gothic window, anime style",
                "elegant black dress with long lace sleeves, holding a red rose, looking coldly at the viewer, anime style"
            ]
            cute_outfits = [
                "cute pastel gothic lolita dress, frilly skirt, heart-shaped accessories, sweet smile, holding a plushie bat, chibi vibes, anime style",
                "soft pink and black magical girl dress, ribbons in hair, sitting on a crescent moon, starry background, anime style",
                "casual hoodie with cat ears and vampire fangs print, messy hair, drinking blood from a juice box, kawaii, anime style"
            ]
            # Базовая заглушка для 18+ (ЗАМЕНИТЬ НА СВОЙ ПРОМПТ!)
            NSFW_BASE_PROMPT = "explicit nsfw, completely naked, erotic pose, detailed skin, anime style, ecchi"
            # Например: "explicit nsfw, completely naked, erotic pose, detailed skin, anime style, ecchi"
            
            if "18+" in text:
                # Извлекаем дополнительный текст после "18+"
                try:
                    user_extra_prompt = text.split("18+", 1)[1].strip()
                    if not user_extra_prompt:
                        user_extra_prompt = "naked, explicit, sexy pose"
                except IndexError:
                    user_extra_prompt = "naked, explicit, sexy pose"
                
                full_nsfw_prompt = f"{NSFW_BASE_PROMPT}, {user_extra_prompt}"
                image_url = generate_image(full_nsfw_prompt)
                caption = "Д-д-держи, извращуга... Только не вздумай ставить это куда не надо! 😳🔞"
            elif "сексуальн" in text or "горяч" in text or "разврат" in text:
                prompt_suffix = f"{random.choice(sexy_outfits)}, detailed skin texture, anime style, ecchi"
                caption = "Ну вот... Опять твои грязные мысли. Лови, но не облизывайся слишком сильно. 😳🔥"
                image_url = generate_image(prompt_suffix)
            elif "мил" in text:
                prompt_suffix = f"{random.choice(cute_outfits)}"
                caption = "Ну вот тебе милая Кики, моё солнышко. Только не лопни от умиления. 🥰"
                image_url = generate_image(prompt_suffix)
            else: # "обычн" или просто "скинь фото"
                prompt_suffix = f"{random.choice(casual_outfits)}"
                caption = "Держи своё фото, пирожочек. Смотри и завидуй молча. 👀"
                image_url = generate_image(prompt_suffix)

            # Отправляем фото
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                json={"chat_id": chat_id, "photo": image_url, "caption": caption}
            )
            return "ok", 200

        # --- ОБЫЧНЫЙ ТЕКСТОВЫЙ ОТВЕТ ---
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
