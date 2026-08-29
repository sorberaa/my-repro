import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import WebAppInfo
from dotenv import load_dotenv

load_dotenv("/app/config/.env")
load_dotenv("config/.env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN", "https://osint.qrport.eu")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")

DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
VISITS_FILE = DATA_DIR / "visits.jsonl"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в config/.env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def is_admin(message: types.Message) -> bool:
    if not ADMIN_CHAT_ID:
        return False
    return str(message.from_user.id) == str(ADMIN_CHAT_ID)


@dp.message(CommandStart())
async def start(message: types.Message):
    web_app = WebAppInfo(url=DOMAIN)
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Открыть OSINT Lab", web_app=web_app)]
        ]
    )
    extra = ""
    if is_admin(message):
        extra = "\nАдмин: /visits — последние IP визитов в панель."
    await message.answer(
        "Образовательный каталог OSINT-модулей." + extra,
        reply_markup=markup,
    )


@dp.message(Command("id"))
async def my_id(message: types.Message):
    await message.answer(f"Твой Telegram id: {message.from_user.id}")


@dp.message(Command("visits"))
async def visits(message: types.Message):
    if not is_admin(message):
        await message.answer("Команда только для ADMIN_CHAT_ID.")
        return
    if not VISITS_FILE.exists():
        await message.answer("Визитов пока нет.")
        return
    lines = VISITS_FILE.read_text(encoding="utf-8").splitlines()[-15:]
    lines.reverse()
    text = "Последние визиты в панель:\n\n" + "\n".join(lines[:15])
    if len(text) > 3500:
        text = text[:3500] + "…"
    await message.answer(text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
