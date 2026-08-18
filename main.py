import os, json, requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = "@vkusno_test_kitchen"

prompt = 'Выбери случайную страну (Россия, Китай, Грузия, Италия, Япония, Таиланд, Индия, Мексика, Греция, Узбекистан, Франция, Испания, Турция, Корея) и её блюдо. Верни СТРОГО JSON: {"post": "пост СТРОГО ДО 850 символов: флаг+название, время, порции, калории, ингредиенты с граммами, 6-7 шагов, секрет, история, хештеги. Если длиннее 850 - убери секрет и историю", "image_prompt": "START with the exact english dish name, then describe precisely how it looks: shape, color, main ingredients visible on the plate, garnish, sauce, tableware. The photo must be clearly recognizable as this exact dish"}'

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
