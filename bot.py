import asyncio
from aiogram import Bot, Dispatcher, types
import os

TOKEN = os.getenv("BOT_TOKEN")   # Токен твоего бота
FORWARD_TO = 6882565528         # Кому пересылать
WATCH_USER = 6234173903         # Кого отслеживаем

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def forward_messages(message: types.Message):
    if message.from_user and message.from_user.id == WATCH_USER:
        await message.forward(FORWARD_TO)

async def main():
    print("Бот работает 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
