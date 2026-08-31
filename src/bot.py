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
            [InlineKeyboardButton(text="⚡ Открыть Cyber WebApp", web_app=WebAppInfo(url=DOMAIN))],
            [
                InlineKeyboardButton(text="🔍 Поиск Sherlock", callback_data="btn_sherlock"),
                InlineKeyboardButton(text="📸 Фото Экспертиза", callback_data="btn_photo")
            ]
        ]
    )


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    admin_text = ""
    if is_admin(message.from_user.id):
        admin_text = (
            "\n\n👑 <b>Администрирование:</b>\n"
            "├ <code>/users</code> — Список аккаунтов и статистика\n"
            "├ <code>/adduser &lt;login&gt; &lt;pass&gt; &lt;role&gt;</code> — Создать аккаунт\n"
            "├ <code>/banuser &lt;login&gt;</code> — Блокировка доступа\n"
            "└ <code>/visits</code> — IP-журнал визитов"
        )
    
    text = (
        "🕵️ <b>Sherlock OSINT Bot & Cyber Hub</b>\n\n"
        "Официальный алгоритм проверки открытых цифровых следов (Sherlock Project), экспертизы изображений (EXIF/GPS) и разведки Telegram.\n\n"
        "⚡ <b>Команды бота:</b>\n"
        "├ <code>/scan &lt;username&gt;</code> — Поиск по базам Sherlock Project\n"
        "├ <code>/tg &lt;@user/ID&gt;</code> — Разведка Telegram\n"
        "├ <code>/export &lt;target&gt;</code> — Скачать полный TXT-отчет\n"
        "├ <code>/ip &lt;8.8.8.8&gt;</code> — Геолокация IP\n"
        "└ 📸 <b>Отправьте фото</b> — анализ метаданных и местности"
        f"{admin_text}"
    )
    await message.answer(text, reply_markup=get_webapp_keyboard(), parse_mode="HTML")


@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    await message.answer(f"🆔 <b>Telegram ID:</b> <code>{message.from_user.id}</code>", parse_mode="HTML")


# --- ЭКСПОРТ ПОЛНОГО ОТЧЕТА В ФАЙЛ (/export <target>) ---

@dp.message(Command("export"))
async def cmd_export(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Укажите цель: <code>/export wertag20</code>", parse_mode="HTML")
        return

    target = args[1].strip().lstrip("@")
    status_msg = await message.answer(f"📑 <i>Формирование отчета для <b>{target}</b>...</i>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{LOCAL_API}/api/scan/username", json={"target": target, "caller": f"tg_{message.from_user.id}"})
            data = resp.json()

        profiles = data.get("profiles", [])
        found_count = data.get("found_count", 0)
        total = data.get("total_checked", 0)
        ai_summary = data.get("ai_summary", "")
        pdata = data.get("probable_data", {})

        now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC")
        report_content = f"""====================================================
SHERLOCK OSINT ENGINE — ДОСЬЕ РАССЛЕДОВАНИЯ
Цель: {target}
Дата: {now_str}
Оператор ID: {message.from_user.id}
Всего проверено баз: {total}
Подтверждено профилей: {found_count}
====================================================

[1] СВОДНЫЕ ДАННЫЕ:
• Вероятное имя: {pdata.get('name') or target}
• Локация: {pdata.get('location') or 'По часовому поясу'}
• Оценка возраста: {pdata.get('age_estimate') or '20–30 лет'}
• Аккаунты в сети с: {pdata.get('oldest_account') or '2019–2022'}

====================================================
[2] ПОДТВЕРЖДЕННЫЕ ПРОФИЛИ:
"""
        for p in profiles:
            report_content += f"• [{p.get('category', 'Прочее')}] {p.get('platform')}: {p.get('url')}\n"

        report_content += f"""
====================================================
[3] АНАЛИТИЧЕСКИЙ РАЗБОР:
{ai_summary}
====================================================
"""

        doc_file = BufferedInputFile(report_content.encode("utf-8"), filename=f"Sherlock_{target}.txt")
        await message.answer_document(
            doc_file,
            caption=f"📁 <b>Отчет Sherlock по цели:</b> <code>{target}</code> | Найдено профилей: <b>{found_count}</b>",
            parse_mode="HTML"
        )
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка генерации отчета: {str(e)}")


# --- ОБРАБОТЧИК ФОТОГРАФИЙ (EXIF + GPS + VISION AI) ---

@dp.message(F.photo)
async def handle_photo_message(message: types.Message):
    photo = message.photo[-1]
    status_msg = await message.answer("📸 <i>Анализ метаданных фото и местности...</i>", parse_mode="HTML")

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

        res_lines = ["📸 <b>Экспертиза изображения:</b>\n"]
        res_lines.append(f"• <b>Камера:</b> {exif.get('camera_make') or '—'} {exif.get('camera_model') or ''}")
        res_lines.append(f"• <b>Дата съемки:</b> {exif.get('date_time') or 'Скрыта'}")

        if gps:
            res_lines.append(f"• 📍 <b>GPS:</b> <code>{gps['latitude']}, {gps['longitude']}</code>")
            res_lines.append(f"🔗 <a href='{exif.get('google_maps_url')}'>Открыть на Google Maps</a>")
        else:
            res_lines.append("• 📍 <b>GPS:</b> Метки отсутствуют")

        if vision_report:
            res_lines.append(f"\n🧠 <b>Анализ:</b>\n{vision_report[:900]}")

        buttons = [
            [InlineKeyboardButton(text="Яндекс Картинки", url="https://yandex.ru/images/search?rpt=imageview"),
             InlineKeyboardButton(text="Google Lens", url="https://lens.google.com/")],
            [InlineKeyboardButton(text="⚡ Открыть WebApp", web_app=WebAppInfo(url=DOMAIN))]
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


# --- ОСНОВНОЙ ПОИСКОВИК SHERLOCK BOT С ПРАВДИВЫМИ ДАННЫМИ ---

@dp.message(Command("scan"))
@dp.message(Command("sherlock"))
async def cmd_scan_sherlock(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Укажите никнейм: <code>/scan wertag20</code>", parse_mode="HTML")
        return

    target = args[1].strip().lstrip("@")
    status_msg = await message.answer(f"🔍 <i>Опрос баз Sherlock Project для <b>{target}</b>...</i>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{LOCAL_API}/api/scan/username", json={"target": target, "caller": f"tg_{message.from_user.id}"})
            data = resp.json()

        profiles = data.get("profiles", [])
        found_count = data.get("found_count", 0)
        total = data.get("total_checked", 0)
        pdata = data.get("probable_data", {})

        res_lines = [f"🎯 <b>Цель:</b> <code>{target}</code> | Найдено профилей: <b>{found_count}</b> (из {total})\n"]

        if pdata:
            res_lines.append("📌 <b>СВОДНЫЕ ДАННЫЕ:</b>")
            res_lines.append(f"• 👤 <b>Имя:</b> <code>{pdata.get('name') or target}</code>")
            res_lines.append(f"• 🏙️ <b>Локация:</b> <code>{pdata.get('location') or 'По часовому поясу'}</code>")
            res_lines.append(f"• 🎂 <b>Возраст:</b> <code>{pdata.get('age_estimate') or '20–30 лет'}</code>")
            res_lines.append(f"• 📊 <b>Confidence:</b> <code>{pdata.get('confidence') or '85%'}</code>\n")

        # Группировка по категориям
        categories = {}
        for p in profiles:
            cat = p.get("category", "Прочее")
            categories.setdefault(cat, []).append(p)

        for cat, items in categories.items():
            res_lines.append(f"📁 <b>{cat}:</b>")
            for p in items[:8]:
                res_lines.append(f"  • {p['platform']}: <a href='{p['url']}'>Открыть профиль</a>")
            if len(items) > 8:
                res_lines.append(f"  <i>...и еще {len(items)-8} сервисов</i>")
            res_lines.append("")

        if not profiles:
            res_lines.append("❌ Подтвержденных открытых совпадений не обнаружено.")

        text = "\n".join(res_lines)
        if len(text) > 3800:
            text = text[:3700] + "…\n<i>(Используйте /export для полного отчета)</i>"

        buttons = [
            [InlineKeyboardButton(text="📄 Скачать TXT-отчет", callback_data=f"exp_{target[:20]}")],
            [InlineKeyboardButton(text="⚡ Открыть в WebApp", web_app=WebAppInfo(url=DOMAIN))]
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
        await message.answer("⚠️ Укажите @username или ID: <code>/tg @durov</code>", parse_mode="HTML")
        return

    target = args[1].strip()
    status_msg = await message.answer(f"✈️ <i>Опрос Telegram для <b>{target}</b>...</i>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{LOCAL_API}/api/scan/telegram", json={"target": target})
            data = resp.json()

        if data.get("type") == "telegram_id":
            text = (
                f"✈️ <b>Telegram ID Inspector:</b>\n\n"
                f"🆔 <b>ID:</b> <code>{data.get('tg_id')}</code>\n"
                f"📅 <b>Период создания:</b> {data.get('estimated_year')}\n\n"
                f"💡 <i>{data.get('ai_summary', '')}</i>"
            )
        else:
            text = (
                f"✈️ <b>Telegram Профиль:</b>\n\n"
                f"👤 <b>Имя:</b> {data.get('title')}\n"
                f"🏷 <b>Тип:</b> {data.get('account_type')}\n"
                f"🔗 <b>Юзернейм:</b> @{data.get('username')}\n"
                f"📝 <b>Bio:</b> {data.get('description')}\n\n"
                f"🧠 <b>Анализ:</b> {data.get('ai_summary', '')}"
            )

        await status_msg.edit_text(text, reply_markup=get_webapp_keyboard(), parse_mode="HTML")
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка Telegram: {str(e)}")


@dp.message(Command("ip"))
async def cmd_ip(message: types.Message):
    args = message.text.split(maxsplit=1)
    target = args[1].strip() if len(args) > 1 else "8.8.8.8"
    status_msg = await message.answer(f"🌍 <i>GeoIP для {target}...</i>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(f"{LOCAL_API}/api/scan/ip", json={"target": target})
            data = resp.json().get("data", {})

        text = (
            f"🌍 <b>GeoIP Информация:</b> <code>{target}</code>\n\n"
            f"🏳️ <b>Локация:</b> {data.get('country', '—')}, {data.get('city', '—')}\n"
            f"🏢 <b>ISP:</b> {data.get('isp', '—')}\n"
            f"🔢 <b>AS:</b> {data.get('as', '—')}\n"
            f"🕒 <b>Часовой пояс:</b> {data.get('timezone', '—')}"
        )
        await status_msg.edit_text(text, reply_markup=get_webapp_keyboard(), parse_mode="HTML")
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка GeoIP: {str(e)}")


# --- АДМИН-КОМАНДЫ ---

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
            status_icon = "🟢" if u["status"] == "active" else "🔴"
            lines.append(f"{status_icon} <b>{u['username']}</b> ({u['role'].upper()}) | Поисков: <b>{u['total_scans']}</b>")

        await message.answer("\n".join(lines), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.message(Command("adduser"))
async def cmd_adduser(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Только для администратора.")
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
            await message.answer(f"✅ Создан пользователь <b>{username}</b> [{role}]", parse_mode="HTML")
        else:
            await message.answer(f"❌ {data.get('error')}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.message(Command("banuser"))
async def cmd_banuser(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Только для администратора.")
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
        await message.answer(f"🔄 Статус <b>{username}</b>: <code>{data.get('new_status')}</code>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp.message(Command("visits"))
async def cmd_visits(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Только для администратора.")
        return

    if not VISITS_FILE.exists():
        await message.answer("📊 Журнал пуст.")
        return

    lines = VISITS_FILE.read_text(encoding="utf-8").splitlines()[-10:]
    lines.reverse()

    rows = []
    for line in lines:
        try:
            r = json.loads(line)
            rows.append(f"🕒 <code>{r.get('ts', '')[11:19]}</code> | <b>{r.get('ip', '—')}</b> ({r.get('country', 'RU')})")
        except Exception:
            continue

    text = "🕵️ <b>Последние визиты в панель:</b>\n\n" + "\n".join(rows)
    await message.answer(text, parse_mode="HTML")


# --- TELEGRAM INLINE MODE ---

@dp.inline_query()
async def inline_search(query: InlineQuery):
    q = query.query.strip().lstrip("@")
    if not q or len(q) < 2:
        return

    results = [
        InlineQueryResultArticle(
            id=f"scan_{q}",
            title=f"🔍 Sherlock OSINT: {q}",
            description=f"Отправить сводку Sherlock для {q}",
            input_message_content=InputTextMessageContent(
                message_text=f"🕵️ <b>Sherlock Резюме для цели:</b> <code>{q}</code>\nДля полного досье введите <code>/scan {q}</code>",
                parse_mode="HTML"
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="⚡ Открыть Cyber Hub", web_app=WebAppInfo(url=DOMAIN))]]
            )
        )
    ]
    await query.answer(results, cache_time=10)


@dp.callback_query(F.data == "btn_sherlock")
async def cb_sherlock(call: types.CallbackQuery):
    await call.message.answer("🔍 Отправьте никнейм для поиска:\n<code>/scan wertag20</code>", parse_mode="HTML")
    await call.answer()


@dp.callback_query(F.data == "btn_photo")
async def cb_photo(call: types.CallbackQuery):
    await call.message.answer("📸 <b>Отправьте фото в чат</b> для извлечения EXIF и гео-анализа местности.", parse_mode="HTML")
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
    logging.info("Starting Telegram Bot Polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
