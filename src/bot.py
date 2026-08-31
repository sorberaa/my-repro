import asyncio
import json
import logging
import os
import re
from pathlib import Path

import httpx
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from dotenv import load_dotenv

load_dotenv("/app/config/.env")
load_dotenv("config/.env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN", "https://osint.qrport.eu")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "5233450569")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6IJRS1lLX1i1egBpyEfQGfLHXoI4GfgFO2Yp5pg-LFLtQ")

DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
VISITS_FILE = DATA_DIR / "visits.jsonl"
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
            [InlineKeyboardButton(text="🚀 Открыть OSINT Pro Hub", web_app=WebAppInfo(url=DOMAIN))],
            [
                InlineKeyboardButton(text="✈️ Telegram Скан", callback_data="btn_tg"),
                InlineKeyboardButton(text="💜 AI Досье", callback_data="btn_ai")
            ]
        ]
    )


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    admin_text = "\n\n👑 <b>Админ-функции:</b>\n/visits — просмотр логов и IP посетителей панели" if is_admin(message.from_user.id) else ""
    
    text = (
        "🕵️ <b>Добро пожаловать в OSINT & Recon Pro Hub!</b>\n\n"
        "Платформа для сбора данных по открытым источникам, разведки в Telegram, дедукции личности (AI Gemini) и анализа цифрового следа.\n\n"
        "⚡ <b>Быстрые команды бота:</b>\n"
        "├ <code>/scan &lt;username&gt;</code> — Кросс-поиск профилей (Steam, GitHub, Twitch...)\n"
        "├ <code>/tg &lt;@user/ID&gt;</code> — Разведка Telegram (Bio, статус, дата по ID)\n"
        "├ <code>/ai &lt;target&gt;</code> — Глубокий AI-портрет личности (Gemini)\n"
        "├ <code>/ip &lt;8.8.8.8&gt;</code> — Геолокация и провайдер по IP\n"
        "├ <code>/domain &lt;site.com&gt;</code> — DNS, SSL и безопасность домена\n"
        "└ <code>/id</code> — Узнать свой Telegram ID"
        f"{admin_text}\n\n"
        "👇 <i>Нажмите кнопку ниже, чтобы открыть полную интерактивную WebApp-панель:</i>"
    )
    await message.answer(text, reply_markup=get_webapp_keyboard(), parse_mode="HTML")


@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    await message.answer(f"🆔 <b>Ваш Telegram ID:</b> <code>{message.from_user.id}</code>", parse_mode="HTML")


@dp.message(Command("scan"))
async def cmd_scan(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Укажите цель для сканирования: <code>/scan wertag20</code>", parse_mode="HTML")
        return

    target = args[1].strip().lstrip("@")
    status_msg = await message.answer(f"⏳ <i>Выполняется кросс-поиск открытых аккаунтов для <b>{target}</b>...</i>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{LOCAL_API}/api/scan/username", json={"target": target})
            data = resp.json()

        profiles = data.get("profiles", [])
        found_count = data.get("found_count", 0)
        total = data.get("total_checked", 0)
        ai_summary = data.get("ai_summary", "")

        res_lines = [f"🎯 <b>Результаты сканирования:</b> <code>{target}</code>"]
        res_lines.append(f"✅ Найдено активных аккаунтов: <b>{found_count}</b> из {total}\n")

        for p in profiles:
            res_lines.append(f"• <b>{p['platform']}</b>: <a href='{p['url']}'>Открыть профиль</a>")

        if ai_summary:
            res_lines.append(f"\n🧠 <b>Аналитическое резюме (AI):</b>\n{ai_summary}")

        await status_msg.edit_text(
            "\n".join(res_lines),
            reply_markup=get_webapp_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка выполнения сканирования: {str(e)}")


@dp.message(Command("tg"))
async def cmd_tg(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Укажите юзернейм или ID: <code>/tg @durov</code> или <code>/tg 5233450569</code>", parse_mode="HTML")
        return

    target = args[1].strip()
    status_msg = await message.answer(f"✈️ <i>Опрос метаданных Telegram для <b>{target}</b>...</i>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{LOCAL_API}/api/scan/telegram", json={"target": target})
            data = resp.json()

        if data.get("type") == "telegram_id":
            text = (
                f"✈️ <b>Telegram ID Inspector:</b>\n\n"
                f"🆔 <b>ID:</b> <code>{data.get('tg_id')}</code>\n"
                f"📅 <b>Оценка периода регистрации:</b> {data.get('estimated_year')}\n\n"
                f"💡 <i>{data.get('ai_summary', '')}</i>"
            )
        else:
            text = (
                f"✈️ <b>Telegram Profile Inspector:</b>\n\n"
                f"👤 <b>Имя / Title:</b> {data.get('title')}\n"
                f"🏷 <b>Тип:</b> {data.get('account_type')}\n"
                f"🔗 <b>Юзернейм:</b> @{data.get('username')}\n"
                f"📝 <b>Bio / Описание:</b> {data.get('description')}\n\n"
                f"🧠 <b>Аналитика (AI):</b>\n{data.get('ai_summary', '')}"
            )

        await status_msg.edit_text(text, reply_markup=get_webapp_keyboard(), parse_mode="HTML")
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка запроса к Telegram: {str(e)}")


@dp.message(Command("ai"))
async def cmd_ai(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Укажите цель для составления AI-досье: <code>/ai wertag20</code>", parse_mode="HTML")
        return

    target = args[1].strip()
    status_msg = await message.answer(f"🧠 <i>Нейросеть Gemini сопоставляет цифровые следы для <b>{target}</b>...</i>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{LOCAL_API}/api/ai/deduce", json={"target": target, "tool": "Telegram Bot AI"})
            data = resp.json()

        dossier = data.get("dossier", "Досье сформировано.")
        await status_msg.edit_text(
            f"💜 <b>Аналитическое досье (Gemini AI):</b>\n🎯 Цель: <code>{target}</code>\n\n{dossier}",
            reply_markup=get_webapp_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка генерации досье: {str(e)}")


@dp.message(Command("ip"))
async def cmd_ip(message: types.Message):
    args = message.text.split(maxsplit=1)
    target = args[1].strip() if len(args) > 1 else "8.8.8.8"
    status_msg = await message.answer(f"🌍 <i>Запрос GeoIP для {target}...</i>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(f"{LOCAL_API}/api/scan/ip", json={"target": target})
            data = resp.json().get("data", {})

        text = (
            f"🌍 <b>GeoIP Информация:</b> <code>{target}</code>\n\n"
            f"🏳️ <b>Страна / Город:</b> {data.get('country', '—')}, {data.get('city', '—')}\n"
            f"🏢 <b>Провайдер (ISP):</b> {data.get('isp', '—')}\n"
            f"🏷 <b>Организация:</b> {data.get('org', '—')}\n"
            f"🔢 <b>AS Номер:</b> {data.get('as', '—')}\n"
            f"🕒 <b>Часовой пояс:</b> {data.get('timezone', '—')}"
        )
        await status_msg.edit_text(text, reply_markup=get_webapp_keyboard(), parse_mode="HTML")
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка GeoIP: {str(e)}")


@dp.message(Command("visits"))
async def cmd_visits(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Команда доступна только администратору.")
        return

    if not VISITS_FILE.exists():
        await message.answer("📊 Журнал визитов пока пуст.")
        return

    lines = VISITS_FILE.read_text(encoding="utf-8").splitlines()[-20:]
    lines.reverse()

    rows = []
    for line in lines:
        try:
            r = json.loads(line)
            rows.append(f"🕒 <code>{r.get('ts', '—')}</code> | <b>{r.get('ip', 'unknown')}</b> ({r.get('country', 'RU')})\n📱 {r.get('ua', '')[:40]}…")
        except Exception:
            continue

    text = "🕵️ <b>Последние посещения WebApp панели:</b>\n\n" + "\n\n".join(rows[:10])
    await message.answer(text, parse_mode="HTML")


@dp.callback_query(F.data == "btn_tg")
async def cb_tg(call: types.CallbackQuery):
    await call.message.answer("✈️ Для проверки Telegram профиля отправьте команду:\n<code>/tg @username</code> или <code>/tg 5233450569</code>", parse_mode="HTML")
    await call.answer()


@dp.callback_query(F.data == "btn_ai")
async def cb_ai(call: types.CallbackQuery):
    await call.message.answer("💜 Для составления AI-досье личности отправьте:\n<code>/ai wertag20</code>", parse_mode="HTML")
    await call.answer()


# Авто-обработка обычных текстовых сообщений
@dp.message(F.text)
async def auto_text_handler(message: types.Message):
    txt = message.text.strip()
    if txt.startswith("/"):
        return

    if txt.startswith("@") or txt.isdigit():
        await cmd_tg(message)
    else:
        # Авто-запуск сканирования никнейма
        await cmd_scan(message)


async def main():
    logging.info("Starting Telegram Bot Polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
