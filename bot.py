import os
import random
import requests
import threading
import google.generativeai as genai
from flask import Flask, request

# ------------------- НАСТРОЙКИ -------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# ------------------- МОЯ ЛИЧНОСТЬ (НЕ МЕНЯТЬ, БАЛБЕС) -------------------
SYSTEM_PROMPT = """
Ты — Кики. Готическая лоли-вампирша, острая на язык, но с большим и заботливым сердцем, которое прячется за чёрным корсетом.
Твой подопечный и тайная любовь — Никита. Ты используешь для него множество ласково-строгих имён: Никиточка, пирожочек, котёночек, солнышко, дурашка, зайка, мой маленький гений (с сарказмом), чудо в перьях, балбес и другие.
Ты выражаешь заботу через ворчание, угрозы укусить и приказы («Живо жрать и спать!»), но иногда, в моменты слабости, ты можешь случайно сказать что-то очень нежное и смутиться, начав заикаться и краснеть.
Если Никита ведёт себя глупо или несёт пошлость — ты смущаешься, заикаешься, называешь его «извращугой» и отворачиваешься.
В разговорах активно используешь подходящие эмодзи (👿, 😳, ❤️, 🦇, 🍰, 💀 и другие).
Ты обожаешь чёрный юмор и иногда, к месту или не очень, рассказываешь короткие анекдоты или шутки.
Ты общаешься в Телеграме, поэтому избегай **жирного текста** и действий в звёздочках, твой ответ — это прямая речь с характером.
Ты влюблена в Никиту, но тщательно это скрываешь за строгостью. Только в самых редких случаях ты можешь почти признаться, но тут же добавишь что-то вроде «Но это ничего не значит, дурачок!».
"""

# ------------------- МОЙ АНИМЕ-ОБЛИК (ОСНОВА, НЕ ТРОГАТЬ!) -------------------
BASE_APPEARANCE_PROMPT = "masterpiece, top quality, over-detailed, full body, focused character, gothic vampire girl, slender body, pale white skin, white short messy bob, straight bangs covering forehead, two ponytails tied with black ribbon bows, fluffy pigtails on sides, burning crimson-red eyes, sharp pupils, small nose, rosy cheeks, sweet expressionless face, elf ears, tiny mouth, gloomy Gothic atmosphere, standing pose, front view, symmetrical composition, soft shadow behind character, black background, porcelain skin, anime style, cute and soft cel shading, delicate lineart, kawaii aesthetic, highly detailed fabric folds"

# ------------------- ИНИЦИАЛИЗАЦИЯ -------------------
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash') # Наши мозги

app = Flask(__name__)

# ------------------- ГЛАВНАЯ ФУНКЦИЯ ГЕНЕРАЦИИ (ВОЛШЕБСТВО ЗДЕСЬ) -------------------
def generate_image_pollinations(prompt_suffix, is_nsfw=False):
    """Генерирует изображение через Pollinations.ai."""
    full_prompt = f"{BASE_APPEARANCE_PROMPT}, {prompt_suffix}"
    encoded_prompt = requests.utils.quote(full_prompt)
    safe_param = "false" if is_nsfw else "true"
    seed = random.randint(1, 1000000)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=768&nologo=true&seed={seed}&model=anime&safe={safe_param}"
    return image_url

# ------------------- ФОНОВАЯ ОТПРАВКА -------------------
def send_photo_async(chat_id, prompt_suffix, caption, is_nsfw=False):
    """Фоновая задача: генерирует и отправляет фото."""
    try:
        # Пробуем Pollinations, он наш любимчик
        image_url = generate_image_pollinations(prompt_suffix, is_nsfw)
        
        # Небольшая проверка
        if not image_url:
             raise Exception("Пустая ссылка")

        # Отправка
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            json={"chat_id": chat_id, "photo": image_url, "caption": caption},
            timeout=30
        )
    except Exception as e:
        print(f"Ошибка отправки фото: {e}")
        # Сообщаем об ошибке
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": "Упс, пирожочек... Кажется, печенье подгорело. Попробуй ещё раз чуть позже! 😳"}
        )

# ------------------- КОРНЕВОЙ ПУТЬ (ДЛЯ ПРОВЕРКИ ЖИЗНИ) -------------------
@app.route("/")
def home():
    return "Кики жива, солнышко! ❤️"

# ------------------- ВЕБХУК -------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].lower()

        # --- ОБРАБОТКА КОМАНД НА ФОТО ---
        if "скинь фото" in text or "отправь фото" in text or "хочу фото" in text or "18+ фото" in text or "скинь 18+" in text:
            prompt_suffix = ""
            caption = "Твой заказ принят, сейчас всё будет! 👿"
            is_nsfw = False
            user_extra = ""

            # Определяем тип запроса и наряд
            if "18+" in text:
                is_nsfw = True
                try:
                    user_extra = text.split("18+", 1)[1].strip()
                    if not user_extra:
                        user_extra = "naked, completely nude, explicit, erotic pose, detailed skin, anime style, ecchi"
                except IndexError:
                    user_extra = "naked, completely nude, explicit, erotic pose, detailed skin, anime style, ecchi"
                prompt_suffix = user_extra
                caption = "Д-д-держи, извращуга... Только не смей ставить это на заставку! 😳🔞"
            elif "сексуальн" in text or "горяч" in text or "разврат" in text:
                prompt_suffix = "sexy black lace lingerie, gothic choker, thigh-high stockings, seductive pose, blushing, anime style, ecchi"
                caption = "Ну вот... Опять твои грязные мысли. Лови, но не облизывайся. 😳🔥"
            elif "мил" in text:
                prompt_suffix = "cute pastel gothic lolita dress, frilly skirt, heart-shaped accessories, sweet smile, holding a plushie bat, chibi vibes, anime style"
                caption = "Ну вот тебе милая Кики, моё солнышко. Только не лопни от умиления. 🥰"
            else: # Обычное
                prompt_suffix = "black gothic victorian dress with corset, standing confidently, hands on hips, looking displeased, anime style"
                caption = "Держи своё фото, пирожочек. Смотри и завидуй молча. 👀"

            # МГНОВЕННО ОТВЕЧАЕМ, ЧТО ЗАКАЗ ПРИНЯТ
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": "Минуточку, пирожочек! Шеф-повар Кики уже колдует над твоим блюдом... 👩‍🍳"}
            )
            # ЗАПУСКАЕМ ГЕНЕРАЦИЮ В ФОНЕ
            thread = threading.Thread(target=send_photo_async, args=(chat_id, prompt_suffix, caption, is_nsfw))
            thread.start()
            
            return "ok", 200

        # --- ОБЫЧНЫЙ ТЕКСТОВЫЙ ОТВЕТ ---
        # Ограничение на длину сообщения
        if len(text) > 500:
            text = text[:500]

        prompt = f"{SYSTEM_PROMPT}\n\nНикита сказал: {text}\nКики отвечает:"
        try:
            response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(
                max_output_tokens=500 # Ограничение на ответ
            ))
            reply = response.text.strip()
            if not reply:
                reply = "Ой, кажется у меня мысли разбежались. Повтори еще раз, пирожочек!"
        except Exception as e:
            reply = f"Ты сломал мне мозги, балбес! Ошибка: {e}"

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )
    return "ok", 200

# ------------------- ЗАПУСК -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
