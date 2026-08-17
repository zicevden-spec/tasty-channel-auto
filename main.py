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
BAD = ["whisper", "orpheus", "allam", "guard", "safeguard"]
good_ids = [m for m in ids if not any(b in m for b in BAD)]
print("Good models:", good_ids)
pref = ["groq/compound-mini", "groq/compound", "llama-3.1-8b-instant"]
candidates = [m for m in pref if m in good_ids] + [m for m in good_ids if m not in pref]
print("Candidates:", candidates)

PROMPT = 'Ты — опытный шеф-повар и фуд-блогер. Выбери СЛУЧАЙНУЮ страну из: Россия, Китай, Грузия, Италия, Япония, Таиланд, Индия, Мексика, Греция, Узбекистан, Франция, Испания, Турция, Корея и её известное блюдо. Верни ТОЛЬКО валидный JSON без каких-либо размышлений, без блоков <think>, без пояснений, сразу начинай с {.\nПоля:\n"post" — пост ТОЧНО по шаблону с переносами строк:\n[эмодзи флага] [аппетитное название]\n\n⏱ X мин\n🍽 X порций\n🔥 X ккал\n\n🛒 Ингредиенты:\n— ингредиент — точный вес\n\n👩‍🍳 Шаги:\n1. подробный шаг (что делать, время, огонь/температура, признак готовности)\n2. (всего 6-7 шагов)\n\n💡 Секрет: совет хозяйки\n\n📖 А вы знали? 1-2 предложения истории блюда\n\n#хештег #хештег\nУ КАЖДОГО ингредиента точные граммы/миллилитры, включая воду, масло, соль. Пост не длиннее 950 символов ИТОГО.\n"image_prompt" — detailed english description of the finished dish on a beautiful plate with garnish and sauce.'

data = None
for model in candidates:
    print(f"Trying:", model)
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": model, "messages": [{"role": "user", "content": PROMPT}], "temperature": 0.9, "max_tokens": 8000})
    print("Status:", r.status_code)
    if r.status_code != 200:
        print("Response:", r.text[:300])
        continue
    result = r.json()
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "`")
    print("Finish reason:", result.get("choices", [{}])[0].get("finish_reason"))
    print("Content[:300]:", content[:300])
    if <think> in content or Here's a thinking in content:
        print("Thinking model detected, skip")
        continue
    start = content.find("{")
    end = content.rfind("}") + 1
    if start == -1 or end == 0:
        print("No JSON found, skip")
        continue
    try:
        data = json.loads(content[start:end])
        print("Post length:", len(data.get("post", "`")))
        break
    except Exception as e:
        print("JSON parse error:", e)
        continue

if not data:
    print("FAILED: no valid JSON from any model")
else:
    image_url = "https://image.pollinations.ai/prompt/" + requests.utils.quote(data["image_prompt"] + STYLE) + "?model=flux&width=1280&height=800&nologo=true"
    r2 = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data={"chat_id": CHANNEL, "caption": data["post"], "photo": image_url})
    print("Telegram status:", r2.status_code, r2.text[:200])
