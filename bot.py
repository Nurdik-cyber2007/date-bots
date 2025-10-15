# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from config import BOT_TOKEN

# Импортируем обработчики
from handlers import start, agreement, date_offer

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем все обработчики
    dp.include_router(start.router)
    dp.include_router(agreement.router)
    dp.include_router(date_offer.router) 

    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
