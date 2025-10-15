from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Прочитать соглашение")],
            [KeyboardButton(text="Выйти (если не готова)")],
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Привет, моя жаным❤️\n\n"
        "Ты готова прочитать соглашение и начать игру?",
        reply_markup=kb
    )