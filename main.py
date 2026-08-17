import os
import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = "@vkusno_test_kitchen"
TEXT = "🇨🇳 Китайская кухня | Курица в кисло-сладком соусе\n⏱ 30 мин · 🍽 2 порции\n\n🛒 Ингредиенты:\n— куриное филе 500 г\n— болгарский перец 1 шт\n— ананас 150 г\n\n💡 Секрет хозяйки: обжаривайте филе дважды для хрустящей корочки!\n\n#КитайскаяКухня #Ужин"
IMAGE = "https://image.pollinations.ai/prompt/appetizing%20sweet%20and%20sour%20chicken%20with%20rice%20pineapple%20bell%20pepper%20glossy%20sauce%20food%20photography%20steam?width=1024&height=640&nologo=true"

r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data={"chat_id": CHANNEL, "caption": TEXT, "photo": IMAGE})
print(r.status_code, r.text[:200])
