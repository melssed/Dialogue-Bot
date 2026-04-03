import asyncio
import os
import aiosqlite
from aiogram import Bot, Dispatcher, types

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_NAME = "messages.db"

# --- БАЗА ---
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

# --- СОХРАНЕНИЕ ---
async def save_message(message: types.Message):
    text = message.text or message.caption

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO messages VALUES (?, ?, ?, ?)
        """, (
            message.message_id,
            message.chat.id,
            message.from_user.id if message.from_user else None,
            text
        ))
        await db.commit()

# --- ВСЕ СООБЩЕНИЯ ---
@dp.message()
async def handle(message: types.Message):
    await save_message(message)

# --- ОТСЛЕЖИВАНИЕ ИЗМЕНЕНИЙ ---
@dp.edited_message()
async def edited(message: types.Message):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("""
        SELECT text FROM messages
        WHERE message_id=? AND chat_id=?
        """, (message.message_id, message.chat.id))
        
        row = await cur.fetchone()

        if row:
            old_text = row[0]
            new_text = message.text or message.caption

            # обновляем базу
            await db.execute("""
            UPDATE messages SET text=?
            WHERE message_id=? AND chat_id=?
            """, (new_text, message.message_id, message.chat.id))
            await db.commit()

            # 🔥 УВЕДОМЛЕНИЕ
            await message.answer(
                f"✏️ Сообщение изменено\n\n"
                f"OLD:\n{old_text}\n\n"
                f"NEW:\n{new_text}"
            )

# --- СТАРТ ---
async def main():
    await init_db()
    print("Бот работает 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
