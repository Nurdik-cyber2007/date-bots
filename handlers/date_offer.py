# -*- coding: utf-8 -*-
from aiogram import Router, types, F, Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
import datetime
import random
import os

router = Router()

# 👉 Telegram ID администратора (твой)
ADMIN_ID = 1030165506

# 🧠 Переменные
last_user_id = None
chat_mode = {}          # состояние секретного чата
pending_choice = {}     # временный выбор для подтверждения

# 📸 Данные по вариантам свиданий
# ВАЖНО: ключи без лишних пробелов — это убирает многие баги
DATE_OPTIONS = {
    "🌇 Вечерний кинорум": {
        "photo": "photos/gentlemen.png",
        "reply": [
            "Оу, кинорум? Тогда я бронирую, только скажи в какое время тебе удобно?\n",
            "Смешная комедия, плед и мы - идеальное сочетание для нас)",
        ]
    },
    "☕ Прогулка у Хан-Шатыра, с кофейком": {
        "photo": "photos/coffee.png",
        "reply": [
            "Кофе у Хан-Шатыра? Почему бы и нет? Главное - ты рядом)\n",
            "Горячий кофе и свежий воздух - приятный вечер для нас обоих <3",
        ]
    },
    "🍽 Антикафе": {
        "photo": "photos/akitime.png",
        "reply": [
            "Антикафе — PlayStation, Nintendo, Sega настолки и уют. Предлагаю AkiTime.\n",
            "Будет весело, жаным я обещаю)",
        ]
    },
    "🏎 Врум-симуляторы": {
        "photo": "photos/racing.png",
        "reply": [
            "Автосимулятор - Симулятор бибики\n",
            "Постарайся меня не сбивать просто так :)",
        ]
    },
    "👻 Хоррор-квест для двоих": {
        "photo": "photos/teorema.png",
        "reply": [
            "Будем убегать - зато вместе.\n",
            "Если испугаешься - Не переживай я рядом.",
        ]
    },
    "🏁 Картинг": {
        "photo": "photos/carting.png",
        "reply": [
            "Картинг? будем сбивать друг-друга? почему бы и нет)\n",
            "Визавишь такси?)",
        ]
    },
    "💻 Компьютерный клуб": {
        "photo": "photos/pc.png",
        "reply": [
            "Комп-клуб - Либо выигрываем, либо сосем\n",
            "Главное - чтобы было весело.",
        ]
    },
    "🎬 Кинотеатр": {
        "photo": "photos/cino.png",
        "reply": [
            "Классика из классик, посмотрим казахский фильм который я не понимаю, и покушаем попкорн)\n",
            "Если будет скучно - просто болтаем.",
        ]
    }
}

# Вспомог: список чистых ключей (используется для фильтров и клавиатуры)
DATE_KEYS = list(DATE_OPTIONS.keys())

# Вспомог: функция для построения клавиатуры из DATE_KEYS
def make_dates_kb():
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=option)] for option in DATE_KEYS] + [[KeyboardButton(text="Назад в меню")]],
        resize_keyboard=True
    )
    return kb

# -------------------------------
# 🔹 Главное меню
# -------------------------------
@router.message(F.text.in_(["Войти в главное меню", "/start", "Назад в меню"]))
async def open_main_menu(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мое искреннее извинение")],
            [KeyboardButton(text="Предложить свидание")],
            [KeyboardButton(text="Секретный чат")],
            [KeyboardButton(text="Выйти (если не готова)")]
        ],
        resize_keyboard=True
    )
    print("[LOG] open_main_menu called")
    await message.answer("Главное меню\n\nВыбери, что хочешь сделать:", reply_markup=kb)


# -------------------------------
# 🔹 Искреннее извинение
# -------------------------------
@router.message(F.text == "Мое искреннее извинение")
async def my_apology(message: types.Message):
    print("[LOG] my_apology called")
    await message.answer(
        "Я бы хотел извинится за то, что причинил тебе вред, я люблю тебя, и понимаю что я натворил в последней нашем общении, и хочу исправится..\n"
        "Я сожалею, и хочу начать всё снова поэтому создал этого бота, если ты хочешь этого, и готова, то выбери, куда мы пойдем, только я и ты <3"
    )


# -------------------------------
# 🔹 Предложить свидание
# -------------------------------
@router.message(F.text == "Предложить свидание")
async def offer_date_options(message: types.Message):
    print("[LOG] offer_date_options called")
    kb = make_dates_kb()
    await message.answer("У меня есть несколько идей для нас, выбери что тебе по душе:", reply_markup=kb)


# -------------------------------
# 🔹 Обработка выбора (показывает фото и описание)
# -------------------------------
@router.message(F.text.in_(DATE_KEYS))
async def handle_date_choice(message: types.Message):
    # Нормализуем текст (убираем лишние пробелы)
    choice = message.text.strip()
    print(f"[LOG] handle_date_choice called: raw='{message.text}' stripped='{choice}'")

    # Сохраняем временно выбор
    pending_choice[message.from_user.id] = choice

    # Берём данные; если ключи в DATE_OPTIONS совпадают с stripped, то OK
    data = DATE_OPTIONS.get(choice)
    if not data:
        # Если вдруг ключи отличаются по пробелам — пытаемся найти похожий
        # пробуем найти соответствие по конкатенации без пробелов (на случай)
        for k in DATE_OPTIONS.keys():
            if k.replace(" ", "").lower() == choice.replace(" ", "").lower():
                data = DATE_OPTIONS[k]
                choice = k
                pending_choice[message.from_user.id] = choice
                break

    if not data:
        print("[ERROR] Не найдено описание для выбора:", message.text)
        await message.answer("Ошибка: описание для этого варианта не найдено")
        return

    # подготовка текста и фото
    reply_text = "".join(data["reply"])
    photo_path = data["photo"]

    # лог: покажем абсолютный путь к фото — для отладки
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), photo_path))
    print(f"[LOG] photo_path = {photo_path} abs_path = {abs_path} exists = {os.path.exists(abs_path)}")

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да, уверена")],
            [KeyboardButton(text="Хочу выбрать другое")]
        ],
        resize_keyboard=True
    )

    # пробуем отправить файл из относительного пути относительно handlers/
    try:
        # путь относительно файла: os.path.join(os.path.dirname(__file__), photo_path)
        await message.answer_photo(
            photo=FSInputFile(os.path.join(os.path.dirname(__file__), photo_path)),
            caption=f"{reply_text}\n\nТы выбрала: {choice}\nТы уверена?",
            reply_markup=kb
        )
        print("[LOG] Фото отправлено успешно")
    except Exception as e:
        print(f"[ERROR] Не удалось отправить фото {photo_path}: {e}")
        # fallback: просто текст с тем же kb
        await message.answer(f"{reply_text}\n\nТы выбрала: {choice}\nТы уверена?", reply_markup=kb)


# -------------------------------
# 🔹 Подтверждение выбора свидания (устойчиво, без повторов)
# -------------------------------
from aiogram import types, F
import asyncio

already_confirmed = set()  # чтобы не допускать повторов

@router.message(F.text == "Да, уверена")
async def confirm_date_choice(message: types.Message):
    user_id = message.from_user.id
    choice = pending_choice.get(user_id)

    print(f"[LOG] confirm_date_choice called for user {user_id}, choice={choice}")

    # 🔒 Если уже нажимала — просто вернуть сообщение без перезапуска сценария
    if user_id in already_confirmed:
        await message.answer("Ты уже всё подтвердила 💛, я помню твой выбор 🌸")
        return
    already_confirmed.add(user_id)

    if not choice:
        await message.answer("Ты уже всё подтвердила 💛")
        return

    # 📩 Уведомление админу
    try:
        await message.bot.send_message(
            ADMIN_ID,
            f"📩 Она выбрала: {choice}\nПользователь: {message.from_user.full_name} (@{message.from_user.username})"
        )
    except Exception as e:
        print("[ERROR] Не удалось отправить уведомление админу:", e)

    from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

    # 💭 Анимация шагов
    msg = await message.answer("Секундочку... 💭", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(1.3)
    await msg.delete()

    msg = await message.answer("Проверяю время и брони... ⏳")
    await asyncio.sleep(1.5)
    await msg.delete()

    msg = await message.answer(f"Отлично, я всё запомнил для {choice} 💛")
    await asyncio.sleep(1.5)
    await msg.delete()

    await message.answer(
        f"Отлично, я всё запомнил для {choice} 💛\n\n"
        "Теперь скажи, во сколько тебе удобно начать?\n\n"
        "💌 Мне уже не терпится провести это время вместе."
    )

    # 🧹 Очистка выбора
    pending_choice.pop(user_id, None)

    # ⏳ Через 5 секунд — кнопки (только один раз)
    await asyncio.sleep(5)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отменить выбор / передумала")],
            [KeyboardButton(text="Назад в меню")]
        ],
        resize_keyboard=True
    )

    await message.answer("Если вдруг передумала — просто нажми ниже:", reply_markup=kb)

    # 🧽 Через 1 минуту можно снова активировать подтверждение (на случай новых выборов)
    async def reset_flag():
        await asyncio.sleep(60)
        already_confirmed.discard(user_id)

    asyncio.create_task(reset_flag())

    # -------------------------------
# 🔹 Обработка сообщения с временем свидания
# -------------------------------
from aiogram import types, F
import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

@router.message(
    F.text.not_in([
        "❌ Отменить выбор / передумала",
        "Хочу выбрать другое",
        "Назад в меню",
        "Мое искреннее извинение",
        "Предложить свидание",
        "Секретный чат",
        "🚪 Выйти из переписки",
        "Выйти (если не готова)",
        "Войти в главное меню",
        "/start"
    ]) & F.text.regexp(r"\d")  # только если сообщение содержит цифры (например, "19:00")
)
async def handle_time_response(message: types.Message):

    user_id = message.from_user.id

    # Проверяем, есть ли у пользователя активное подтверждение
    if user_id in already_confirmed:
        # 💬 Первое сообщение
        await asyncio.sleep(1.2)
        await message.answer("Твоя бронь принята, жаным 💛")
        await asyncio.sleep(1.8)

        # 💬 Второе сообщение
        await message.answer("Выбор места и твоего времени отправляется админу... 🕊")
        await asyncio.sleep(1.8)

        # 📩 Отправляем админу данные
        try:
            await message.bot.send_message(
                ADMIN_ID,
                f"🕓 {message.from_user.full_name} (@{message.from_user.username}) "
                f"подтвердила время: {message.text}"
            )
        except Exception as e:
            print("[ERROR] Не удалось отправить админу данные:", e)

        # 💬 Третье сообщение
        await asyncio.sleep(1.5)
        await message.answer("Возвращение в главное меню 🔙")

        # 🧭 Главное меню
        kb_main = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Мое искреннее извинение")],
                [KeyboardButton(text="Предложить свидание")],
                [KeyboardButton(text="Секретный чат")],
                [KeyboardButton(text="Выйти (если не готова)")]
            ],
            resize_keyboard=True
        )

        await asyncio.sleep(1.5)
        await message.answer("Ты снова в главном меню, жаным 💖", reply_markup=kb_main)

        # ✅ Сбрасываем подтверждение, чтобы можно было начать заново
        already_confirmed.discard(user_id)
    else:
        # Если пользователь пишет что-то просто так — ничего не делаем
        return



# -------------------------------
# 🔹 Отмена выбора после подтверждения
# -------------------------------
@router.message(F.text == "❌ Отменить выбор / передумала")
async def cancel_date_choice(message: types.Message):
    kb = make_dates_kb()
    await message.answer(
        "Хорошо 😊 Всё отменяю. Выбери другой вариант, я ничего не сохраняю.",
        reply_markup=kb
    )



# -------------------------------
# 🔹 Отмена и выбор другого варианта
# -------------------------------
@router.message(F.text == "Хочу выбрать другое")
async def choose_another_date(message: types.Message):
    print("[LOG] choose_another_date called")
    kb = make_dates_kb()
    await message.answer("Хорошо, выбери другой вариант:", reply_markup=kb)


# -------------------------------
# 🔹 Секретный чат
# -------------------------------
@router.message(F.text == "Секретный чат")
async def secret_chat_start(message: types.Message):
    global last_user_id, chat_mode
    last_user_id = message.from_user.id
    chat_mode[message.from_user.id] = True
    print(f"[LOG] secret_chat_start user={last_user_id}")

    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🚪 Выйти из переписки")]], resize_keyboard=True)
    await message.answer("Секретный чат активирован. Чтобы закончить — нажми «🚪 Выйти из переписки».", reply_markup=kb)

    if message.from_user.id != ADMIN_ID:
        await message.bot.send_message(ADMIN_ID, "🔒 Она вошла в секретный чат.")


# -------------------------------
# 🔹 Выход из переписки
# -------------------------------
@router.message(F.text == "🚪 Выйти из переписки")
async def exit_conversation(message: types.Message, bot: Bot):
    global chat_mode
    user_id = message.from_user.id

    if user_id == ADMIN_ID:
        if last_user_id:
            await bot.send_message(last_user_id, "Он вышел из переписки.")
    else:
        await bot.send_message(ADMIN_ID, "Она вышла из переписки.")

    chat_mode[user_id] = False
    await open_main_menu(message)


# -------------------------------
# 🔹 Выйти (если не готова)
# -------------------------------
@router.message(F.text == "Выйти (если не готова)")
async def cancel_conversation(message: types.Message, bot: Bot):
    await message.answer("Удаляю всё, чтобы начать с чистого листа...\nЕсли хочешь — напиши /start")
    chat_id = message.chat.id
    for msg_id in range(message.message_id, message.message_id - 100, -1):
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception:
            pass
    global chat_mode, last_user_id
    chat_mode.pop(message.from_user.id, None)
    if message.from_user.id == last_user_id:
        last_user_id = None


# -------------------------------
# 🔹 Сообщения от пользователей — ставим фильтр и оставляем в самом конце файла!
# -------------------------------
@router.message(F.text.not_in(DATE_KEYS + [
    "Предложить свидание", "Мое искреннее извинение",
    "Секретный чат", "🚪 Выйти из переписки",
    "Назад в меню", "Да, уверена", "Хочу выбрать другое",
    "Выйти (если не готова)"
]))
async def forward_from_user(message: types.Message, bot: Bot):
    global last_user_id, chat_mode
    print(f"[LOG] forward_from_user called text='{message.text}' from={message.from_user.id}")
    if message.from_user.id != ADMIN_ID:
        last_user_id = message.from_user.id
        if chat_mode.get(message.from_user.id):
            await forward_any_message(message, bot, ADMIN_ID)
        else:
            if message.text:
                await bot.send_message(ADMIN_ID, f"💬 Сообщение от {message.from_user.full_name} (@{message.from_user.username}):\n\n{message.text}")
    else:
        if last_user_id and chat_mode.get(last_user_id):
            await forward_any_message(message, bot, last_user_id)


# -------------------------------
# 🔹 Универсальная пересылка (в самом конце)
# -------------------------------
async def forward_any_message(message: types.Message, bot: Bot, receiver_id: int):
    if message.text:
        await bot.send_message(receiver_id, message.text)
    elif message.photo:
        await bot.send_photo(receiver_id, message.photo[-1].file_id, caption=message.caption or "")
    elif message.voice:
        await bot.send_voice(receiver_id, message.voice.file_id, caption=message.caption or "")
    elif message.sticker:
        await bot.send_sticker(receiver_id, message.sticker.file_id)
    elif message.video:
        await bot.send_video(receiver_id, message.video.file_id, caption=message.caption or "")
    elif message.document:
        await bot.send_document(receiver_id, message.document.file_id, caption=message.caption or "")
