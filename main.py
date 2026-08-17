import os
import json
import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GROQ = os.environ["GROQ_API_KEY"]
CHANNEL = "@vkusno_test_kitchen"
STYLE = ", award-winning professional food photography, shot on DSLR 50mm lens, soft natural window light, shallow depth of field, dark rustic wooden table, gentle steam, vibrant appetizing colors, ultra realistic, high detail, magazine quality, no text, no watermark"

headers = {"Authorization": f"Bearer {GROQ}", "Content-Type": "application/json"}
ids = [m["id"] for m in requests.get("https://api.groq.com/openai/v1/models", headers=headers).json().get("data", [])]
print("Models:", ids)
choice = next((w for w in ["llama-3.1-8b-instant", "openai/gpt-oss-20b", "meta-llama/llama-4-scout-17b-16e-instruct"] if w in ids), None) or (ids[0] if ids else None)
print("Using:", choice)

PROMPT = 'Ты — опытный шеф-повар и фуд-блогер. Выбери СЛУЧАЙНУЮ страну из списка: Россия, Китай, Грузия, Италия, Япония, Таиланд, Индия, Мексика, Греция, Узбекистан, Франция, Испания, Турция, Корея и её известное блюдо. Верни СТРОГО валидный JSON без лишнего текста, с тремя полями.\nПоле "title" — [эмодзи флага] [аппетитное название блюда], не длиннее 60 символов.\nПоле "post" — текст ТОЧНО по шаблону, переносы строк обязательны:\n⏱ X мин\n🍽 X порций\n🔥 X ккал\n\n🛒 Ингредиенты:\n— ингредиент — точный вес\n— (каждый с новой строки)\n\n👩‍🍳 Шаги:\n1. подробный шаг\n2. (7-9 шагов; каждый шаг подробно описывает процесс: что делать, сколько минут, какой огонь, признак готовности)\n\n💡 Секрет: совет хозяйки\n\n📖 А вы знали? 2-3 предложения истории блюда\n\n#хештег #хештег\nПравила: у КАЖДОГО ингредиента точные граммы/миллилитры, включая воду, масло, соль; шаги настолько подробные, чтобы новичок приготовил без ошибок; текст 1500-2500 символов; тёплый простой тон; без грамматических ошибок.\nПоле "image_prompt" — detailed english description of the finished dish on a beautiful plate with garnish and sauce.'

try:
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": choice, "messages": [{"role": "user", "content": PROMPT}], "temperature": 0.9})
    print("Groq status:", r.status_code)
    content = r.json()["choices"][0]["message"]["content"]
    print("Groq said:", content[:200])
    data = json.loads(content[content.find("{"):content.rfind("}") + 1])
    image_url = "https://image.pollinations.ai/prompt/" + requests.utils.quote(data["image_prompt"] + STYLE) + "?model=flux&width=1280&height=800&nologo=true"
    r2 = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data={"chat_id": CHANNEL, "caption": data["title"], "photo": image_url})
    print("Photo status:", r2.status_code)
    r3 = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHANNEL, "text": data["post"]})
    print("Text status:", r3.status_code, r3.text[:100])
except Exception as e:
    print("ERROR:", e)
