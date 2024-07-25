from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import asyncio
import sys
import logging
import random

TOKEN = "YOUR_TOKEN_HERE"

dp = Dispatcher()

admins_id = {
    1147020090
}

requests = {}  # запросы о помощи пользователей, словарь id : message

admin_panel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🆘 Отвечать пользователям")],
    [KeyboardButton(text="📖 Посмотреть статистику")]
], resize_keyboard=True)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if message.from_user.id in admins_id:
        await message.answer("Здравствуйте, администратор! Вот ваша админ панель, приятной работы 😉:", reply_markup=admin_panel)
    else:
        await message.answer(f"Здравствуйте, {message.from_user.full_name}!\n"
                             "В этом канале вы можете связаться с нами и получить ответы на интересующие вас вопросы. "
                             "Для этого просто напишите сообщение ниже, операторы свяжутся как можно скорее!")


@dp.message(lambda message: message.from_user.id in admins_id and message.text == "🆘 Отвечать пользователям")
async def send_reply_help_users(message: Message) -> None:
    if len(requests) == 0:
        await message.answer("Сейчас нет пользователей, которым нужна помощь... Ожидайте уведомлений!")
    else:
        await message.answer("Окей, вот список всех запросов от пользователей: ")
        for uid, reqst in requests.items():  # исправлено на items()
            await bot.send_message(message.from_user.id, f"{uid}: {reqst}")
        await bot.send_message(message.from_user.id, "Чтобы ответить пользователю, напишите следующее: ID: ответ")


@dp.message(lambda message: message.from_user.id in admins_id and 
                        message.text not in ["🆘 Отвечать пользователям", "📖 Посмотреть статистику"])
async def answer_user(message: Message) -> None:
    try:
        text = message.text
        arr = text.split(':')
        uid = int(arr[0].strip())  # Преобразуем в int и убираем лишние пробелы
        reply_text = " ".join(arr[1:]).strip()

        # Это отправляется юзеру!
        await bot.send_message(uid, "Вам ответил администратор!")
        await bot.send_message(uid, reply_text)
        requests.pop(uid, None)  # Убираем запрос из списка
        await message.answer("Спасибо за ответ пользователю. Сообщение отправлено!")
    except (ValueError, IndexError):
        await message.answer("Неправильный формат. Пожалуйста, используйте: ID: ответ")


@dp.message(lambda message: message.from_user.id not in admins_id)
async def echo_handler(message: Message) -> None:
    try:
        text = message.text
        uid = message.from_user.id
        requests[uid] = text
        admins_id_list = list(admins_id)
        admin_id = admins_id_list[random.randint(0, len(admins_id_list) - 1)]
        user = await bot.get_chat(uid)
        await bot.send_message(admin_id, f"⚠️ Пришел новый запрос от пользователя {user.full_name} (@{user.username}): {text}")
        await message.answer("🙏 Спасибо за запрос! Скоро вам ответит администратор.")
    except Exception as e:
        await message.answer(f"Простите, но мы не поддерживаем такой формат сообщений. Попробуйте снова, пожалуйста! Или позвоните по телефону поддержки: {html.bold}+7(800)500-10-20\nОшибка: {e}")


async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
