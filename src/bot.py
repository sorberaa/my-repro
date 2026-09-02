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
    LabeledPrice,
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

STAR_PACKAGES = {
    "pkg_20": {"title": "⭐️ 20 OSINT Запросов", "description": "Пополнение баланса поиска на 20 проверок", "scans": 20, "stars": 35},
    "pkg_50": {"title": "⭐️ 50 OSINT Запросов", "description": "Пополнение баланса поиска на 50 проверок", "scans": 50, "stars": 88},
    "pkg_100": {"title": "⭐️ 100 OSINT Запросов", "description": "Пополнение баланса поиска на 100 проверок", "scans": 100, "stars": 235},
}

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
            [InlineKeyboardButton(text="⚡ Открыть OSINT Панель", web_app=WebAppInfo(url=DOMAIN))],
            [InlineKeyboardButton(text="⭐️ Купить запросы (Stars)", callback_data="open_buy_menu")]
        ]
    )


@dp.message(CommandStart())
@dp.message(Command("help"))
async def cmd_start(message: types.Message):
    admin_text = ""
    if is_admin(message.from_user.id):
        admin_text = "\n\n👑 <b>Админ:</b> <code>/users</code> | <code>/setscans</code> | <code>/grantvip</code> | <code>/adduser</code> | <code>/banuser</code> | <code>/visits</code>"
    text = (
        "🏝️ <b>peace of the island of sor/ber peoples</b>\n"
        "🌐 <i>Платформа OSINT-разведки и поиска цифрового следа.</i>\n\n"
        "🎁 <b>Вам начислено 5 бесплатных поисковых запросов!</b>\n\n"
        "🔍 <b>Возможности:</b>\n"
        "• <b>Sherlock:</b> Поиск никнейма по 480+ открытым сервисам\n"
        "• <b>Instagram & Social:</b> Instaloader, Osintgram, Toutatis, VK, TikTok\n"
        "• <b>Crypto Forensics:</b> Анализ криптокошельков (BTC, ETH, TRX, USDT)\n"
        "• <b>OSINT Dorking:</b> Генератор 25+ дорков (утечки, документы, БД)\n"
        "• <b>GitHub Recon:</b> Поиск скрытых email в истории коммитов\n"
        "• <b>Phone:</b> Определение оператора связи, региона и мессенджеров\n"
        "• <b>Вирты:</b> Атрибуция основы и скрытых связей профилей\n\n"
        "⭐️ <b>Подписки:</b> /buy — пополнение запросов через Telegram Stars\n"
        "👇 <i>Нажмите кнопку ниже для запуска веб-панели:</i>"
        f"{admin_text}"
    )
    await message.answer(text, reply_markup=get_webapp_keyboard(), parse_mode="HTML")


@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    await message.answer(f"🆔 <b>Ваш Telegram ID:</b> <code>{message.from_user.id}</code>", parse_mode="HTML")


@dp.message(Command("buy"))
@dp.message(Command("stars"))
async def cmd_buy_stars(message: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌟 20 запросов — 35 ⭐️", callback_data="buy_pkg_20")],
            [InlineKeyboardButton(text="🌟 50 запросов — 88 ⭐️", callback_data="buy_pkg_50")],
            [InlineKeyboardButton(text="🌟 100 запросов — 235 ⭐️", callback_data="buy_pkg_100")],
            [InlineKeyboardButton(text="⚡ Открыть OSINT Панель", web_app=WebAppInfo(url=DOMAIN))]
        ]
    )
    text = (
        "⭐️ <b>Пополнение баланса запросов (Telegram Stars)</b>\n\n"
        "Каждому новому агенту предоставляется <b>5 бесплатных запросов</b>.\n"
        "Для продолжения расследований выберите подходящий пакет:\n\n"
        "• <b>20 запросов</b> — <code>35 Stars</code>\n"
        "• <b>50 запросов</b> — <code>88 Stars</code>\n"
        "• <b>100 запросов</b> — <code>235 Stars</code>\n\n"
        "<i>Оплата происходит мгновенно в один клик через официальные Telegram Stars.</i>"
    )
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@dp.callback_query(F.data == "open_buy_menu")
async def callback_open_buy_menu(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌟 20 запросов — 35 ⭐️", callback_data="buy_pkg_20")],
            [InlineKeyboardButton(text="🌟 50 запросов — 88 ⭐️", callback_data="buy_pkg_50")],
            [InlineKeyboardButton(text="🌟 100 запросов — 235 ⭐️", callback_data="buy_pkg_100")],
            [InlineKeyboardButton(text="⚡ Открыть OSINT Панель", web_app=WebAppInfo(url=DOMAIN))]
        ]
    )
    text = (
        "⭐️ <b>Пополнение баланса запросов (Telegram Stars)</b>\n\n"
        "• <b>20 запросов</b> — <code>35 Stars</code>\n"
        "• <b>50 запросов</b> — <code>88 Stars</code>\n"
        "• <b>100 запросов</b> — <code>235 Stars</code>\n\n"
        "<i>Нажмите на нужный тариф для моментального выставления счета в Stars:</i>"
    )
    await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data.startswith("buy_pkg_"))
async def callback_buy_package(callback: types.CallbackQuery):
    pkg_key = callback.data.replace("buy_", "")
    pkg = STAR_PACKAGES.get(pkg_key)
    if not pkg:
        await callback.answer("Пакет не найден", show_alert=True)
        return

    await callback.message.answer_invoice(
        title=pkg["title"],
        description=pkg["description"],
        payload=f"stars_{pkg_key}_{callback.from_user.id}_{int(time.time())}",
        currency="XTR",
        prices=[LabeledPrice(label=pkg["title"], amount=pkg["stars"])],
        provider_token=""
    )
    await callback.answer()


@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@dp.message(F.successful_payment)
async def successful_payment_handler(message: types.Message):
    sp = message.successful_payment
    payload = sp.invoice_payload
    stars_amount = sp.total_amount

    scans = 20
    if "pkg_50" in payload or stars_amount == 88:
        scans = 50
    elif "pkg_100" in payload or stars_amount == 235:
        scans = 100
    elif "pkg_20" in payload or stars_amount == 35:
        scans = 20

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{LOCAL_API}/api/user/add-stars-scans",
                json={"tg_id": str(message.from_user.id), "scans": scans, "stars": stars_amount}
            )
    except Exception:
        pass

    text = (
        f"🎉 <b>Оплата успешно получена!</b>\n\n"
        f"⭐️ Списано: <code>{stars_amount} Stars</code>\n"
        f"⚡ Начислено: <b>+{scans} OSINT-запросов</b>\n\n"
        f"<i>Запросы уже зачислены на ваш баланс. Откройте веб-панель для продолжения работы!</i>"
    )
    await message.answer(text, reply_markup=get_webapp_keyboard(), parse_mode="HTML")


# --- АДМИН-КОМАНДЫ УПРАВЛЕНИЯ ПАНЕЛЬЮ ---

@dp.message(Command("users"))
async def cmd_users(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Только для администратора.")
        return

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{LOCAL_API}/api/admin/users", headers={"X-Telegram-User-Id": str(message.from_user.id)})
            users = resp.json().get("users", [])

        if not users:
            await message.answer("👥 Список пользователей пуст.")
            return

        lines = ["👥 <b>Пользователи peace of the island of sor/ber peoples:</b>\n"]
        for u in users:
            st = "🟢" if u.get("status") == "active" else "🔴"
            vip_tag = " [👑 VIP]" if u.get("is_unlimited") else f" [⚡ {u.get('scan_balance', 0)} ост.]"
            twink_tag = " ⚠️ Твинк" if u.get("is_twink") else ""
            tg_info = f"@{u.get('tg_username')}" if u.get("tg_username") else f"ID:{u.get('tg_id')}"
            lines.append(f"{st} <b>{u.get('nickname') or u.get('username')}</b> ({tg_info}){vip_tag}{twink_tag} | Поисков: {u.get('total_scans')}")

        await message.answer("\n".join(lines), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.message(Command("setscans"))
async def cmd_setscans(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Только для администратора.")
        return

    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("⚠️ Формат: <code>/setscans позывной_или_tg_id количество</code>\nПример: <code>/setscans 5233450569 50</code>", parse_mode="HTML")
        return

    username = parts[1]
    try:
        amount = int(parts[2])
    except ValueError:
        await message.answer("❌ Количество должно быть числом.")
        return

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{LOCAL_API}/api/admin/user/set-quota",
                headers={"X-Telegram-User-Id": str(message.from_user.id)},
                json={"username": username, "amount": amount, "mode": "set"}
            )
            data = resp.json()

        if data.get("ok"):
            await message.answer(f"✅ {data.get('message')}", parse_mode="HTML")
        else:
            await message.answer(f"❌ {data.get('error')}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.message(Command("grantvip"))
async def cmd_grantvip(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Только для администратора.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ Формат: <code>/grantvip позывной_или_tg_id</code>", parse_mode="HTML")
        return

    username = parts[1]
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{LOCAL_API}/api/admin/user/set-quota",
                headers={"X-Telegram-User-Id": str(message.from_user.id)},
                json={"username": username, "mode": "unlimited"}
            )
            data = resp.json()

        if data.get("ok"):
            await message.answer(f"👑 Пользователю <code>{username}</code> выдан бесконечный доступ (VIP)!", parse_mode="HTML")
        else:
            await message.answer(f"❌ {data.get('error')}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.message(Command("adduser"))
async def cmd_adduser(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Только для администратора.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ Формат: <code>/adduser позывной [пароль] [роль]</code>", parse_mode="HTML")
        return

    username = parts[1]
    password = parts[2] if len(parts) > 2 else "12345"
    role = parts[3] if len(parts) > 3 else "user"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{LOCAL_API}/api/admin/users/create",
                headers={"X-Telegram-User-Id": str(message.from_user.id)},
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
        await message.answer("⚠️ Формат: <code>/banuser позывной_или_tg_id</code>", parse_mode="HTML")
        return

    username = parts[1]
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{LOCAL_API}/api/admin/users/toggle_status",
                headers={"X-Telegram-User-Id": str(message.from_user.id)},
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
            resp = await client.get(f"{LOCAL_API}/api/admin/visitors?limit=10", headers={"X-Telegram-User-Id": str(message.from_user.id)})
            visitors = resp.json().get("visitors", [])

        if not visitors:
            await message.answer("📊 Журнал визитов пуст.")
            return

        lines = ["🌐 <b>Последние 10 визитов:</b>\n"]
        for v in visitors:
            ts = v.get("ts", "")[:19].replace("T", " ")
            user_lbl = v.get("user") or v.get("tg_username") or v.get("tg_id") or "Гость"
            lines.append(f"• <code>{ts}</code> | <b>{user_lbl}</b> | IP: <code>{v.get('ip')}</code> | {v.get('country')} ({v.get('city')})")

        await message.answer("\n".join(lines), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.message()
async def fallback_any_message(message: types.Message):
    await message.answer(
        "🏝️ <b>peace of the island of sor/ber peoples</b>\n"
        "🌐 <i>Платформа OSINT-разведки. Для запуска поиска откройте веб-панель:</i>",
        reply_markup=get_webapp_keyboard(),
        parse_mode="HTML"
    )


import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Telegram Bot started in WebApp Launcher mode...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
