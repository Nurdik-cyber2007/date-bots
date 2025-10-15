import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("Error: BOT_TOKEN не задано в переменных окружения")
