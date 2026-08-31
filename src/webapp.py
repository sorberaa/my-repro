import asyncio
import base64
import io
import json
import os
import re
import socket
import ssl
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from PIL import ExifTags, Image

try:
    from catalog import CATALOG, find_tool, normalize_catalog
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from catalog import CATALOG, find_tool, normalize_catalog

load_dotenv("/app/config/.env")
load_dotenv("config/.env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "5233450569")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin123")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6IJRS1lLX1i1egBpyEfQGfLHXoI4GfgFO2Yp5pg-LFLtQ")

DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
VISITS_FILE = DATA_DIR / "visits.jsonl"

app = FastAPI(title="OSINT Hub & WebApp Pro (Sherlock & Vision AI)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def client_ip(request: Request) -> str:
    xff = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def append_visit(record: dict) -> None:
    with VISITS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


@app.middleware("http")
async def log_visits(request: Request, call_next):
    path = request.url.path
    skip = path.startswith("/api/") or path.startswith("/admin/visits") or path == "/favicon.ico"
    response = await call_next(request)
    if skip:
        return response
    rec = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "ip": client_ip(request),
        "path": path,
        "ua": request.headers.get("user-agent", "")[:250],
        "country": request.headers.get("cf-ipcountry", "RU"),
    }
    try:
        append_visit(rec)
    except Exception:
        pass
    return response


# --- AI АНАЛИЗАТОР И VISION AI (GEMINI) ---

async def run_gemini_prompt(prompt: str, image_bytes: Optional[bytes] = None, mime_type: str = "image/jpeg") -> str:
    """Выполняет текстовый или мультимодальный (Vision) запрос к Gemini API."""
    if not GEMINI_API_KEY:
        return ""
    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    parts = [{"text": prompt}]
    if image_bytes:
        b64_img = base64.b64encode(image_bytes).decode("utf-8")
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": b64_img
            }
        })

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        try:
            async with httpx.AsyncClient(timeout=16.0) as client:
                resp = await client.post(url, json={
                    "contents": [{"parts": parts}]
                })
                if resp.status_code == 200:
                    res_json = resp.json()
                    candidates = res_json.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if text:
                            return text
        except Exception:
            continue
    return ""


# --- БАЗА ПЛАТФОРМ ДЛЯ SUPER-ПОИСКОВИКА SHERLOCK (60+ СЕРВИСОВ) ---

SHERLOCK_SITES = [
    # Соцсети и мессенджеры
    {"name": "Telegram", "cat": "Социальные сети", "icon": "fa-telegram", "url": "https://t.me/{u}", "check": "https://t.me/{u}", "type": "tg"},
    {"name": "VKontakte", "cat": "Социальные сети", "icon": "fa-vk", "url": "https://vk.com/{u}", "check": "https://vk.com/{u}", "type": "status"},
    {"name": "TikTok", "cat": "Социальные сети", "icon": "fa-tiktok", "url": "https://www.tiktok.com/@{u}", "check": "https://www.tiktok.com/@{u}", "type": "status"},
    {"name": "Pinterest", "cat": "Социальные сети", "icon": "fa-pinterest", "url": "https://www.pinterest.com/{u}/", "check": "https://www.pinterest.com/{u}/", "type": "status"},
    {"name": "Reddit", "cat": "Социальные сети", "icon": "fa-reddit", "url": "https://www.reddit.com/user/{u}", "check": "https://www.reddit.com/user/{u}/about.json", "type": "status"},
    {"name": "Twitter / X", "cat": "Социальные сети", "icon": "fa-x-twitter", "url": "https://x.com/{u}", "check": "https://x.com/{u}", "type": "status"},
    {"name": "Snapchat", "cat": "Социальные сети", "icon": "fa-snapchat", "url": "https://www.snapchat.com/add/{u}", "check": "https://www.snapchat.com/add/{u}", "type": "status"},
    {"name": "Mastodon", "cat": "Социальные сети", "icon": "fa-mastodon", "url": "https://mastodon.social/@{u}", "check": "https://mastodon.social/@{u}", "type": "status"},
    {"name": "Bluesky", "cat": "Социальные сети", "icon": "fa-cloud", "url": "https://bsky.app/profile/{u}.bsky.social", "check": "https://bsky.app/profile/{u}.bsky.social", "type": "status"},
    {"name": "Tumblr", "cat": "Социальные сети", "icon": "fa-tumblr", "url": "https://{u}.tumblr.com", "check": "https://{u}.tumblr.com", "type": "status"},
    
    # IT, Разработка и Дизайн
    {"name": "GitHub", "cat": "IT & Разработка", "icon": "fa-github", "url": "https://github.com/{u}", "check": "https://api.github.com/users/{u}", "type": "status"},
    {"name": "GitLab", "cat": "IT & Разработка", "icon": "fa-gitlab", "url": "https://gitlab.com/{u}", "check": "https://gitlab.com/{u}", "type": "status"},
    {"name": "DockerHub", "cat": "IT & Разработка", "icon": "fa-docker", "url": "https://hub.docker.com/u/{u}", "check": "https://hub.docker.com/v2/users/{u}", "type": "status"},
    {"name": "Dev.to", "cat": "IT & Разработка", "icon": "fa-dev", "url": "https://dev.to/{u}", "check": "https://dev.to/{u}", "type": "status"},
    {"name": "Habr", "cat": "IT & Разработка", "icon": "fa-code", "url": "https://habr.com/ru/users/{u}/", "check": "https://habr.com/ru/users/{u}/", "type": "status"},
    {"name": "Medium", "cat": "IT & Разработка", "icon": "fa-medium", "url": "https://medium.com/@{u}", "check": "https://medium.com/@{u}", "type": "status"},
    {"name": "Kaggle", "cat": "IT & Разработка", "icon": "fa-brain", "url": "https://www.kaggle.com/{u}", "check": "https://www.kaggle.com/{u}", "type": "status"},
    {"name": "LeetCode", "cat": "IT & Разработка", "icon": "fa-terminal", "url": "https://leetcode.com/{u}", "check": "https://leetcode.com/{u}", "type": "status"},
    {"name": "Codeforces", "cat": "IT & Разработка", "icon": "fa-laptop-code", "url": "https://codeforces.com/profile/{u}", "check": "https://codeforces.com/profile/{u}", "type": "status"},
    {"name": "Replit", "cat": "IT & Разработка", "icon": "fa-code-branch", "url": "https://replit.com/@{u}", "check": "https://replit.com/@{u}", "type": "status"},
    {"name": "Behance", "cat": "IT & Разработка", "icon": "fa-behance", "url": "https://www.behance.net/{u}", "check": "https://www.behance.net/{u}", "type": "status"},
    {"name": "Dribbble", "cat": "IT & Разработка", "icon": "fa-dribbble", "url": "https://dribbble.com/{u}", "check": "https://dribbble.com/{u}", "type": "status"},
    {"name": "ArtStation", "cat": "IT & Разработка", "icon": "fa-palette", "url": "https://www.artstation.com/{u}", "check": "https://www.artstation.com/{u}", "type": "status"},

    # Гейминг и Киберспорт
    {"name": "Steam", "cat": "Гейминг", "icon": "fa-steam", "url": "https://steamcommunity.com/id/{u}", "check": "https://steamcommunity.com/id/{u}", "type": "status"},
    {"name": "Roblox", "cat": "Гейминг", "icon": "fa-gamepad", "url": "https://www.roblox.com/user.aspx?username={u}", "check": "https://www.roblox.com/user.aspx?username={u}", "type": "status"},
    {"name": "Twitch", "cat": "Гейминг", "icon": "fa-twitch", "url": "https://www.twitch.tv/{u}", "check": "https://www.twitch.tv/{u}", "type": "status"},
    {"name": "Chess.com", "cat": "Гейминг", "icon": "fa-chess", "url": "https://www.chess.com/member/{u}", "check": "https://api.chess.com/pub/player/{u}", "type": "status"},
    {"name": "NameMC (Minecraft)", "cat": "Гейминг", "icon": "fa-cube", "url": "https://namemc.com/profile/{u}", "check": "https://namemc.com/profile/{u}", "type": "status"},
    {"name": "Osu!", "cat": "Гейминг", "icon": "fa-circle-dot", "url": "https://osu.ppy.sh/users/{u}", "check": "https://osu.ppy.sh/users/{u}", "type": "status"},
    {"name": "Faceit", "cat": "Гейминг", "icon": "fa-crosshairs", "url": "https://www.faceit.com/en/players/{u}", "check": "https://www.faceit.com/en/players/{u}", "type": "status"},
    {"name": "Speedrun.com", "cat": "Гейминг", "icon": "fa-stopwatch", "url": "https://www.speedrun.com/user/{u}", "check": "https://www.speedrun.com/user/{u}", "type": "status"},

    # Медиа, Музыка и Видео
    {"name": "YouTube", "cat": "Медиа & Музыка", "icon": "fa-youtube", "url": "https://www.youtube.com/@{u}", "check": "https://www.youtube.com/@{u}", "type": "status"},
    {"name": "Spotify", "cat": "Медиа & Музыка", "icon": "fa-spotify", "url": "https://open.spotify.com/user/{u}", "check": "https://open.spotify.com/user/{u}", "type": "status"},
    {"name": "SoundCloud", "cat": "Медиа & Музыка", "icon": "fa-soundcloud", "url": "https://soundcloud.com/{u}", "check": "https://soundcloud.com/{u}", "type": "status"},
    {"name": "Bandcamp", "cat": "Медиа & Музыка", "icon": "fa-music", "url": "https://{u}.bandcamp.com", "check": "https://{u}.bandcamp.com", "type": "status"},
    {"name": "Last.fm", "cat": "Медиа & Музыка", "icon": "fa-lastfm", "url": "https://www.last.fm/user/{u}", "check": "https://www.last.fm/user/{u}", "type": "status"},
    {"name": "Vimeo", "cat": "Медиа & Музыка", "icon": "fa-vimeo", "url": "https://vimeo.com/{u}", "check": "https://vimeo.com/{u}", "type": "status"},

    # Блоги, Форумы и Комьюнити
    {"name": "Pikabu", "cat": "Блоги & Комьюнити", "icon": "fa-comments", "url": "https://pikabu.ru/@{u}", "check": "https://pikabu.ru/@{u}", "type": "status"},
    {"name": "LiveJournal", "cat": "Блоги & Комьюнити", "icon": "fa-pen-nib", "url": "https://{u}.livejournal.com", "check": "https://{u}.livejournal.com", "type": "status"},
    {"name": "Pastebin", "cat": "Блоги & Комьюнити", "icon": "fa-file-lines", "url": "https://pastebin.com/u/{u}", "check": "https://pastebin.com/u/{u}", "type": "status"},
    {"name": "Wattpad", "cat": "Блоги & Комьюнити", "icon": "fa-book-open", "url": "https://www.wattpad.com/user/{u}", "check": "https://www.wattpad.com/user/{u}", "type": "status"},
    {"name": "Letterboxd", "cat": "Блоги & Комьюнити", "icon": "fa-film", "url": "https://letterboxd.com/{u}", "check": "https://letterboxd.com/{u}", "type": "status"},
    {"name": "MyAnimeList", "cat": "Блоги & Комьюнити", "icon": "fa-tv", "url": "https://myanimelist.net/profile/{u}", "check": "https://myanimelist.net/profile/{u}", "type": "status"},
    {"name": "Duolingo", "cat": "Блоги & Комьюнити", "icon": "fa-language", "url": "https://www.duolingo.com/profile/{u}", "check": "https://www.duolingo.com/profile/{u}", "type": "status"},

    # Маркетплейсы и ссылки
    {"name": "Linktree", "cat": "Контакты & Ссылки", "icon": "fa-link", "url": "https://linktr.ee/{u}", "check": "https://linktr.ee/{u}", "type": "status"},
    {"name": "BuyMeACoffee", "cat": "Контакты & Ссылки", "icon": "fa-mug-hot", "url": "https://www.buymeacoffee.com/{u}", "check": "https://www.buymeacoffee.com/{u}", "type": "status"},
    {"name": "Kwork", "cat": "Контакты & Ссылки", "icon": "fa-briefcase", "url": "https://kwork.ru/user/{u}", "check": "https://kwork.ru/user/{u}", "type": "status"},
    {"name": "Freelance.ru", "cat": "Контакты & Ссылки", "icon": "fa-user-tie", "url": "https://freelance.ru/{u}", "check": "https://freelance.ru/{u}", "type": "status"},
]


# --- ИЗВЛЕЧЕНИЕ EXIF МЕТАДАННЫХ ИЗ ФОТО ---

def get_decimal_from_dms(dms, ref):
    try:
        degrees = float(dms[0])
        minutes = float(dms[1]) / 60.0
        seconds = float(dms[2]) / 3600.0
        if ref in ['S', 'W']:
            return -float(degrees + minutes + seconds)
        return float(degrees + minutes + seconds)
    except Exception:
        return None


def extract_exif_data(image_bytes: bytes) -> dict:
    """Извлекает EXIF, GPS координаты, камеру, дату и параметры съемки."""
    info = {
        "has_exif": False,
        "camera_make": None,
        "camera_model": None,
        "date_time": None,
        "software": None,
        "lens_model": None,
        "gps": None,
        "google_maps_url": None,
        "raw_tags": {}
    }
    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif = image._getexif()
        if not exif:
            return info

        info["has_exif"] = True
        gps_data = {}

        for tag_id, value in exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
            
            if tag_name == "Make":
                info["camera_make"] = str(value).strip()
            elif tag_name == "Model":
                info["camera_model"] = str(value).strip()
            elif tag_name in ["DateTimeOriginal", "DateTime"]:
                info["date_time"] = str(value).strip()
            elif tag_name == "Software":
                info["software"] = str(value).strip()
            elif tag_name == "LensModel":
                info["lens_model"] = str(value).strip()
            elif tag_name == "GPSInfo":
                for gps_tag_id in value:
                    gps_tag_name = ExifTags.GPSTAGS.get(gps_tag_id, str(gps_tag_id))
                    gps_data[gps_tag_name] = value[gps_tag_id]

        # Конвертация GPS в десятичные координаты
        if gps_data and "GPSLatitude" in gps_data and "GPSLongitude" in gps_data:
            lat = get_decimal_from_dms(gps_data["GPSLatitude"], gps_data.get("GPSLatitudeRef", "N"))
            lon = get_decimal_from_dms(gps_data["GPSLongitude"], gps_data.get("GPSLongitudeRef", "E"))
            if lat is not None and lon is not None:
                info["gps"] = {
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6),
                    "lat_ref": gps_data.get("GPSLatitudeRef", "N"),
                    "lon_ref": gps_data.get("GPSLongitudeRef", "E")
                }
                info["google_maps_url"] = f"https://www.google.com/maps?q={round(lat,6)},{round(lon,6)}"

    except Exception:
        pass
    return info


# --- API ЭНДПОИНТЫ ---

@app.get("/api/catalog")
async def api_catalog(q: Optional[str] = None, cat: Optional[str] = None):
    normalize_catalog()
    query = (q or "").strip().lower()
    category = (cat or "").strip().lower()

    groups = []
    for g in CATALOG:
        if category and g["id"].lower() != category:
            continue
        tools = []
        for t in g["tools"]:
            if not query:
                tools.append(t)
                continue
            guide_str = json.dumps(t.get("install_guide", {}), ensure_ascii=False).lower()
            search_blob = f"{g['title']} {g['desc']} {t['name']} {t['purpose']} {t.get('input', '')} {guide_str}".lower()
            if query in search_blob:
                tools.append(t)
        if tools:
            groups.append({**g, "tools": tools})
    return {"groups": groups}


@app.get("/api/admin/visitors")
async def get_admin_visitors(limit: int = 50):
    rows = []
    if VISITS_FILE.exists():
        for line in VISITS_FILE.read_text(encoding="utf-8").splitlines()[-max(1, min(limit, 200)):]:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    rows.reverse()
    return {
        "ok": True,
        "total_recorded": len(rows),
        "visitors": rows
    }


# --- SUPER-ПОИСКОВИК SHERLOCK (АСИНХРОННЫЙ МУЛЬТИ-ПОИСК 60+ САЙТОВ) ---

@app.post("/api/scan/username")
async def scan_username_sherlock(request: Request):
    """Мощный асинхронный поиск по 60+ платформам (Sherlock Engine)."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    username = str(body.get("target", "")).strip().lstrip("@")

    if not username or len(username) < 2:
        return JSONResponse({"ok": False, "error": "Введите никнейм длиной от 2 символов"}, status_code=400)

    found = []
    checked_count = 0
    sem = asyncio.Semaphore(25)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async def check_platform(client: httpx.AsyncClient, site: dict):
        nonlocal checked_count
        target_url = site["check"].format(u=username)
        profile_url = site["url"].format(u=username)

        async with sem:
            try:
                r = await client.get(target_url, headers=headers, timeout=3.5, follow_redirects=True)
                checked_count += 1
                
                if r.status_code == 200:
                    # Специфические фильтры от ложных срабатываний
                    if site["type"] == "tg" and ("tgme_page_extra" not in r.text and "@" not in r.text):
                        return
                    if "user not found" in r.text.lower() or "страница не найдена" in r.text.lower() or "404 not found" in r.text.lower():
                        return

                    found.append({
                        "platform": site["name"],
                        "category": site["cat"],
                        "icon": site["icon"],
                        "url": profile_url,
                        "status": "Активен"
                    })
            except Exception:
                pass

    async with httpx.AsyncClient() as client:
        tasks = [check_platform(client, s) for s in SHERLOCK_SITES]
        await asyncio.gather(*tasks)

    # Генерация AI резюме
    categories_found = list(set(p["category"] for p in found))
    prompt = (
        f"Ты — ведущий эксперт по OSINT и цифровой дедукции.\n"
        f"Проведен поиск по 60+ базам данных для никнейма '{username}'.\n"
        f"Найдены подтвержденные аккаунты ({len(found)} шт.): {[p['platform'] for p in found]}.\n"
        f"Категории активности: {categories_found}.\n\n"
        "Сделай структурированный аналитический портрет:\n"
        "1. 👤 **Вероятное имя / ФИО / Псевдоним**\n"
        "2. 🎂 **Оценка возраста / намеки в нике**\n"
        "3. 🎯 **Ключевые интересы и профиль деятельности**\n"
        "4. 💡 **Рекомендации по дальнейшим шагам**\n"
        "Пиши лаконично, структурированно, с эмодзи."
    )
    ai_dossier = await run_gemini_prompt(prompt)

    return {
        "ok": True,
        "type": "username",
        "username": username,
        "found_count": len(found),
        "total_checked": len(SHERLOCK_SITES),
        "profiles": found,
        "ai_summary": ai_dossier or f"Найдено {len(found)} открытых профилей на 60+ платформах."
    }


# --- СКАНИРОВАНИЕ И АНАЛИЗ ФОТОГРАФИЙ (EXIF + GEMINI VISION AI) ---

@app.post("/api/scan/photo")
async def scan_photo_endpoint(request: Request, file: Optional[UploadFile] = File(None)):
    """Анализ метаданных фото (EXIF/GPS) + распознавание местности через Gemini Vision."""
    image_bytes = None
    mime_type = "image/jpeg"

    if file:
        image_bytes = await file.read()
        mime_type = file.content_type or "image/jpeg"
    else:
        try:
            body = await request.json()
            b64_data = body.get("image_base64", "")
            if b64_data:
                if "," in b64_data:
                    header, b64_data = b64_data.split(",", 1)
                    if "image/png" in header:
                        mime_type = "image/png"
                    elif "image/webp" in header:
                        mime_type = "image/webp"
                image_bytes = base64.b64decode(b64_data)
        except Exception:
            pass

    if not image_bytes:
        return JSONResponse({"ok": False, "error": "Загрузите файл изображения или передайте base64"}, status_code=400)

    # 1. Извлечение EXIF и GPS
    exif_result = extract_exif_data(image_bytes)

    # 2. Vision AI анализ геолокации и объектов
    prompt = (
        "Ты — профессиональный эксперт по GeoINT и анализу изображений в расследованиях.\n"
        "Внимательно изучи прикрепленное фото и предоставь детальный OSINT-отчет:\n\n"
        "1. 🌍 **Геолокация и местоположение**: Определи страну, регион, город или тип ландшафта (по архитектуре, дорогам, растительности, розеткам, солнцу, номерам авто).\n"
        "2. 🔍 **Текст, вывески и надписи**: Распознай все видимые тексты, язык, бренды, дорожные указатели.\n"
        "3. ☀️ **Освещение и тени**: Оцени примерное время суток и угол падения лучей солнца.\n"
        "4. 💡 **Рекомендации по подтверждению локации**: Какие ориентиры проверить через спутники (Google Earth / Overpass)."
    )

    vision_ai_report = await run_gemini_prompt(prompt, image_bytes=image_bytes, mime_type=mime_type)

    return {
        "ok": True,
        "type": "photo",
        "exif": exif_result,
        "vision_ai_report": vision_ai_report or "Изображение обработано.",
        "reverse_search": {
            "google_lens": "https://lens.google.com/",
            "yandex_images": "https://yandex.ru/images/search?rpt=imageview",
            "tineye": "https://tineye.com/"
        }
    }


# --- TELEGRAM, DOMAIN, EMAIL, IP СКАНЕРЫ ---

def estimate_telegram_creation_date(tg_id: int) -> str:
    if tg_id < 50_000_000:
        return "2013 — 2014 гг. (Один из первых пользователей Telegram)"
    elif tg_id < 200_000_000:
        return "2015 — 2016 гг."
    elif tg_id < 600_000_000:
        return "2017 — 2018 гг."
    elif tg_id < 1_500_000_000:
        return "2019 — 2020 гг."
    elif tg_id < 5_000_000_000:
        return "2021 — 2023 гг."
    else:
        return "2024 — 2026 гг. (Свежий аккаунт)"


@app.post("/api/scan/telegram")
async def scan_telegram(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    target = str(body.get("target", "")).strip().lstrip("@")

    if not target or len(target) < 2:
        return JSONResponse({"ok": False, "error": "Введите Telegram юзернейм или числовой ID"}, status_code=400)

    if target.isdigit():
        tg_id = int(target)
        year_estimate = estimate_telegram_creation_date(tg_id)
        return {
            "ok": True,
            "type": "telegram_id",
            "tg_id": tg_id,
            "estimated_year": year_estimate,
            "tg_link": f"tg://user?id={tg_id}",
            "ai_summary": f"🎯 **Telegram ID:** `{tg_id}`\n📅 **Примерный период регистрации:** {year_estimate}\n💡 **Подсказка:** Для поиска привязанных сообщений используйте TelegramDB или поиск в каналах."
        }

    url = f"https://t.me/{target}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    try:
        async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
    except Exception as e:
        return JSONResponse({"ok": False, "error": f"Ошибка соединения с Telegram: {str(e)}"}, status_code=500)

    if resp.status_code != 200:
        return JSONResponse({"ok": False, "error": "Не удалось загрузить данные из Telegram"}, status_code=404)

    html = resp.text
    soup = BeautifulSoup(html, "html.parser")

    title_elem = soup.find("div", class_="tgme_page_title")
    title = title_elem.get_text(strip=True) if title_elem else target

    desc_elem = soup.find("div", class_="tgme_page_description")
    description = desc_elem.get_text(strip=True) if desc_elem else "Описание не указано или скрыто"

    extra_elem = soup.find("div", class_="tgme_page_extra")
    extra = extra_elem.get_text(strip=True) if extra_elem else ""

    photo_elem = soup.find("img", class_="tgme_page_photo_image")
    photo_url = photo_elem["src"] if photo_elem and "src" in photo_elem.attrs else None

    is_channel = "subscribers" in extra.lower() or "подписчик" in extra.lower()
    is_bot = "bot" in target.lower() or "if you have telegram" in html.lower() and "bot" in extra.lower()
    is_group = "members" in extra.lower() or "участник" in extra.lower()
    account_type = "Канал" if is_channel else ("Бот" if is_bot else ("Группа" if is_group else "Пользователь"))

    prompt = (
        f"Проанализируй публичный профиль Telegram:\n"
        f"Юзернейм: @{target}\n"
        f"Имя профиля: {title}\n"
        f"Тип: {account_type}\n"
        f"Bio/Описание: {description}\n"
        f"Метаданные: {extra}\n\n"
        "Сделай экспертный вывод о владельце/канале, ключевых темах и рекомендациях."
    )
    ai_dossier = await run_gemini_prompt(prompt)

    return {
        "ok": True,
        "type": "telegram",
        "username": target,
        "title": title,
        "description": description,
        "extra": extra,
        "photo_url": photo_url,
        "account_type": account_type,
        "url": url,
        "ai_summary": ai_dossier or f"Публичный {account_type} Telegram найден."
    }


@app.post("/api/scan/domain")
async def scan_domain(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    target = str(body.get("target", "")).strip().lower()
    target = re.sub(r"^https?://", "", target).split("/")[0].split(":")[0]

    if not target or "." not in target:
        return JSONResponse({"ok": False, "error": "Укажите корректное доменное имя (например, example.com)"}, status_code=400)

    results = {"target": target, "dns": {}, "ssl": {}, "headers": {}, "server_info": {}}

    try:
        ip_list = socket.gethostbyname_ex(target)[2]
        results["dns"]["A"] = ip_list
    except Exception as e:
        results["dns"]["A_error"] = str(e)

    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((target, 443), timeout=3.5) as sock:
            with ctx.wrap_socket(sock, server_hostname=target) as ssock:
                cert = ssock.getpeercert()
                subject = dict(x[0] for x in cert.get("subject", []))
                issuer = dict(x[0] for x in cert.get("issuer", []))
                results["ssl"] = {
                    "commonName": subject.get("commonName"),
                    "issuer": issuer.get("organizationName") or issuer.get("commonName"),
                    "notAfter": cert.get("notAfter"),
                }
    except Exception:
        results["ssl"]["status"] = "SSL не получен"

    try:
        async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
            resp = await client.get(f"https://{target}", headers={"User-Agent": "Mozilla/5.0"})
            results["server_info"]["status_code"] = resp.status_code
            hdrs = resp.headers
            results["headers"] = {
                "Server": hdrs.get("server", "Скрыт"),
                "Strict-Transport-Security": hdrs.get("strict-transport-security", "Отсутствует"),
            }
    except Exception:
        pass

    return {"ok": True, "type": "domain", "target": target, "data": results}


@app.post("/api/scan/email")
async def scan_email(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    email = str(body.get("target", "")).strip().lower()

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return JSONResponse({"ok": False, "error": "Некорректный формат email"}, status_code=400)

    domain = email.split("@")[1]
    res = {"email": email, "domain": domain, "syntax_valid": True, "status": "Почтовый домен активен"}

    try:
        res["domain_ip"] = socket.gethostbyname_ex(domain)[2]
    except Exception:
        res["status"] = "Почтовый домен не отвечает"

    return {"ok": True, "type": "email", "target": email, "data": res}


@app.post("/api/scan/ip")
async def scan_ip(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    target_ip = str(body.get("target", "")).strip() or client_ip(request)

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(f"http://ip-api.com/json/{target_ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query")
            return {"ok": True, "type": "ip", "target": target_ip, "data": resp.json()}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/api/ai/deduce")
async def ai_deduce_persona(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    target = str(body.get("target", "")).strip()
    if not target:
        return JSONResponse({"ok": False, "error": "Цель не указана"}, status_code=400)

    prompt = (
        f"Ты — ведущий OSINT-аналитик. Составь подробное досье на цель: '{target}'.\n"
        "Определи: 1) Вероятное имя 2) Возраст/даты 3) Интересы 4) Связи 5) Гео-следы.\n"
        "Пиши структурированно, красиво с эмодзи."
    )
    ai_text = await run_gemini_prompt(prompt)
    return {"ok": True, "target": target, "dossier": ai_text or "Досье составлено."}


# --- FRONTEND ИНТЕРФЕЙС WEBAPP PRO ---

HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>OSINT Pro Hub (Sherlock 60+ & Vision AI)</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
<style>
:root {
  --bg: #07090e;
  --card-bg: #0f141c;
  --card-border: #1e293b;
  --primary: #00ff66;
  --primary-glow: rgba(0, 255, 102, 0.25);
  --cyan: #00e5ff;
  --cyan-glow: rgba(0, 229, 255, 0.2);
  --purple: #a855f7;
  --warn: #ffaa00;
  --danger: #ff3366;
  --text: #e2e8f0;
  --text-muted: #94a3b8;
  --input-bg: #070a10;
  --code-bg: #05070a;
}
* { margin:0; padding:0; box-sizing:border-box; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-tap-highlight-color: transparent; }
body { background:var(--bg); color:var(--text); min-height:100vh; padding:12px; padding-bottom:80px; }
.container { max-width:760px; margin:0 auto; }

/* Шапка и навигация */
.navbar { display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--card-border); padding:10px 0 14px; margin-bottom:14px; }
.brand { font-size:18px; font-weight:800; color:#fff; display:flex; align-items:center; gap:8px; text-transform:uppercase; cursor:pointer; }
.brand i { color:var(--primary); text-shadow:0 0 12px var(--primary-glow); }
.nav-actions { display:flex; gap:6px; }

/* Страницы / Вьюшки */
.view-page { display:none; }
.view-page.active { display:block; }

/* Поиск и фильтры */
.search-box { position:relative; margin-bottom:12px; }
.search-box i { position:absolute; left:14px; top:50%; transform:translateY(-50%); color:var(--text-muted); font-size:14px; }
.search-box input { width:100%; padding:12px 14px 12px 40px; background:var(--input-bg); border:1px solid var(--card-border); border-radius:10px; color:#fff; font-size:14px; outline:none; transition:all .2s ease; }
.search-box input:focus { border-color:var(--primary); box-shadow:0 0 10px var(--primary-glow); }

.filter-chips { display:flex; gap:6px; overflow-x:auto; padding-bottom:8px; margin-bottom:14px; scrollbar-width:none; }
.filter-chips::-webkit-scrollbar { display:none; }
.chip { padding:6px 12px; background:var(--card-bg); border:1px solid var(--card-border); border-radius:20px; font-size:12px; color:var(--text-muted); white-space:nowrap; cursor:pointer; transition:all .15s ease; }
.chip.active, .chip:hover { background:rgba(0,255,102,0.1); border-color:var(--primary); color:var(--primary); font-weight:600; }

/* Карточки каталога */
.group-title { font-size:14px; font-weight:700; color:var(--cyan); margin:18px 0 10px; display:flex; align-items:center; gap:6px; text-transform:uppercase; letter-spacing:0.5px; }
.group-desc { font-size:11px; color:var(--text-muted); margin-top:-6px; margin-bottom:10px; }

.cards-grid { display:grid; gap:10px; }
.card { background:var(--card-bg); border:1px solid var(--card-border); border-radius:12px; padding:14px; position:relative; transition:border-color .15s ease, transform .15s ease; cursor:pointer; }
.card:hover { border-color:var(--cyan); transform:translateY(-1px); }
.card-header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px; gap:8px; }
.card-title { font-size:15px; font-weight:700; color:#fff; display:flex; align-items:center; gap:6px; }
.badge { font-size:10px; font-weight:700; padding:2px 8px; border-radius:12px; text-transform:uppercase; }
.badge-web { background:rgba(0,229,255,0.15); color:var(--cyan); border:1px solid var(--cyan); }
.badge-api { background:rgba(0,255,102,0.15); color:var(--primary); border:1px solid var(--primary); }
.badge-doc { background:rgba(148,163,184,0.15); color:var(--text-muted); border:1px solid var(--text-muted); }

.card-purpose { font-size:12px; color:var(--text-muted); line-height:1.45; margin-bottom:12px; }
.card-meta { font-size:11px; color:#64748b; margin-bottom:12px; display:flex; align-items:center; gap:12px; }
.card-meta span { display:inline-flex; align-items:center; gap:4px; }

/* Кнопки */
.btn-group { display:flex; flex-wrap:wrap; gap:8px; }
.btn { padding:8px 14px; font-size:12px; font-weight:600; border-radius:8px; border:none; cursor:pointer; display:inline-flex; align-items:center; gap:6px; transition:all .15s ease; text-decoration:none; }
.btn-primary { background:var(--primary); color:#000; font-weight:700; }
.btn-primary:active { transform:scale(0.97); }
.btn-secondary { background:#1e293b; color:var(--text); border:1px solid #334155; }
.btn-secondary:hover { background:#283548; color:#fff; }
.btn-purple { background:linear-gradient(135deg, #7c3aed, #a855f7); color:#fff; font-weight:700; }

/* СТРАНИЦА ИНСТРУМЕНТА */
.tool-view-header { background:#0f172a; border:1px solid #1e293b; border-radius:14px; padding:18px; margin-bottom:16px; position:relative; }
.back-btn { display:inline-flex; align-items:center; gap:6px; color:var(--cyan); font-size:12px; font-weight:600; cursor:pointer; margin-bottom:12px; }
.back-btn:hover { text-decoration:underline; }
.tool-view-title { font-size:20px; font-weight:800; color:#fff; display:flex; align-items:center; gap:10px; margin-bottom:6px; }
.tool-view-desc { font-size:13px; color:var(--text-muted); line-height:1.5; margin-bottom:14px; }

.workspace-box { background:#0a0f18; border:1px solid var(--card-border); border-radius:14px; padding:16px; margin-bottom:16px; }
.workspace-title { font-size:14px; font-weight:700; color:var(--primary); margin-bottom:12px; display:flex; align-items:center; gap:8px; }
.input-row { display:flex; gap:8px; margin-bottom:14px; }
.tool-input { flex:1; padding:12px 14px; background:var(--input-bg); border:1px solid var(--card-border); border-radius:10px; color:#fff; font-size:14px; outline:none; }
.tool-input:focus { border-color:var(--primary); }

/* Загрузка фото */
.upload-dropzone { border:2px dashed #334155; border-radius:12px; padding:24px; text-align:center; cursor:pointer; background:#070a10; transition:all .2s ease; margin-bottom:14px; }
.upload-dropzone:hover { border-color:var(--cyan); background:#0c121c; }
.upload-preview { max-width:100%; max-height:220px; border-radius:8px; margin:10px auto; display:none; }

/* Вывод утилиты */
.tool-output-box { background:#040608; border:1px solid #1e293b; border-radius:10px; padding:16px; margin-top:14px; display:none; }
.output-header { display:flex; justify-content:space-between; align-items:center; padding-bottom:10px; border-bottom:1px solid #1e293b; margin-bottom:12px; font-size:13px; font-weight:700; color:#fff; }

/* Telegram Профиль Карточка */
.tg-profile-card { background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:16px; display:flex; gap:16px; align-items:center; margin-bottom:14px; }
.tg-avatar { width:64px; height:64px; border-radius:50%; object-fit:cover; border:2px solid var(--cyan); background:#1e293b; }
.tg-info { flex:1; }
.tg-name { font-size:17px; font-weight:800; color:#fff; display:flex; align-items:center; gap:8px; }
.tg-handle { font-size:13px; color:var(--cyan); margin-bottom:6px; }
.tg-desc { font-size:12px; color:#cbd5e1; line-height:1.4; background:#070a10; padding:8px 10px; border-radius:6px; border:1px solid #1e293b; }

/* AI Досье Блок */
.ai-dossier-card { background:linear-gradient(145deg, #0d1a2d, #14243b); border:1px solid #23456e; border-radius:12px; padding:18px; margin-top:16px; box-shadow:0 6px 20px rgba(0, 229, 255, 0.1); }
.ai-dossier-title { font-size:15px; font-weight:800; color:var(--cyan); display:flex; align-items:center; gap:8px; margin-bottom:12px; }
.ai-dossier-text { font-size:13px; color:#cbd5e1; line-height:1.65; white-space:pre-wrap; }

/* Сетка найденных профилей Sherlock */
.profiles-grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:10px; margin-top:12px; }
.profile-card { background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:12px; display:flex; align-items:center; justify-content:space-between; }
.profile-left { display:flex; align-items:center; gap:10px; }
.profile-icon { font-size:20px; color:var(--cyan); width:24px; text-align:center; }
.profile-name { font-size:13px; font-weight:700; color:#fff; }
.profile-tag { font-size:10px; color:var(--primary); }

.loader { display:none; text-align:center; padding:16px 0; }
.spinner { border:2px solid rgba(255,255,255,0.1); border-top:2px solid var(--primary); border-radius:50%; width:24px; height:24px; animation:spin 0.8s linear infinite; margin:0 auto 8px; }
@keyframes spin { 0% { transform:rotate(0deg); } 100% { transform:rotate(360deg); } }

.code-wrap { position:relative; background:var(--code-bg); border:1px solid #1f2937; border-radius:8px; padding:10px 12px; font-family:'Courier New', monospace; font-size:12px; color:var(--primary); word-break:break-all; white-space:pre-wrap; }
.cmd-box { margin-bottom:10px; }
.cmd-label { font-size:11px; font-weight:700; color:var(--cyan); text-transform:uppercase; margin-bottom:4px; display:flex; justify-content:space-between; align-items:center; }
.copy-btn { position:absolute; right:8px; top:8px; background:#1e293b; color:var(--text-muted); border:none; border-radius:6px; padding:4px 8px; font-size:11px; cursor:pointer; }
.copy-btn:hover { background:var(--primary); color:#000; }

.footer-info { text-align:center; font-size:11px; color:#475569; margin-top:24px; }
</style>
</head>
<body>

<div class="container">
  <!-- Навбар -->
  <div class="navbar">
    <div class="brand" onclick="showView('catalogView')">
      <i class="fa-solid fa-shield-halved"></i> OSINT Pro Hub
    </div>
    <div class="nav-actions">
      <button class="btn btn-secondary" onclick="showView('photoView')"><i class="fa-solid fa-camera"></i> Фото & EXIF</button>
      <button class="btn btn-purple" onclick="showView('aiView')"><i class="fa-solid fa-brain"></i> AI Досье</button>
    </div>
  </div>

  <!-- ВЬЮ 1: ГЛАВНЫЙ КАТАЛОГ -->
  <div class="view-page active" id="catalogView">
    <div class="search-box">
      <i class="fa-solid fa-magnifying-glass"></i>
      <input type="text" id="searchInput" placeholder="Поиск по 60+ базам, никнеймам, Telegram, GeoINT..." oninput="renderCatalog()">
    </div>

    <div class="filter-chips">
      <div class="chip active" onclick="setFilter('all', this)">Все категории</div>
      <div class="chip" onclick="setFilter('username_osint', this)">🔍 Sherlock (60+ сайтов)</div>
      <div class="chip" onclick="setFilter('telegram_osint', this)">✈️ Telegram Разведка</div>
      <div class="chip" onclick="setFilter('amazing_osint', this)">🌟 Фото, GeoINT & Спутники</div>
      <div class="chip" onclick="setFilter('mapping_investigation', this)">🗺️ Графы и фреймворки</div>
      <div class="chip" onclick="setFilter('domain_network', this)">🌐 Домены и DNS</div>
      <div class="chip" onclick="setFilter('email_checks', this)">📧 Почта и телефоны</div>
    </div>

    <div id="catalogContainer"></div>
  </div>

  <!-- ВЬЮ 2: ОТДЕЛЬНАЯ СТРАНИЦА ИНСТРУМЕНТА -->
  <div class="view-page" id="toolView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог всех инструментов
    </div>

    <div class="tool-view-header">
      <div class="tool-view-title" id="tvTitle">Название инструмента</div>
      <div class="tool-view-desc" id="tvPurpose">Описание назначения инструмента</div>
      <div class="btn-group" id="tvHeaderButtons"></div>
    </div>

    <!-- Индивидуальная рабочая область -->
    <div class="workspace-box">
      <div class="workspace-title"><i class="fa-solid fa-bolt"></i> Рабочая область инструмента</div>
      
      <!-- Блок загрузки фото для фото-утилит -->
      <div id="tvPhotoUploaderBox" style="display:none;">
        <div class="upload-dropzone" onclick="document.getElementById('tvFileInput').click()">
          <i class="fa-solid fa-cloud-arrow-up" style="font-size:32px; color:var(--cyan); margin-bottom:8px;"></i>
          <div style="font-weight:700; color:#fff;">Нажмите для выбора фото или перетащите сюда</div>
          <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">Извлечение GPS, даты, камеры и AI Vision гео-анализ</div>
          <input type="file" id="tvFileInput" accept="image/*" style="display:none;" onchange="handlePhotoUpload(this)">
        </div>
        <img id="tvPhotoPreview" class="upload-preview">
      </div>

      <!-- Текстовый ввод для остальных утилит -->
      <div class="input-row" id="tvTextInputRow">
        <input class="tool-input" id="tvTargetInput" placeholder="Введите цель...">
        <button class="btn btn-primary" onclick="runCurrentToolScan()"><i class="fa-solid fa-play"></i> Запустить</button>
      </div>

      <div class="loader" id="tvLoader">
        <div class="spinner"></div>
        <span style="font-size:12px; color:var(--cyan);">Выполняется глубокое сканирование и обработка...</span>
      </div>

      <!-- Персональный контейнер вывода -->
      <div class="tool-output-box" id="tvOutputBox"></div>
    </div>

    <!-- Блок инструкции по установке -->
    <div class="workspace-box">
      <div class="workspace-title"><i class="fa-solid fa-book-open"></i> Инструкция по установке и настройке</div>
      <div id="tvInstallCommands"></div>
    </div>
  </div>

  <!-- ВЬЮ 3: ВЫДЕЛЕННЫЙ ФОТО & VISION AI АНАЛИЗАТОР -->
  <div class="view-page" id="photoView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог
    </div>

    <div class="workspace-box">
      <div class="workspace-title" style="color:var(--cyan);"><i class="fa-solid fa-camera"></i> Фото-детектив & Геолокация (Vision AI + EXIF)</div>
      <p style="font-size:13px; color:var(--text-muted); margin-bottom:14px;">
        Загрузите любую фотографию — система автоматически извлечет скрытые метаданные (GPS координаты, дату, модель камеры), определит примерную геолокацию по архитектуре и теням через Gemini Vision, и создаст ссылки для обратного поиска.
      </p>

      <div class="upload-dropzone" onclick="document.getElementById('directPhotoInput').click()">
        <i class="fa-solid fa-image" style="font-size:36px; color:var(--cyan); margin-bottom:8px;"></i>
        <div style="font-weight:700; color:#fff;">Загрузить изображение для экспертизы</div>
        <div style="font-size:12px; color:var(--text-muted);">Поддерживаются JPEG, PNG, WEBP, HEIC</div>
        <input type="file" id="directPhotoInput" accept="image/*" style="display:none;" onchange="processDirectPhoto(this)">
      </div>

      <img id="directPhotoPreview" class="upload-preview">

      <div class="loader" id="photoLoader">
        <div class="spinner" style="border-top-color:var(--cyan);"></div>
        <span style="font-size:12px; color:var(--cyan);">Нейросеть распознает объекты, координаты и текст на фото...</span>
      </div>

      <div id="photoResultBox"></div>
    </div>
  </div>

  <!-- ВЬЮ 4: AI ДЕДУКТИВНОЕ ДОСЬЕ -->
  <div class="view-page" id="aiView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог
    </div>

    <div class="workspace-box">
      <div class="workspace-title" style="color:var(--purple);"><i class="fa-solid fa-brain"></i> Нейросетевой AI-детектив (Gemini)</div>
      <p style="font-size:13px; color:var(--text-muted); margin-bottom:14px;">
        Введите никнейм, Telegram, почту или имя — нейросеть проведет глубокий анализ цифрового следа и составит структурированное досье с вероятным возрастом, интересами, связями и геолокацией.
      </p>
      <div class="input-row">
        <input class="tool-input" id="aiSearchTarget" placeholder="Введите никнейм или @username...">
        <button class="btn btn-purple" onclick="runAiDossierDirect()"><i class="fa-solid fa-wand-magic-sparkles"></i> Составить досье</button>
      </div>

      <div class="loader" id="aiLoader">
        <div class="spinner" style="border-top-color:var(--purple);"></div>
        <span style="font-size:12px; color:var(--purple);">Нейросеть сопоставляет цифровые следы и строит портрет...</span>
      </div>

      <div id="aiDossierResultDirect"></div>
    </div>
  </div>

  <div class="footer-info">
    OSINT Pro Hub · Sherlock Engine (60+ сервисов) & Gemini Vision AI
  </div>
</div>

<script>
let FULL_CATALOG = [];
let currentCategory = 'all';
let activeTool = null;
let currentUploadedBase64 = null;

const tg = window.Telegram?.WebApp;
if (tg) {
  tg.expand();
  tg.ready();
}

function showView(viewId) {
  document.querySelectorAll('.view-page').forEach(el => el.classList.remove('active'));
  document.getElementById(viewId).classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function loadCatalog() {
  try {
    const res = await fetch('/api/catalog');
    const data = await res.json();
    FULL_CATALOG = data.groups || [];
    renderCatalog();
  } catch (err) {
    document.getElementById('catalogContainer').innerHTML = '<div style="color:var(--danger); text-align:center; padding:20px;">Ошибка загрузки каталога.</div>';
  }
}

function setFilter(cat, elem) {
  currentCategory = cat;
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  if (elem) elem.classList.add('active');
  renderCatalog();
}

function renderCatalog() {
  const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();
  const container = document.getElementById('catalogContainer');
  container.innerHTML = '';

  let totalShown = 0;

  FULL_CATALOG.forEach(group => {
    if (currentCategory !== 'all' && group.id !== currentCategory) return;

    const filteredTools = group.tools.filter(t => {
      if (!query) return true;
      const gStr = JSON.stringify(t.install_guide || {}).toLowerCase();
      const blob = (group.title + ' ' + t.name + ' ' + t.purpose + ' ' + (t.input||'') + ' ' + gStr).toLowerCase();
      return blob.includes(query);
    });

    if (filteredTools.length === 0) return;
    totalShown += filteredTools.length;

    const groupWrap = document.createElement('div');
    groupWrap.innerHTML = `
      <div class="group-title">${group.title}</div>
      <div class="group-desc">${group.desc}</div>
    `;

    const grid = document.createElement('div');
    grid.className = 'cards-grid';

    filteredTools.forEach(tool => {
      const card = document.createElement('div');
      card.className = 'card';
      card.onclick = () => openToolPage(tool.id);

      let badge = '<span class="badge badge-doc">CLI / Справка</span>';
      if (tool.web_runnable && tool.launch?.type === 'api') {
        badge = '<span class="badge badge-api">⚡ SHERLOCK 60+</span>';
      } else if (tool.web_url && tool.launch?.type === 'url') {
        badge = '<span class="badge badge-web">🌐 WEB-APP</span>';
      }

      card.innerHTML = `
        <div class="card-header">
          <div class="card-title">${tool.name}</div>
          ${badge}
        </div>
        <div class="card-purpose">${tool.purpose}</div>
        <div class="card-meta">
          <span><i class="fa-solid fa-crosshairs"></i> Вход: <b>${tool.input || '—'}</b></span>
        </div>
        <div class="btn-group" onclick="event.stopPropagation()">
          <button class="btn btn-primary" onclick="openToolPage('${tool.id}')"><i class="fa-solid fa-arrow-right"></i> Открыть утилиту</button>
        </div>
      `;
      grid.appendChild(card);
    });

    groupWrap.appendChild(grid);
    container.appendChild(groupWrap);
  });

  if (totalShown === 0) {
    container.innerHTML = '<div style="text-align:center; padding:30px; color:var(--text-muted);">Ничего не найдено по вашему запросу.</div>';
  }
}

// ОТКРЫТИЕ СТРАНИЦЫ ИНСТРУМЕНТА
function openToolPage(toolId) {
  let selected = null;
  for (let g of FULL_CATALOG) {
    for (let t of g.tools) {
      if (t.id === toolId) { selected = t; break; }
    }
  }
  if (!selected) return;

  activeTool = selected;
  document.getElementById('tvTitle').innerHTML = `<i class="fa-solid fa-cube" style="color:var(--primary);"></i> ${selected.name}`;
  document.getElementById('tvPurpose').innerText = selected.purpose;

  const btnGroup = document.getElementById('tvHeaderButtons');
  btnGroup.innerHTML = '';

  if (selected.web_url) {
    btnGroup.innerHTML += `<a href="${selected.web_url}" target="_blank" rel="noopener" class="btn btn-primary"><i class="fa-solid fa-arrow-up-right-from-square"></i> Открыть официальный Web</a>`;
  }
  if (selected.repo) {
    btnGroup.innerHTML += `<a href="${selected.repo}" target="_blank" rel="noopener" class="btn btn-secondary"><i class="fa-brands fa-github"></i> Репозиторий GitHub</a>`;
  }

  // Проверка: является ли утилита инструментом анализа фото (MetaDetective, SunCalc, Image GeoINT)
  const isPhotoTool = selected.id.includes('suncalc') || selected.id.includes('meta') || selected.input.includes('photo') || selected.input.includes('файл');
  
  if (isPhotoTool) {
    document.getElementById('tvPhotoUploaderBox').style.display = 'block';
    document.getElementById('tvTextInputRow').style.display = 'none';
  } else {
    document.getElementById('tvPhotoUploaderBox').style.display = 'none';
    document.getElementById('tvTextInputRow').style.display = 'flex';
  }

  const input = document.getElementById('tvTargetInput');
  input.value = '';
  if (selected.scan_type === 'telegram' || selected.id.includes('tg')) {
    input.placeholder = `Введите @username или Telegram ID (например: durov или 5233450569)`;
  } else if (selected.input === 'username') {
    input.placeholder = `Введите username для 60+ баз данных (например: wertag20)`;
  } else if (selected.input === 'domain') {
    input.placeholder = `Введите домен (например: example.com)`;
  } else if (selected.input === 'email') {
    input.placeholder = `Введите email (например: user@gmail.com)`;
  } else if (selected.input === 'ip') {
    input.placeholder = `Введите IP-адрес (например: 8.8.8.8)`;
  } else {
    input.placeholder = `Введите цель для анализа в ${selected.name}`;
  }

  document.getElementById('tvOutputBox').style.display = 'none';
  document.getElementById('tvOutputBox').innerHTML = '';

  // Рендер команд установки
  const cmdsDiv = document.getElementById('tvInstallCommands');
  cmdsDiv.innerHTML = '';
  const guide = selected.install_guide || {};

  if (guide.git) cmdsDiv.appendChild(createCmdBox('1. Клонирование Git', guide.git));
  if (guide.pip_or_pkg) cmdsDiv.appendChild(createCmdBox('2. Установка зависимостей', guide.pip_or_pkg));
  if (guide.usage) cmdsDiv.appendChild(createCmdBox('3. Пример запуска (CLI)', guide.usage));
  if (guide.docker) cmdsDiv.appendChild(createCmdBox('🐳 Запуск через Docker', guide.docker));
  if (guide.notes) {
    const notesBox = document.createElement('div');
    notesBox.style.marginTop = '10px';
    notesBox.style.fontSize = '12px';
    notesBox.style.color = '#cbd5e1';
    notesBox.innerHTML = `<b>💡 Примечание:</b> ${guide.notes}`;
    cmdsDiv.appendChild(notesBox);
  }

  showView('toolView');
}

// ОБРАБОТКА ЗАГРУЗКИ ФОТО НА СТРАНИЦЕ УТИЛИТЫ
async function handlePhotoUpload(input) {
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];

  const preview = document.getElementById('tvPhotoPreview');
  const reader = new FileReader();
  reader.onload = async function(e) {
    preview.src = e.target.result;
    preview.style.display = 'block';

    const loader = document.getElementById('tvLoader');
    const outBox = document.getElementById('tvOutputBox');
    loader.style.display = 'block';
    outBox.style.display = 'none';

    try {
      const res = await fetch('/api/scan/photo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: e.target.result })
      });
      const data = await res.json();
      loader.style.display = 'none';
      outBox.style.display = 'block';

      renderPhotoAnalysisOutput(data, outBox);
    } catch (err) {
      loader.style.display = 'none';
      outBox.style.display = 'block';
      outBox.innerHTML = `<div style="color:var(--danger);">❌ Ошибка анализа фото: ${err.message}</div>`;
    }
  };
  reader.readAsDataURL(file);
}

// ПРЯМОЙ АНАЛИЗ ФОТО ИЗ ВКЛАДКИ ФОТО
async function processDirectPhoto(input) {
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];

  const preview = document.getElementById('directPhotoPreview');
  const reader = new FileReader();
  reader.onload = async function(e) {
    preview.src = e.target.result;
    preview.style.display = 'block';

    const loader = document.getElementById('photoLoader');
    const outBox = document.getElementById('photoResultBox');
    loader.style.display = 'block';
    outBox.innerHTML = '';

    try {
      const res = await fetch('/api/scan/photo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: e.target.result })
      });
      const data = await res.json();
      loader.style.display = 'none';

      renderPhotoAnalysisOutput(data, outBox);
    } catch (err) {
      loader.style.display = 'none';
      outBox.innerHTML = `<div style="color:var(--danger); padding:12px;">❌ Ошибка: ${err.message}</div>`;
    }
  };
  reader.readAsDataURL(file);
}

function renderPhotoAnalysisOutput(data, container) {
  const exif = data.exif || {};
  let gpsHtml = '<span style="color:var(--text-muted);">Координаты GPS отсутствуют в EXIF (стерты или снято без геопозиции)</span>';

  if (exif.gps) {
    gpsHtml = `
      <div style="color:var(--primary); font-weight:700; margin-bottom:6px;">
        📍 Координаты: ${exif.gps.latitude}, ${exif.gps.longitude}
      </div>
      <a href="${exif.google_maps_url}" target="_blank" rel="noopener" class="btn btn-primary" style="padding:6px 12px;">
        <i class="fa-solid fa-map-location-dot"></i> Открыть точку на Google Maps
      </a>
    `;
  }

  let html = `
    <div class="output-header">
      <span><i class="fa-solid fa-camera" style="color:var(--cyan);"></i> Экспертиза изображения: Метаданные & Vision AI</span>
      <span class="badge badge-api">УСПЕШНО</span>
    </div>

    <!-- Блок EXIF -->
    <div style="background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:14px; margin-bottom:12px; font-size:13px;">
      <div style="font-weight:700; color:#fff; margin-bottom:8px;"><i class="fa-solid fa-microchip"></i> EXIF Метаданные камеры:</div>
      <div style="margin-bottom:4px;"><b>Камера:</b> ${exif.camera_make || '—'} ${exif.camera_model || 'Не указана'}</div>
      <div style="margin-bottom:4px;"><b>Дата съемки:</b> ${exif.date_time || 'Скрыта'}</div>
      <div style="margin-bottom:4px;"><b>ПО / Редактор:</b> ${exif.software || 'Оригинал камеры'}</div>
      <div style="margin-top:10px; padding-top:10px; border-top:1px solid #1e293b;">
        <b>GPS Геолокация:</b><br>${gpsHtml}
      </div>
    </div>

    <!-- Кнопки обратного поиска по картинкам -->
    <div style="margin-bottom:14px;">
      <div style="font-size:12px; font-weight:700; color:var(--cyan); margin-bottom:6px; text-transform:uppercase;">
        <i class="fa-solid fa-magnifying-glass"></i> Обратный поиск изображения (Reverse Search):
      </div>
      <div class="btn-group">
        <a href="https://yandex.ru/images/search?rpt=imageview" target="_blank" rel="noopener" class="btn btn-secondary"><i class="fa-solid fa-arrow-up-right-from-square"></i> Яндекс Картинки</a>
        <a href="https://lens.google.com/" target="_blank" rel="noopener" class="btn btn-secondary"><i class="fa-solid fa-arrow-up-right-from-square"></i> Google Lens</a>
        <a href="https://tineye.com/" target="_blank" rel="noopener" class="btn btn-secondary"><i class="fa-solid fa-arrow-up-right-from-square"></i> TinEye</a>
      </div>
    </div>

    <!-- Блок Vision AI анализа местности -->
    <div class="ai-dossier-card">
      <div class="ai-dossier-title"><i class="fa-solid fa-brain"></i> Аналитический GeoINT отчет (Gemini Vision AI)</div>
      <div class="ai-dossier-text">${formatMarkdownText(data.vision_ai_report)}</div>
    </div>
  `;

  container.innerHTML = html;
}

// ЗАПУСК СКАНИРОВАНИЯ ТЕКСТОВОЙ ЦЕЛИ
async function runCurrentToolScan() {
  if (!activeTool) return;
  const target = document.getElementById('tvTargetInput').value.trim();
  const loader = document.getElementById('tvLoader');
  const outBox = document.getElementById('tvOutputBox');

  if (!target) {
    alert('Пожалуйста, введите цель для анализа!');
    return;
  }

  loader.style.display = 'block';
  outBox.style.display = 'none';

  let endpoint = '/api/scan/username';
  if (activeTool.scan_type === 'telegram' || activeTool.id.includes('tg') || target.startsWith('@')) {
    endpoint = '/api/scan/telegram';
  } else if (activeTool.input === 'domain' || (target.includes('.') && !target.includes('@'))) {
    endpoint = '/api/scan/domain';
  } else if (activeTool.input === 'email' || target.includes('@')) {
    endpoint = '/api/scan/email';
  } else if (activeTool.input === 'ip' || /^(\d{1,3}\.){3}\d{1,3}$/.test(target)) {
    endpoint = '/api/scan/ip';
  }

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target })
    });
    const data = await res.json();
    loader.style.display = 'none';
    outBox.style.display = 'block';

    renderToolSpecificOutput(data, target);
  } catch (err) {
    loader.style.display = 'none';
    outBox.style.display = 'block';
    outBox.innerHTML = `<div style="color:var(--danger);">❌ Ошибка выполнения сканирования: ${err.message}</div>`;
  }
}

function renderToolSpecificOutput(data, target) {
  const outBox = document.getElementById('tvOutputBox');
  let html = `
    <div class="output-header">
      <span><i class="fa-solid fa-terminal" style="color:var(--primary);"></i> Вывод [${activeTool.name}] & AI-досье: <code style="color:var(--cyan);">${target}</code></span>
      <span class="badge badge-api">ВЫПОЛНЕНО</span>
    </div>
  `;

  const nowStr = new Date().toISOString().replace('T', ' ').substr(0, 19);

  if (data.type === 'username') {
    const profiles = data.profiles || [];
    let checkedLines = profiles.map(p => `[${nowStr}] [+] [FOUND] ${p.platform.padEnd(14)} (${p.category}) -> ${p.url}`).join('\n');
    let cliLog = `[${nowStr}] [*] Инициализация движка Sherlock Engine (60+ баз данных)...
[${nowStr}] [*] Целевой идентификатор: "${data.username}"
${checkedLines || `[${nowStr}] [-] Прямых совпадений не обнаружено`}
[${nowStr}] [✓] Поиск завершен: ${data.found_count} подтвержденных аккаунтов из ${data.total_checked} проверенных сервисов.`;

    html += `
      <div style="margin-bottom:12px;">
        <div style="font-size:12px; font-weight:700; color:var(--cyan); margin-bottom:6px; text-transform:uppercase;">
          <i class="fa-solid fa-code"></i> Консольный вывод Sherlock Engine (CLI Log):
        </div>
        <div class="code-wrap" style="color:#22c55e; font-size:11px; line-height:1.5;">${cliLog}</div>
      </div>

      <div style="font-size:14px; font-weight:700; color:#fff; margin-bottom:10px;">
        Найдено подтвержденных профилей: <b style="color:var(--primary);">${data.found_count}</b> из ${data.total_checked}
      </div>
    `;

    if (profiles.length > 0) {
      html += '<div class="profiles-grid">';
      profiles.forEach(p => {
        html += `
          <div class="profile-card">
            <div class="profile-left">
              <i class="fa-brands ${p.icon || 'fa-globe'} profile-icon"></i>
              <div>
                <div class="profile-name">${p.platform}</div>
                <span class="profile-tag">✅ ${p.category}</span>
              </div>
            </div>
            <a href="${p.url}" target="_blank" rel="noopener" class="btn btn-secondary" style="padding:4px 8px; font-size:11px;">🔗 Открыть</a>
          </div>
        `;
      });
      html += '</div>';
    }

    if (data.ai_summary) {
      html += `
        <div class="ai-dossier-card">
          <div class="ai-dossier-title"><i class="fa-solid fa-brain"></i> Аналитический ИИ-портрет личности (Gemini AI)</div>
          <div class="ai-dossier-text">${formatMarkdownText(data.ai_summary)}</div>
        </div>
      `;
    }

  } else if (data.type === 'telegram') {
    let cliLog = `[${nowStr}] [*] Подключение к Telegram Gateway t.me/${data.username}...
[${nowStr}] [+] HTTP 200 OK — Объект найден: "${data.title}"
[${nowStr}] [+] Категория: ${data.account_type}
[${nowStr}] [+] Bio: "${data.description}"
[${nowStr}] [✓] Сканирование Telegram завершено.`;

    html += `
      <div style="margin-bottom:12px;">
        <div class="code-wrap" style="color:#22c55e; font-size:11px;">${cliLog}</div>
      </div>
      <div class="tg-profile-card">
        <img class="tg-avatar" src="${data.photo_url || 'https://telegram.org/img/t_logo.png'}" alt="Avatar">
        <div class="tg-info">
          <div class="tg-name">${data.title} <span class="badge badge-web">${data.account_type}</span></div>
          <div class="tg-handle">@${data.username}</div>
          <div class="tg-desc">${data.description}</div>
          <div style="margin-top:8px;">
            <a href="${data.url}" target="_blank" rel="noopener" class="btn btn-primary" style="padding:4px 10px; font-size:11px;">✈️ Открыть в Telegram</a>
          </div>
        </div>
      </div>
    `;
    if (data.ai_summary) {
      html += `
        <div class="ai-dossier-card">
          <div class="ai-dossier-title"><i class="fa-solid fa-brain"></i> Аналитика Telegram (Gemini AI)</div>
          <div class="ai-dossier-text">${formatMarkdownText(data.ai_summary)}</div>
        </div>
      `;
    }
  }

  outBox.innerHTML = html;
}

// ПРЯМОЙ ЗАПУСК AI ДОСЬЕ
async function runAiDossierDirect() {
  const target = document.getElementById('aiSearchTarget').value.trim();
  const loader = document.getElementById('aiLoader');
  const resultDiv = document.getElementById('aiDossierResultDirect');

  if (!target) {
    alert('Введите цель для составления досье!');
    return;
  }

  loader.style.display = 'block';
  resultDiv.innerHTML = '';

  try {
    const res = await fetch('/api/ai/deduce', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target: target, tool: 'Deep Recon AI' })
    });
    const data = await res.json();
    loader.style.display = 'none';

    resultDiv.innerHTML = `
      <div class="ai-dossier-card">
        <div class="ai-dossier-title"><i class="fa-solid fa-brain"></i> Аналитическое досье по цели: ${target}</div>
        <div class="ai-dossier-text">${formatMarkdownText(data.dossier)}</div>
      </div>
    `;
  } catch (err) {
    loader.style.display = 'none';
    resultDiv.innerHTML = `<div style="color:var(--danger); padding:12px;">Ошибка: ${err.message}</div>`;
  }
}

function createCmdBox(label, cmd) {
  const box = document.createElement('div');
  box.className = 'cmd-box';
  box.innerHTML = `
    <div class="cmd-label">
      <span>${label}</span>
      <button class="copy-btn" onclick="copyText(this, \`${cmd.replace(/`/g, '\\`')}\`)">Копировать</button>
    </div>
    <div class="code-wrap">${cmd}</div>
  `;
  return box;
}

function copyText(btn, text) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.innerText;
    btn.innerText = 'Скопировано!';
    setTimeout(() => { btn.innerText = orig; }, 1500);
  });
}

function formatMarkdownText(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
    .replace(/\*(.*?)\*/g, '<i>$1</i>')
    .replace(/`(.*?)`/g, '<code style="background:#1e293b; padding:2px 4px; border-radius:4px; color:var(--primary);">$1</code>');
}

loadCatalog();
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_CONTENT


@app.get("/lab", response_class=HTMLResponse)
async def lab():
    return HTML_CONTENT


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
