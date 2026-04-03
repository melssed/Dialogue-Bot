import asyncio
import os
import aiosqlite
from aiogram import Bot, Dispatcher, types

# --- ПЕРЕМЕННАЯ ОКРУЖЕНИЯ ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6882565528  # твой ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_NAME = "messages.db"

# --- ИНИЦИАЛИЗАЦИЯ БАЗЫ ---
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER,
            chat_id INTEGER,
            user_id INTEGER,
            text TEXT
        )
        """)
        await db.commit()

# --- СОХРАНЕНИЕ СООБЩЕНИЯ ---
async def save_message(message: types.Message):
    text = message.text or message.caption
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT OR IGNORE INTO messages VALUES (?, ?, ?, ?)
        """, (
            message.message_id,
            message.chat.id,
            message.from_user.id if message.from_user else None,
            text
        ))
        await db.commit()

# --- ОБРАБОТКА НОВЫХ СООБЩЕНИЙ ---
@dp.message()
async def handle_message(message: types.Message):
    await save_message(message)

# --- ОБРАБОТКА ИЗМЕНЕННЫХ СООБЩЕНИЙ ---
@dp.edited_message()
async def handle_edited(message: types.Message):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT text FROM messages WHERE message_id=? AND chat_id=?",
            (message.message_id, message.chat.id)
        )
        row = await cur.fetchone()
        new_text = message.text or message.caption
        if row:
            old_text = row[0]
            if old_text != new_text:
                # обновляем базу
                await db.execute(
                    "UPDATE messages SET text=? WHERE message_id=? AND chat_id=?",
                    (new_text, message.message_id, message.chat.id)
                )
                await db.commit()
                # уведомление
                await bot.send_message(
                    ADMIN_ID,
                    f"✏️ Сообщение изменено\n\nOLD:\n{old_text}\nNEW:\n{new_text}"
                )

# --- ПРОВЕРКА УДАЛЕННЫХ СООБЩЕНИЙ В ГРУППАХ ---
async def check_deleted_messages():
    while True:
        await asyncio.sleep(30)  # проверка каждые 30 секунд
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT chat_id, message_id FROM messages") as cursor:
                async for chat_id, message_id in cursor:
                    try:
                        await bot.get_message(chat_id, message_id)
                    except:
                        # сообщение удалено
                        await bot.send_message(
                            ADMIN_ID,
                            f"❌ Сообщение {message_id} удалено из чата {chat_id}"
                        )
                        # удаляем из базы
                        await db.execute(
                            "DELETE FROM messages WHERE chat_id=? AND message_id=?",
                            (chat_id, message_id)
                        )
                        await db.commit()

# --- СТАРТ БОТА ---
async def main():
    await init_db()
    # запускаем проверку удалённых сообщений параллельно
    asyncio.create_task(check_deleted_messages())
    print("Бот работает 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())