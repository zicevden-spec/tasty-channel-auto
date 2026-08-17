import os
import json
import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GROQ = os.environ["GROQ_API_KEY"]
CHANNEL = "@vkusno_test_kitchen"

PROMPT = 'Придумай блюдо русской или китайской кухни. Верни СТРОГО валидный JSON без лишнего текста: {"post": "пост для телеграм: название с эмодзи, время и порции, ингредиенты списком, 5 коротких шагов приготовления, секрет хозяйки, 2 хештега", "image_prompt": "short english food photo description with lighting and style"}'

try:
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {GROQ}", "Content-Type": "application/json"}, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": PROMPT}], "temperature": 0.9})
    print("Groq status:", r.status_code)
    content = r.json()["choices"][0]["message"]["content"]
    print("Groq said:", content[:200])
    start = content.find("{")
    end = content.rfind("}") + 1
    data = json.loads(content[start:end])
    
    image_url = "https://image.pollinations.ai/prompt/" + requests.utils.quote(data["image_prompt"]) + "?width=1024&height=640&nologo=true"
    r2 = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data={"chat_id": CHANNEL, "caption": data["post"], "photo": image_url})
    print("Telegram status:", r2.status_code, r2.text[:200])
except Exception as e:
    print("ERROR:", e)
    print("Response:", r.text if 'r' in locals() else 'no response')
