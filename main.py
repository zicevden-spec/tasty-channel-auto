import os
import json
import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GROQ = os.environ["GROQ_API_KEY"]
CHANNEL = "@vkusno_test_kitchen"
STYLE = ", professional food photography, soft natural window light, shallow depth of field, rustic wooden table, steam, vibrant colors, high detail, magazine quality"

headers = {"Authorization": f"Bearer {GROQ}", "Content-Type": "application/json"}
ids = [m["id"] for m in requests.get("https://api.groq.com/openai/v1/models", headers=headers).json().get("data", [])]
print("Models:", ids)
choice = next((w for w in ["llama-3.1-8b-instant", "openai/gpt-oss-20b", "meta-llama/llama-4-scout-17b-16e-instruct"] if w in ids), None) or (ids[0] if ids else None)
print("Using:", choice)

PROMPT = 'Ты — опытный шеф-повар и фуд-блогер. Выбери СЛУЧАЙНУЮ страну из списка: Россия, Китай, Грузия, Италия, Япония, Таиланд, Индия, Мексика, Греция, Узбекистан, Франция, Испания, Турция, Корея — и её известное блюдо. Верни СТРОГО валидный JSON без лишнего текста: {"post": "пост в формате: название блюда с эмодзи флага страны; строка: время | порции | калории; заголовок 🛒 Ингредиенты и список с ТОЧНЫМИ граммами и миллилитрами у КАЖДОГО ингредиента, включая воду, масло и соль; заголовок 👩‍🍳 Шаги и 5-7 коротких нумерованных шагов, один шаг = одно действие; заголовок 💡 Секрет и совет хозяйки; заголовок 📖 А вы знали? и 2-3 предложения интересной истории блюда; в конце 2 хештега. Весь пост НЕ длиннее 900 символов, пиши просто и понятно для занятой хозяйки", "image_prompt": "detailed english description of the finished dish served on a beautiful plate with garnish"}'

try:
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": choice, "messages": [{"role": "user", "content": PROMPT}], "temperature": 0.9})
    print("Groq status:", r.status_code)
    content = r.json()["choices"][0]["message"]["content"]
    print("Groq said:", content[:200])
    data = json.loads(content[content.find("{"):content.rfind("}") + 1])
    image_url = "https://image.pollinations.ai/prompt/" + requests.utils.quote(data["image_prompt"] + STYLE) + "?model=flux&width=1280&height=800&nologo=true"
    r2 = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data={"chat_id": CHANNEL, "caption": data["post"], "photo": image_url})
    print("Telegram status:", r2.status_code, r2.text[:200])
except Exception as e:
    print("ERROR:", e)
