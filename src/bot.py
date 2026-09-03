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
        admin_text = "\n\n👑 <b>Административный доступ:</b>\n<code>/users</code> — база пользователей | <code>/setscans</code> — выдать баланс\n<code>/grantvip</code> — выдать безлимит | <code>/visits</code> — логи визитов"
    text = (
        "🛡️ <b>ISLAND INTELLIGENCE // CYBER & OSINT FORENSICS</b>\n"
        "<code>SYSTEM_STATUS: ONLINE [v2.4_SECURE]</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Аналитический комплекс глубокой сетевой разведки, анализа цифрового следа и деанонимизации открытых источников.\n\n"
        "🎯 <b>АКТИВНЫЕ МОДУЛИ КОМПЛЕКСА:</b>\n"
        "├ <b>Sherlock Intelligence:</b> Сквозной поиск по 480+ международным платформам\n"
        "├ <b>Social Recon:</b> Анализ профилей Instagram, TikTok, VK и истории коммитов GitHub\n"
        "├ <b>Crypto Forensics:</b> Аудит балансов, связей и транзакций BTC, ETH, TRX, SOL\n"
        "├ <b>Attribution Engine:</b> Выявление связи виртуальных аккаунтов с основой\n"
        "├ <b>GeoINT & SunCalc:</b> Определение локации по EXIF и времени съемки по теням\n"
        "├ <b>Dork Matrix:</b> Поисковые алгоритмы скрытых баз, документов и утечек\n"
        "└ <b>Web Graph:</b> Интерактивное построение графа связей цели\n\n"
        f"🔐 <b>ИДЕНТИФИКАТОР:</b> <code>{message.from_user.id}</code>\n"
        "🎁 <b>ВЫДЕЛЕННЫЙ БАЛАНС:</b> <code>5 бесплатных проверок</code>\n"
        "⭐️ <b>ПОПОЛНЕНИЕ КВОТЫ:</b> <code>/buy</code> (Telegram Stars)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ <i>Запустите рабочий терминал нажатием кнопки ниже:</i>"
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


# --- ПОЛЬЗОВАТЕЛЬСКИЕ КОМАНДЫ БЫСТРОГО АНАЛИЗА ---

@dp.message(Command("dossier"))
@dp.message(Command("profiler"))
async def cmd_dossier(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("🧠 <b>AI Detective Profiler:</b>\nИспользование: <code>/dossier @username</code> или <code>/dossier Имя Фамилия</code>", parse_mode="HTML")
        return

    target = parts[1].strip()
    status_msg = await message.answer(f"⏳ <i>Собираю данные по открытым реестрам и формирую AI-досье на '{target}'...</i>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                f"{LOCAL_API}/api/scan/ai_profiler",
                json={"target": target, "caller": str(message.from_user.id)},
                headers={"X-Telegram-User-Id": str(message.from_user.id)}
            )
            data = resp.json()

        if not data.get("ok"):
            await status_msg.edit_text(f"❌ <b>Ошибка:</b> {data.get('error', 'Не удалось сформировать досье')}", parse_mode="HTML")
            return

        scam = data.get("scam_score", 15)
        badge = "🟢 Высокая подлинность" if scam < 30 else ("🟡 Требует проверки" if scam < 60 else "🔴 Высокий риск / Фейк")
        report = data.get("dossier_text", "Досье сформировано.")

        text = (
            f"🧠 <b>AI DETECTIVE DOSSIER // {target}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ <b>Scam/Catfish Score:</b> <code>{scam}%</code> ({badge})\n"
            f"🌐 <b>Обнаружено платформ:</b> <code>{data.get('profiles_count', 0)}</code>\n\n"
            f"{report[:3600]}"
        )
        await status_msg.edit_text(text, reply_markup=get_webapp_keyboard(), parse_mode="Markdown")
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка соединения: {str(e)}")


@dp.message(Command("aml"))
async def cmd_aml(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("🚨 <b>Crypto AML & Sanctions Auditor:</b>\nИспользование: <code>/aml 0x71C... / bc1q... / T...</code>", parse_mode="HTML")
        return

    target = parts[1].strip()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{LOCAL_API}/api/scan/crypto_aml",
                json={"target": target, "caller": str(message.from_user.id)},
                headers={"X-Telegram-User-Id": str(message.from_user.id)}
            )
            data = resp.json()

        if not data.get("ok"):
            await message.answer(f"❌ {data.get('error', 'Ошибка проверки AML')}")
            return

        flags_text = "\n".join([f"• {f}" for f in data.get("flags", [])])
        text = (
            f"🚨 <b>CRYPTO AML AUDIT // {data.get('coin')}</b>\n"
            f"<code>{data.get('address')}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 <b>Индекс риска AML:</b> <code>{data.get('aml_risk_score')}% / 100%</code>\n"
            f"🏷️ <b>Статус:</b> <b>{data.get('risk_level')}</b>\n\n"
            f"💡 <b>Рекомендация:</b>\n{data.get('recommendation')}\n\n"
            f"<b>Факторы анализа:</b>\n{flags_text}"
        )
        await message.answer(text, reply_markup=get_webapp_keyboard(), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка проверки: {str(e)}")


@dp.message(Command("spy"))
async def cmd_spy(message: types.Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        await message.answer("⏱️ <b>Spy Activity & Sleep Tracker:</b>\nИспользование: <code>/spy @username</code> или <code>/spy @user1 @user2</code> (Mutual Spy)", parse_mode="HTML")
        return

    target1 = parts[1].strip().lstrip("@")
    target2 = parts[2].strip().lstrip("@") if len(parts) > 2 else ""

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{LOCAL_API}/api/scan/activity_tracker",
                json={"target": target1, "target2": target2, "caller": str(message.from_user.id)},
                headers={"X-Telegram-User-Id": str(message.from_user.id)}
            )
            data = resp.json()

        if not data.get("ok"):
            await message.answer(f"❌ {data.get('error', 'Ошибка трекера')}")
            return

        mutual_block = ""
        if data.get("mutual_analysis"):
            m = data["mutual_analysis"]
            mutual_block = f"\n\n💞 <b>Mutual Spy (Совпадение с @{m['target2']}):</b>\n<b>Индекс связи:</b> <code>{m['overlap_score']}%</code>\n{m['communication_likelihood']}"

        text = (
            f"⏱️ <b>SPY ACTIVITY REPORT // @{target1}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🌍 <b>Часовой пояс:</b> <code>{data.get('timezone')}</code>\n"
            f"💤 <b>Режим сна (оффлайн):</b> <code>{data.get('sleep_phase')}</code>\n"
            f"🔥 <b>Пики активности:</b> <code>{data.get('peak_activity')}</code>"
            f"{mutual_block}\n\n"
            f"<i>Подробная почасовая тепловая карта доступна в WebApp.</i>"
        )
        await message.answer(text, reply_markup=get_webapp_keyboard(), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка трекера: {str(e)}")


@dp.message(Command("audit"))
async def cmd_audit(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("🛡️ <b>Personal Breach & Digital Hygiene Audit:</b>\nИспользование: <code>/audit your_email@domain.com</code> или <code>/audit +380...</code>", parse_mode="HTML")
        return

    target = parts[1].strip()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{LOCAL_API}/api/scan/breach_audit",
                json={"identifier": target, "caller": str(message.from_user.id)},
                headers={"X-Telegram-User-Id": str(message.from_user.id)}
            )
            data = resp.json()

        if not data.get("ok"):
            await message.answer(f"❌ {data.get('error', 'Ошибка аудита')}")
            return

        leaks = "\n".join([f"• 📁 <b>{l['source']}</b> ({l['date']})" for l in data.get("leaks", [])])
        checklist = "\n".join([f"{c}" for c in data.get("remediation_checklist", [])[:3]])

        text = (
            f"🛡️ <b>DIGITAL HYGIENE AUDIT // {target}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🚨 <b>Упоминаний в утечках:</b> <code>{data.get('leaks_count')} баз данных</code>\n"
            f"📊 <b>Индекс уязвимости (DEI):</b> <code>{data.get('exposure_score')}/100</code> [<b>{data.get('security_grade')}</b>]\n\n"
            f"<b>Обнаружено в утечках:</b>\n{leaks}\n\n"
            f"💡 <b>Рекомендации по защите:</b>\n{checklist}"
        )
        await message.answer(text, reply_markup=get_webapp_keyboard(), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка аудита: {str(e)}")


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
