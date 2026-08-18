import os, json, requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = "@vkusno_test_kitchen"

prompt = 'Выбери случайную страну (Россия, Китай, Грузия, Италия, Япония, Таиланд, Индия, Мексика, Греция, Узбекистан, Франция, Испания, Турция, Корея) и её известное блюдо. Верни СТРОГО JSON. Поле "post": текст ТОЛЬКО НА РУССКОМ, СТРОГО по шаблону ниже, каждая строка с новой строки, пустая строка между блоками, максимум 950 символов:\n[флаг] [страна] — [аппетитное название блюда]\n⏱️ Время: X мин\n👥 Порции: X\n🔥 Калории: X ккал\n\n🧂 Ингредиенты:\n- ингредиент — точный вес\n(каждый с новой строки, 6-10 позиций)\n\n🔪 Шаги:\n1. подробный шаг: действие, время, огонь, признак готовности\n(6-7 шагов, каждый с новой строки)\n\n🔐 Секрет: совет хозяйки\n\n📜 История: 2-3 предложения истории блюда\n\n#хештег #хештег\nЕсли выходит длиннее 950 символов - убери блоки История и Секрет, но сохрани ингредиенты и шаги. Поле "image_prompt" (только это поле на английском): START with the exact english dish name, then describe precisely: traditional plating, shape, colors, main ingredients visible on the plate, garnish, sauce, tableware; close-up of the dish itself, clearly recognizable as this exact dish.'

key = os.environ.get("GROQ_API_KEY")
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "groq/compound-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.9, "max_tokens": 4000})
print("Groq:", r.status_code)

content = r.json()["choices"][0]["message"]["content"]
print("Content:", content[:200])

data = json.loads(content[content.find("{"):content.rfind("}") + 1])
post = data["post"]
if len(post) > 1020:
    post = post[:1020]
    post = post[:post.rfind("\n")] + "\n..."
print("Length:", len(post))

image = "https://image.pollinations.ai/prompt/" + requests.utils.quote(data["image_prompt"]) + "?model=flux&width=1280&height=800&nologo=true"
r2 = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data={"chat_id": CHANNEL, "caption": post, "photo": image})
print("Telegram:", r2.status_code)
