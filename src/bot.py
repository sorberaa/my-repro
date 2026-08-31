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
    BufferedInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    WebAppInfo,
)
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
USERS_FILE = DATA_DIR / "users.json"
LOCAL_API = "http://127.0.0.1:8000"

BOT_CACHE = {}
CACHE_TTL = 600

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
            [InlineKeyboardButton(text="🚀 Открыть WebApp Pro Hub", web_app=WebAppInfo(url=DOMAIN))],
            [
                InlineKeyboardButton(text="🔍 Sherlock 60+", callback_data="btn_sherlock"),
                InlineKeyboardButton(text="📸 Фото Экспертиза", callback_data="btn_photo")
            ]
        ]
    )


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    admin_text = ""
    if is_admin(message.from_user.id):
        admin_text = (
            "\n\n👑 <b>Админ-панель управления:</b>\n"
            "├ <code>/users</code> — Список пользователей и статистика\n"
            "├ <code>/adduser &lt;login&gt; &lt;pass&gt; &lt;role&gt;</code> — Создать аккаунт\n"
            "├ <code>/banuser &lt;login&gt;</code> — Заблокировать/Разблокировать\n"
            "└ <code>/visits</code> — Просмотр IP-логов визитов в реальном времени"
        )
    
    text = (
        "🕵️ <b>Добро пожаловать в OSINT Pro Hub Bot!</b>\n\n"
        "Высокоскоростной комплекс разведки по открытым источникам (Sherlock 60+ баз), экспертизы фото (EXIF/GPS), анализа сайтов и дедукции (Gemini Vision AI).\n\n"
        "⚡ <b>Команды бота:</b>\n"
        "├ <code>/scan &lt;username&gt;</code> — Кросс-поиск аккаунтов по 60+ базам\n"
        "├ <code>/tg &lt;@user/ID&gt;</code> — Глубокая разведка Telegram\n"
        "├ <code>/export &lt;target&gt;</code> — Сформировать и скачать полный TXT-отчет\n"
        "├ <code>/ai &lt;target&gt;</code> — ИИ-досье личности (Gemini AI)\n"
        "├ <code>/ip &lt;8.8.8.8&gt;</code> — Геолокация и провайдер по IP\n"
        "├ 📸 <b>Отправьте фото в чат</b> — извлечение скрытых GPS координат и анализ местности\n"
        "└ <code>/id</code> — Узнать свой Telegram ID"
        f"{admin_text}\n\n"
        "👇 <i>Запустить графическую панель:</i>"
    )
    await message.answer(text, reply_markup=get_webapp_keyboard(), parse_mode="HTML")


@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    await message.answer(f"🆔 <b>Ваш Telegram ID:</b> <code>{message.from_user.id}</code>", parse_mode="HTML")


# --- ЭКСПОРТ ПОЛНОГО ОТЧЕТА В ФАЙЛ (/export <target>) ---

@dp.message(Command("export"))
async def cmd_export(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Укажите цель для экспорта отчета: <code>/export wertag20</code>", parse_mode="HTML")
        return

    target = args[1].strip().lstrip("@")
    status_msg = await message.answer(f"📑 <i>Формирование полного досье и экспортного файла для <b>{target}</b>...</i>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(f"{LOCAL_API}/api/scan/username", json={"target": target, "caller": f"tg_{message.from_user.id}"})
            data = resp.json()

        profiles = data.get("profiles", [])
        found_count = data.get("found_count", 0)
        total = data.get("total_checked", 0)
        ai_summary = data.get("ai_summary", "")
        pdata = data.get("probable_data", {})

        now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC")
        report_content = f"""====================================================
OSINT PRO HUB — ПОЛНОЕ ИССЛЕДОВАТЕЛЬСКОЕ ДОСЬЕ
Цель исследования: {target}
Дата генерации: {now_str}
Оператор: Telegram ID {message.from_user.id}
Всего проверено сервисов: {total}
Подтвержденных активных аккаунтов: {found_count}
====================================================

[1] СВОДНЫЕ НАИВЕРОЯТНЕЙШИЕ ДАННЫЕ:
• Вероятное имя: {pdata.get('name') or target}
• Вероятная локация: {pdata.get('location') or 'Не указана'}
• Старейший аккаунт: {pdata.get('oldest_account') or '2019–2022'}

====================================================
[2] НАЙДЕННЫЕ ОТКРЫТЫЕ ПРОФИЛИ:
"""
        for p in profiles:
            report_content += f"• [{p.get('category', 'Другое')}] {p.get('platform')}: {p.get('url')}\n"

        report_content += f"""
====================================================
[3] АНАЛИТИЧЕСКИЙ ПОРТРЕТ ЛИЧНОСТИ (GEMINI AI):
{ai_summary}
====================================================
Сформировано автоматически OSINT Pro Hub Engine
"""

        doc_file = BufferedInputFile(report_content.encode("utf-8"), filename=f"OSINT_Report_{target}.txt")
        await message.answer_document(
            doc_file,
            caption=f"📁 <b>Полный OSINT-отчет для цели:</b> <code>{target}</code>\nНайдено аккаунтов: <b>{found_count}</b>",
            parse_mode="HTML"
        )
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка генерации файла отчета: {str(e)}")


# --- ОБРАБОТЧИК ФОТОГРАФИЙ (EXIF + GPS + VISION AI) ---

@dp.message(F.photo)
async def handle_photo_message(message: types.Message):
    photo = message.photo[-1]
    status_msg = await message.answer("📸 <i>Скачивание фото и извлечение EXIF метаданных + Vision AI анализ...</i>", parse_mode="HTML")

    file_io = io.BytesIO()
    await bot.download(photo, destination=file_io)
    image_bytes = file_io.getvalue()

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            files = {"file": ("photo.jpg", image_bytes, "image/jpeg")}
            resp = await client.post(f"{LOCAL_API}/api/scan/photo", files=files)
            data = resp.json()

        exif = data.get("exif", {})
        vision_report = data.get("vision_ai_report", "")
        gps = exif.get("gps")

        res_lines = ["📸 <b>Результаты экспертизы фотографии:</b>\n"]
        res_lines.append(f"• <b>Камера:</b> {exif.get('camera_make') or '—'} {exif.get('camera_model') or 'Не указана'}")
        res_lines.append(f"• <b>Дата съемки:</b> {exif.get('date_time') or 'Скрыта в метаданных'}")
        res_lines.append(f"• <b>ПО/Редактор:</b> {exif.get('software') or 'Оригинал'}")

        if gps:
            res_lines.append(f"\n📍 <b>GPS Координаты найдены:</b> <code>{gps['latitude']}, {gps['longitude']}</code>")
            res_lines.append(f"🔗 <a href='{exif.get('google_maps_url')}'>Открыть точку на Google Maps</a>")
        else:
            res_lines.append("\n📍 <b>GPS:</b> Гео-координаты отсутствуют в EXIF")

        if vision_report:
            res_lines.append(f"\n🧠 <b>Анализ местности (Gemini Vision AI):</b>\n{vision_report}")

        buttons = [
            [InlineKeyboardButton(text="Яндекс Картинки", url="https://yandex.ru/images/search?rpt=imageview"),
             InlineKeyboardButton(text="Google Lens", url="https://lens.google.com/")],
            [InlineKeyboardButton(text="🚀 Открыть в WebApp", web_app=WebAppInfo(url=DOMAIN))]
        ]

        await status_msg.edit_text(
            "\n".join(res_lines),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            parse_mode="HTML",
            disable_web_page_preview=False
        )

        if gps:
            await message.answer_location(latitude=gps["latitude"], longitude=gps["longitude"])

    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка анализа фото: {str(e)}")


# --- СУПЕР-ПОИСКОВИК SHERLOCK (60+ БАЗ ДАННЫХ) С ВЫВОДОМ НАИВЕРОЯТНЕЙШИХ ДАННЫХ ---

@dp.message(Command("scan"))
@dp.message(Command("sherlock"))
async def cmd_scan_sherlock(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Укажите никнейм для поиска: <code>/scan wertag20</code>", parse_mode="HTML")
        return

    target = args[1].strip().lstrip("@")
    status_msg = await message.answer(f"🔍 <i>Sherlock Engine: параллельный опрос 60+ баз данных для <b>{target}</b>...</i>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(f"{LOCAL_API}/api/scan/username", json={"target": target, "caller": f"tg_{message.from_user.id}"})
            data = resp.json()

        profiles = data.get("profiles", [])
        found_count = data.get("found_count", 0)
        total = data.get("total_checked", 0)
        ai_summary = data.get("ai_summary", "")
        pdata = data.get("probable_data", {})

        res_lines = [f"🎯 <b>OSINT РАСКРЫТИЕ ЦЕЛИ:</b> <code>{target}</code>\n"]

        # НАИВЕРОЯТНЕЙШИЕ ДАННЫЕ
        if pdata:
            res_lines.append("📌 <b>НАИВЕРОЯТНЕЙШИЕ ДАННЫЕ (ИИ СИНТЕЗ):</b>")
            res_lines.append(f"• 👤 <b>Вероятное имя:</b> <code>{pdata.get('name') or target}</code>")
            res_lines.append(f"• 🏙️ <b>Локация:</b> <code>{pdata.get('location') or 'По часовому поясу'}</code>")
            res_lines.append(f"• 📅 <b>Старейший аккаунт:</b> <code>{pdata.get('oldest_account') or '2019–2022'}</code>")
            res_lines.append(f"• 🔗 <b>Активных профилей:</b> <b>{found_count}</b> из {total}\n")

        # Группировка по категориям
        categories = {}
        for p in profiles:
            cat = p.get("category", "Другое")
            categories.setdefault(cat, []).append(p)

        for cat, items in categories.items():
            res_lines.append(f"📁 <b>{cat}:</b>")
            for p in items:
                res_lines.append(f"  • <b>{p['platform']}</b>: <a href='{p['url']}'>Открыть</a>")
            res_lines.append("")

        if not profiles:
            res_lines.append("❌ Прямых открытых совпадений не обнаружено.")

        if ai_summary:
            res_lines.append(f"🧠 <b>Аналитический портрет (AI):</b>\n{ai_summary}")

        text = "\n".join(res_lines)
        if len(text) > 3900:
            text = text[:3850] + "…\n<i>(Используйте /export для скачивания полного файла)</i>"

        buttons = [
            [InlineKeyboardButton(text="📄 Скачать TXT-отчет", callback_data=f"exp_{target[:20]}")],
            [InlineKeyboardButton(text="🚀 Открыть в WebApp", web_app=WebAppInfo(url=DOMAIN))]
        ]

        await status_msg.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка сканирования: {str(e)}")


@dp.callback_query(F.data.startswith("exp_"))
async def cb_export_target(call: types.CallbackQuery):
    target = call.data.replace("exp_", "")
    fake_msg = call.message
    fake_msg.text = f"/export {target}"
    await cmd_export(fake_msg)
    await call.answer()


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
    status_msg = await message.answer(f"🧠 <i>Нейросеть Gemini анализирует цифровой след для <b>{target}</b>...</i>", parse_mode="HTML")

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


# --- АДМИН-КОМАНДЫ: УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ И ЛОГАМИ ---

@dp.message(Command("users"))
async def cmd_users(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступно только администратору.")
        return

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{LOCAL_API}/api/admin/users")
            users = resp.json().get("users", [])

        lines = ["👥 <b>Зарегистрированные пользователи OSINT Hub:</b>\n"]
        for u in users:
            status_icon = "🟢" if u["status"] == "active" else "🔴"
            lines.append(f"{status_icon} <b>{u['username']}</b> | Роль: <code>{u['role'].upper()}</code> | Поисков: <b>{u['total_scans']}</b>\n📅 Создан: {u['created_at']} ({u['notes'] or 'без заметок'})")

        await message.answer("\n\n".join(lines), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка загрузки пользователей: {str(e)}")


@dp.message(Command("adduser"))
async def cmd_adduser(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступно только администратору.")
        return

    parts = message.text.split(maxsplit=3)
    if len(parts) < 3:
        await message.answer("⚠️ Формат: <code>/adduser login password [role=user/vip/admin]</code>", parse_mode="HTML")
        return

    username = parts[1].strip()
    password = parts[2].strip()
    role = parts[3].strip() if len(parts) > 3 else "user"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(f"{LOCAL_API}/api/admin/users/create", json={"username": username, "password": password, "role": role})
            data = resp.json()
        if data.get("ok"):
            await message.answer(f"✅ Пользователь <b>{username}</b> с ролью <code>{role}</code> успешно создан!", parse_mode="HTML")
        else:
            await message.answer(f"❌ Ошибка: {data.get('error')}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.message(Command("banuser"))
async def cmd_banuser(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступно только администратору.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Формат: <code>/banuser login</code>", parse_mode="HTML")
        return

    username = parts[1].strip()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(f"{LOCAL_API}/api/admin/users/toggle_status", json={"username": username})
            data = resp.json()
        await message.answer(f"🔄 Статус пользователя <b>{username}</b> изменен на: <code>{data.get('new_status')}</code>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


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


# --- TELEGRAM INLINE MODE (БЫСТРЫЙ ПОИСК В ЛЮБОМ ЧАТЕ) ---

@dp.inline_query()
async def inline_search(query: InlineQuery):
    q = query.query.strip().lstrip("@")
    if not q or len(q) < 2:
        return

    results = [
        InlineQueryResultArticle(
            id=f"scan_{q}",
            title=f"🔍 Sherlock OSINT: {q}",
            description=f"Нажмите, чтобы отправить сводку по 60+ базам для {q}",
            input_message_content=InputTextMessageContent(
                message_text=f"🕵️ <b>Запрос разведки для цели:</b> <code>{q}</code>\nЗапустите бота или введите <code>/scan {q}</code> для полного досье.",
                parse_mode="HTML"
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="🚀 Открыть OSINT Hub", web_app=WebAppInfo(url=DOMAIN))]]
            )
        )
    ]
    await query.answer(results, cache_time=10)


@dp.callback_query(F.data == "btn_sherlock")
async def cb_sherlock(call: types.CallbackQuery):
    await call.message.answer("🔍 Для запуска супер-поиска по 60+ базам данных отправьте:\n<code>/scan wertag20</code> или <code>/sherlock username</code>", parse_mode="HTML")
    await call.answer()


@dp.callback_query(F.data == "btn_photo")
async def cb_photo(call: types.CallbackQuery):
    await call.message.answer("📸 <b>Просто отправьте любое фото прямо сюда в чат!</b>\nБот автоматически извлечет EXIF, GPS координаты и проведет анализ местности через Gemini Vision AI.", parse_mode="HTML")
    await call.answer()


@dp.message(F.text)
async def auto_text_handler(message: types.Message):
    txt = message.text.strip()
    if txt.startswith("/"):
        return

    if txt.startswith("@") or txt.isdigit():
        await cmd_tg(message)
    else:
        await cmd_scan_sherlock(message)


async def main():
    logging.info("Starting Telegram Bot Polling with Inline Mode & User System...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
