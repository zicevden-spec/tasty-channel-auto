import os, json, requests
from datetime import date, datetime
from countries import COUNTRIES

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = "@recepty_i_istoriya"
STYLE = ", professional food photography, soft natural window light, shallow depth of field, rustic wooden table, vibrant appetizing colors, ultra realistic, magazine quality, no text, no watermark"

now = datetime.utcnow()
days = (now.date() - date(2026, 1, 1)).days
ru, en, cuisine = COUNTRIES[days % len(COUNTRIES)]
evening = now.hour >= 12
print("Country:", ru, "| evening slot:", evening)

if evening:
    prompt = 'Напиши интересный развёрнутый пост ТОЛЬКО НА РУССКОМ о кухне страны ' + ru + '. Верни СТРОГО JSON с одним полем "post". Шаблон поста: [флаг] [страна] — [цепляющий заголовок]\n\n🍽 Что это за кухня: 1-2 предложения\n\n✨ Интересные факты:\n- малоизвестный небанальный факт\n- ещё факт\n- ещё факт\n\n🥘 Главные ингредиенты и традиции: 2-3 предложения\n\n#хештег #хештег\nМаксимум 950 символов, переносы строк обязательны, тёплый тон, факты выбирай малоизвестные и небанальные.'
else:
    prompt = 'Страна сегодняшнего поста: ' + ru + '. Выбери её известное блюдо. Верни СТРОГО JSON. Поле "post": текст ТОЛЬКО НА РУССКОМ, СТРОГО по шаблону, каждая строка с новой строки, пустая строка между блоками, максимум 950 символов:\n[флаг] [страна] — [аппетитное название блюда]\n⏱️ Время: X мин\n👥 Порции: X\n🔥 Калории: X ккал\n\n🧂 Ингредиенты:\n- ингредиент — точный вес\n(каждый с новой строки, 6-10 позиций)\n\n🔪 Шаги:\n1. подробный шаг: действие, время, огонь, признак готовности\n(6-7 шагов, каждый с новой строки)\n\n🔐 Секрет: совет хозяйки\n\n📜 История: 2-3 предложения истории блюда\n\n#хештег #хештег\nЕсли выходит длиннее 950 символов - убери блоки История и Секрет, но сохрани ингредиенты и шаги. Поле "wiki": exact English Wikipedia article title for this dish (examples: Borscht, Sushi, Khinkali, Carbonara, Pad thai). Поле "image_prompt" (на английском): START with the exact english dish name; then KEY VISUAL IDENTIFIERS: exact colors, shape, signature elements; then traditional plating, garnish, sauce, tableware; close-up of the dish.'

key = os.environ.get("GROQ_API_KEY")
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

content = ""
for model in ["groq/compound-mini", "groq/compound", "llama-3.1-8b-instant"]:
    for attempt in range(2):
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.9, "max_tokens": 4000})
        print(f"Try {model} attempt {attempt+1}:", r.status_code)
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"] or ""
            print("Content[:150]:", content[:150])
            if "{" in content and "}" in content:
                break
    if content and "{" in content:
        break

if not content or "{" not in content:
    print("FAILED: no valid JSON from any model, skipping")
    exit(0)

data = json.loads(content[content.find("{"):content.rfind("}") + 1])
post = data["post"]
if len(post) > 1020:
    post = post[:1020]
    post = post[:post.rfind("\n")] + "\n..."
print("Length:", len(post))

UA = {"User-Agent": "TastyChannelAuto/1.0 (recipe channel bot)"}

def get_wiki_image(title):
    try:
        s = requests.get("https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(title), headers=UA)
        print("Wiki:", s.status_code, title)
        if s.status_code == 200:
            wj = s.json()
            img = wj.get("originalimage", {}).get("source")
            if not img and wj.get("thumbnail", {}).get("source"):
                img = wj["thumbnail"]["source"].replace("/320px-", "/800px-")
            return img
    except Exception as e:
        print("Wiki error:", e)
    return None

image = None
if evening:
    image = get_wiki_image(cuisine)
    if not image:
        image = "https://image.pollinations.ai/prompt/" + requests.utils.quote("traditional " + cuisine + " table spread with national dishes" + STYLE) + "?model=flux&width=1280&height=800&nologo=true"
else:
    wiki = data.get("wiki", "")
    if wiki:
        image = get_wiki_image(wiki)
    if not image:
        img_prompt = data.get("image_prompt", "")
        if not img_prompt:
            q = data.get("wiki", "").split("/")[-1].replace("_", " ")
        else:
            q = img_prompt.split(":")[0].split(",")[0].strip()
        print("Search query:", q)
        try:
            s = requests.get("https://en.wikipedia.org/w/api.php", params={"action": "opensearch", "search": q, "limit": 1, "format": "json"}, headers=UA)
            titles = s.json()[1]
            if titles:
                image = get_wiki_image(titles[0])
        except Exception as e:
            print("Search error:", e)
    if not image:
        print("Fallback to Pollinations")
        fallback_prompt = data.get("image_prompt", data.get("wiki", cuisine))
        image = "https://image.pollinations.ai/prompt/" + requests.utils.quote(fallback_prompt + STYLE) + "?model=flux&width=1280&height=800&nologo=true"
print("Image:", image[:100])

r2 = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data={"chat_id": CHANNEL, "caption": post, "photo": image})
print("Telegram:", r2.status_code)
