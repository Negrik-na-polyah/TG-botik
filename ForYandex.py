import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

bot = Bot(token="8587792984:AAG0k70U93Pl-W72pleShz8QMt6T4gnFnPU")
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton("open app", web_app=WebAppInfo(url="https://music.yandex.ru/")))
    await message.answer(f"Hello {message.from_user.first_name}!", reply_markup=markup)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())