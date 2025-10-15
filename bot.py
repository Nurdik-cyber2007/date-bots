# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher
import asyncio
from config import BOT_TOKEN
from handlers import start, agreement, date_offer
from aiohttp import web

# Запускаем Telegram бота
async def run_bot():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(agreement.router)
    dp.include_router(date_offer.router)
    print("Бот запущен...")
    await dp.start_polling(bot)

# Простейший веб-сервер для Render и UptimeRobot
async def handle(request):
    return web.Response(text="Bot is alive!")

async def run_web():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)  # Render слушает 0.0.0.0 и порт 10000
    await site.start()
    print("Web server started on port 10000")

# Основная точка входа
async def main():
    await asyncio.gather(run_bot(), run_web())

if __name__ == "__main__":
    asyncio.run(main())
