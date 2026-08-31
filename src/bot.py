import asyncio
import io
import json
import logging
import os
import time
from pathlib import Path

import httpx
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from dotenv import load_dotenv

load_dotenv("/app/config/.env")
load_dotenv("config/.env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN", "https://osint.qrport.eu")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "5233450569")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
VISITS_FILE = DATA_DIR / "visits.jsonl"
USERS_FILE = DATA_DIR / "users.json"
LOCAL_API = "http://127.0.0.1:8000"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в config/.env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def is_admin(user_id: int) -> bool:
    if not ADMIN_CHAT_ID:
        return False
    return str(user_id) == str(ADMIN_CHAT_ID)


def get_webapp_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚡ Открыть Cyber Hub", web_app=WebAppInfo(url=DOMAIN))]
        ]
    )


@dp.message(CommandStart())
@dp.message(Command("help"))
async def cmd_start(message: types.Message):
    admin_text = ""
    if is_admin(message.from_user.id):
        admin_text = "\n\n👑 <b>Админ:</b> <code>/users</code> | <code>/adduser</code> | <code>/banuser</code> | <code>/visits</code>"
    text = (
        "<b>OSINT CYBER HUB</b>"
        f"{admin_text}"
    )


@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    await message.answer(f"🆔 <b>Ваш Telegram ID:</b> <code>{message.from_user.id}</code>", parse_mode="HTML")


# --- АДМИН-КОМАНДЫ УПРАВЛЕНИЯ ПАНЕЛЬЮ ---

@dp.message(Command("users"))
async def cmd_users(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Только для администратора.")
        return

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{LOCAL_API}/api/admin/users")
            users = resp.json().get("users", [])

        lines = ["👥 <b>Пользователи OSINT Hub:</b>\n"]
        for u in users:
            st = "🟢" if u.get("status") == "active" else "🔴"
            lines.append(f"{st} <b>{u.get('username')}</b> [{u.get('role')}] | Поисков: {u.get('total_scans')}")

        await message.answer("\n".join(lines), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.message(Command("adduser"))
async def cmd_adduser(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Только для администратора.")
        return

    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("⚠️ Формат: <code>/adduser login password [role]</code>", parse_mode="HTML")
        return

    username = parts[1]
    password = parts[2]
    role = parts[3] if len(parts) > 3 else "user"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{LOCAL_API}/api/admin/users/create",
                json={"username": username, "password": password, "role": role}
            )
            data = resp.json()

        if data.get("ok"):
            await message.answer(f"✅ Пользователь <code>{username}</code> успешно создан.", parse_mode="HTML")
        else:
            await message.answer(f"❌ {data.get('error')}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.message(Command("banuser"))
async def cmd_banuser(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Только для администратора.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ Формат: <code>/banuser login</code>", parse_mode="HTML")
        return

    username = parts[1]
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{LOCAL_API}/api/admin/users/toggle_status",
                json={"username": username}
            )
            data = resp.json()

        if data.get("ok"):
            await message.answer(f"🔄 Статус пользователя <code>{username}</code>: <b>{data.get('new_status')}</b>", parse_mode="HTML")
        else:
            await message.answer(f"❌ {data.get('error')}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.message(Command("visits"))
async def cmd_visits(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Только для администратора.")
        return

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{LOCAL_API}/api/admin/visitors?limit=10")
            visitors = resp.json().get("visitors", [])

        if not visitors:
            await message.answer("📊 Журнал визитов пуст.")
            return

        lines = ["🌐 <b>Последние 10 визитов:</b>\n"]
        for v in visitors:
            ts = v.get("ts", "")[:19].replace("T", " ")
            lines.append(f"• <code>{ts}</code> | <b>{v.get('ip')}</b> | {v.get('country')} ({v.get('city')})")

        await message.answer("\n".join(lines), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.message()
async def fallback_any_message(message: types.Message):
    await message.answer("<b>OSINT CYBER HUB</b>", reply_markup=get_webapp_keyboard(), parse_mode="HTML")


async def main():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Telegram Bot запущен в режиме WebApp Launcher...")
    await dp.start_polling(bot)


    asyncio.run(main())
