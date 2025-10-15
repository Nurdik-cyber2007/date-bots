# -*- coding: utf-8 -*-
from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(F.text == "Прочитать соглашение")
async def show_agreement(message: types.Message):
    text = (
        "❤️ *Соглашение*\n\n"
        "я создал этого бота для тебя, это не просто бот, а мини-игра, если ты согласна на эту мини-игру, то прошу к подписи, и спасибо, если читаешь этот текст"

    )

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поставить подпись")],
            [KeyboardButton(text="Что это значит?"), KeyboardButton(text="Передумать")]
        ],
        resize_keyboard=True
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=kb)


@router.message(F.text == "Что это значит?")
async def explain_agreement(message: types.Message):
    await message.answer(
        "Это просто символическое согласие ❤️\n"
        "Я хочу показать тебе, как сильно ценю тебя и хочу помириться.\n"
        "Это не документ верности на всю жизнь, а мини сюрприз, надеюсь ты поймешь"
    )


@router.message(F.text == "Передумать")
async def cancel_agreement(message: types.Message):
    await message.answer(
        "Хорошо\n"
        "Я понимаю, если ты не готова сейчас.\n"
        "Можешь вернуться в любой момент, когда почувствуешь, что хочешь ❤️"
    )


@router.message(F.text == "Поставить подпись")
async def sign_agreement(message: types.Message):
    await message.answer(
        "Для подписи просто отправь цвет сердечка, который тебе нравится)\n"
        "(Например ❤️, 💜, 💙 или 💖)"
    )


@router.message(F.text.in_(["❤️", "💜", "💙", "💖"]))
async def agreement_signed(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Войти в главное меню")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Подпись принята 💞\n"
        "Добро пожаловать в главное меню",
        reply_markup=kb
    )
