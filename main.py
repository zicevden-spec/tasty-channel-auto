import os, json, requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = "@vkusno_test_kitchen"

prompt = 'Выбери случайную страну (Россия, Китай, Грузия, Италия, Япония, Таиланд, Индия, Мексика, Греция, Узбекистан, Франция, Испания, Турция, Корея) и её блюдо. Верни СТРОГО JSON: {"post": "пост МАКСИМУМ 950 символов: флаг+название, время, порции, калории, ингредиенты с граммами, 6-7 подробных шагов, секрет, история, хештеги. Если выходит длиннее 950 символов - убери блоки секрет и история, но оставь ингредиенты и шаги", "image_prompt": "english dish description"}'

key = os.environ.get("GROQ_API_KEY")
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": "groq/compound-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.9, "max_tokens": 4000})
print("Groq:", r.status_code)

content = r.json()["choices"][0]["message"]["content"]
print("Content:", content[:200])

data = json.loads(content[content.find("{"):content.rfind("}") + 1])
print("Length:", len(data["post"]))

image = "https://image.pollinations.ai/prompt/" + requests.utils.quote(data["image_prompt"]) + "?model=flux&width=1280&height=800&nologo=true"
r2 = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data={"chat_id": CHANNEL, "caption": data["post"], "photo": image})
print("Telegram:", r2.status_code)
