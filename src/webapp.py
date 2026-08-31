import asyncio
import base64
import io
import json
import os
import re
import socket
import ssl
import sys
import time
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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
VISITS_FILE = DATA_DIR / "visits.jsonl"
USERS_FILE = DATA_DIR / "users.json"
WMN_FILE = DATA_DIR / "wmn_sites.json"

# In-memory LRU Cache
SCAN_CACHE = {}
CACHE_TTL = 600

app = FastAPI(title="OSINT Cyber Hub: 750+ Global & CIS Reconnaissance Engine")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_users() -> dict:
    if not USERS_FILE.exists():
        default_users = {
            "admin": {
                "username": "admin",
                "password": "admin123",
                "role": "admin",
                "status": "active",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "total_scans": 0,
                "notes": "Главный администратор"
            },
            "analyst": {
                "username": "analyst",
                "password": "analyst123",
                "role": "vip",
                "status": "active",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "total_scans": 0,
                "notes": "OSINT-исследователь"
            },
            "guest": {
                "username": "guest",
                "password": "guest123",
                "role": "user",
                "status": "active",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "total_scans": 0,
                "notes": "Демо доступ"
            }
        }
        USERS_FILE.write_text(json.dumps(default_users, ensure_ascii=False, indent=2), encoding="utf-8")
        return default_users
    try:
        return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_users(users: dict) -> None:
    USERS_FILE.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def increment_user_scan(username: str = "guest") -> None:
    try:
        users = load_users()
        if username in users:
            users[username]["total_scans"] = users[username].get("total_scans", 0) + 1
            save_users(users)
    except Exception:
        pass


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
            async with httpx.AsyncClient(timeout=14.0) as client:
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


# --- ОСНОВНЫЕ ПЛАТФОРМЫ С ГЛУБОКИМ ИЗВЛЕЧЕНИЕМ МЕТАДАННЫХ ---

CORE_ENRICHED_SITES = [
    # Соцсети & Мессенджеры СНГ и Мира
    {"name": "Telegram", "cat": "Социальные сети", "icon": "fa-telegram", "url": "https://t.me/{u}", "check": "https://t.me/{u}", "type": "tg"},
    {"name": "VKontakte", "cat": "Социальные сети", "icon": "fa-vk", "url": "https://vk.com/{u}", "check": "https://vk.com/{u}", "type": "status"},
    {"name": "Odnoklassniki", "cat": "Социальные сети", "icon": "fa-odnoklassniki", "url": "https://ok.ru/{u}", "check": "https://ok.ru/{u}", "type": "status"},
    {"name": "TikTok", "cat": "Социальные сети", "icon": "fa-tiktok", "url": "https://www.tiktok.com/@{u}", "check": "https://www.tiktok.com/@{u}", "type": "status"},
    {"name": "Pinterest", "cat": "Социальные сети", "icon": "fa-pinterest", "url": "https://www.pinterest.com/{u}/", "check": "https://www.pinterest.com/{u}/", "type": "status"},
    {"name": "Reddit", "cat": "Социальные сети", "icon": "fa-reddit", "url": "https://www.reddit.com/user/{u}", "check": "https://www.reddit.com/user/{u}/about.json", "type": "reddit_api"},
    {"name": "Twitter / X", "cat": "Социальные сети", "icon": "fa-x-twitter", "url": "https://x.com/{u}", "check": "https://x.com/{u}", "type": "status"},
    {"name": "Snapchat", "cat": "Социальные сети", "icon": "fa-snapchat", "url": "https://www.snapchat.com/add/{u}", "check": "https://www.snapchat.com/add/{u}", "type": "status"},
    {"name": "Mastodon", "cat": "Социальные сети", "icon": "fa-mastodon", "url": "https://mastodon.social/@{u}", "check": "https://mastodon.social/@{u}", "type": "status"},
    {"name": "Bluesky", "cat": "Социальные сети", "icon": "fa-cloud", "url": "https://bsky.app/profile/{u}.bsky.social", "check": "https://bsky.app/profile/{u}.bsky.social", "type": "status"},
    {"name": "TenChat", "cat": "Социальные сети", "icon": "fa-briefcase", "url": "https://tenchat.ru/{u}", "check": "https://tenchat.ru/{u}", "type": "status"},
    {"name": "Tumblr", "cat": "Социальные сети", "icon": "fa-tumblr", "url": "https://{u}.tumblr.com", "check": "https://{u}.tumblr.com", "type": "status"},

    # IT, Разработка, Репозитории
    {"name": "GitHub", "cat": "IT & Разработка", "icon": "fa-github", "url": "https://github.com/{u}", "check": "https://api.github.com/users/{u}", "type": "github_api"},
    {"name": "GitLab", "cat": "IT & Разработка", "icon": "fa-gitlab", "url": "https://gitlab.com/{u}", "check": "https://gitlab.com/api/v4/users?username={u}", "type": "gitlab_api"},
    {"name": "Bitbucket", "cat": "IT & Разработка", "icon": "fa-bitbucket", "url": "https://bitbucket.org/{u}/", "check": "https://bitbucket.org/{u}/", "type": "status"},
    {"name": "DockerHub", "cat": "IT & Разработка", "icon": "fa-docker", "url": "https://hub.docker.com/u/{u}", "check": "https://hub.docker.com/v2/users/{u}", "type": "status"},
    {"name": "Dev.to", "cat": "IT & Разработка", "icon": "fa-dev", "url": "https://dev.to/{u}", "check": "https://dev.to/api/users/by_username?url={u}", "type": "devto_api"},
    {"name": "Habr", "cat": "IT & Разработка", "icon": "fa-code", "url": "https://habr.com/ru/users/{u}/", "check": "https://habr.com/ru/users/{u}/", "type": "status"},
    {"name": "Medium", "cat": "IT & Разработка", "icon": "fa-medium", "url": "https://medium.com/@{u}", "check": "https://medium.com/@{u}", "type": "status"},
    {"name": "Kaggle", "cat": "IT & Разработка", "icon": "fa-brain", "url": "https://www.kaggle.com/{u}", "check": "https://www.kaggle.com/{u}", "type": "status"},
    {"name": "LeetCode", "cat": "IT & Разработка", "icon": "fa-terminal", "url": "https://leetcode.com/{u}", "check": "https://leetcode.com/{u}", "type": "status"},
    {"name": "Codeforces", "cat": "IT & Разработка", "icon": "fa-laptop-code", "url": "https://codeforces.com/profile/{u}", "check": "https://codeforces.com/profile/{u}", "type": "status"},
    {"name": "Replit", "cat": "IT & Разработка", "icon": "fa-code-branch", "url": "https://replit.com/@{u}", "check": "https://replit.com/@{u}", "type": "status"},
    {"name": "NPM", "cat": "IT & Разработка", "icon": "fa-npm", "url": "https://www.npmjs.com/~{u}", "check": "https://www.npmjs.com/~{u}", "type": "status"},
    {"name": "PyPI", "cat": "IT & Разработка", "icon": "fa-python", "url": "https://pypi.org/user/{u}/", "check": "https://pypi.org/user/{u}/", "type": "status"},
    {"name": "Behance", "cat": "IT & Разработка", "icon": "fa-behance", "url": "https://www.behance.net/{u}", "check": "https://www.behance.net/{u}", "type": "status"},
    {"name": "Dribbble", "cat": "IT & Разработка", "icon": "fa-dribbble", "url": "https://dribbble.com/{u}", "check": "https://dribbble.com/{u}", "type": "status"},
    {"name": "ArtStation", "cat": "IT & Разработка", "icon": "fa-palette", "url": "https://www.artstation.com/{u}", "check": "https://www.artstation.com/{u}", "type": "status"},

    # Гейминг & Киберспорт
    {"name": "Steam", "cat": "Гейминг", "icon": "fa-steam", "url": "https://steamcommunity.com/id/{u}", "check": "https://steamcommunity.com/id/{u}", "type": "steam_page"},
    {"name": "Roblox", "cat": "Гейминг", "icon": "fa-gamepad", "url": "https://www.roblox.com/user.aspx?username={u}", "check": "https://www.roblox.com/user.aspx?username={u}", "type": "status"},
    {"name": "Twitch", "cat": "Гейминг", "icon": "fa-twitch", "url": "https://www.twitch.tv/{u}", "check": "https://www.twitch.tv/{u}", "type": "status"},
    {"name": "Chess.com", "cat": "Гейминг", "icon": "fa-chess", "url": "https://www.chess.com/member/{u}", "check": "https://api.chess.com/pub/player/{u}", "type": "chess_api"},
    {"name": "Lichess", "cat": "Гейминг", "icon": "fa-chess-knight", "url": "https://lichess.org/@/{u}", "check": "https://lichess.org/api/user/{u}", "type": "status"},
    {"name": "NameMC (Minecraft)", "cat": "Гейминг", "icon": "fa-cube", "url": "https://namemc.com/profile/{u}", "check": "https://namemc.com/profile/{u}", "type": "status"},
    {"name": "Osu!", "cat": "Гейминг", "icon": "fa-circle-dot", "url": "https://osu.ppy.sh/users/{u}", "check": "https://osu.ppy.sh/users/{u}", "type": "status"},
    {"name": "Faceit", "cat": "Гейминг", "icon": "fa-crosshairs", "url": "https://www.faceit.com/en/players/{u}", "check": "https://www.faceit.com/en/players/{u}", "type": "status"},
    {"name": "Speedrun.com", "cat": "Гейминг", "icon": "fa-stopwatch", "url": "https://www.speedrun.com/user/{u}", "check": "https://www.speedrun.com/user/{u}", "type": "status"},
    {"name": "Tracker.gg", "cat": "Гейминг", "icon": "fa-chart-simple", "url": "https://tracker.gg/profile/{u}", "check": "https://tracker.gg/profile/{u}", "type": "status"},

    # Медиа & Стриминг
    {"name": "YouTube", "cat": "Медиа & Музыка", "icon": "fa-youtube", "url": "https://www.youtube.com/@{u}", "check": "https://www.youtube.com/@{u}", "type": "status"},
    {"name": "Rutube", "cat": "Медиа & Музыка", "icon": "fa-play", "url": "https://rutube.ru/channel/{u}/", "check": "https://rutube.ru/channel/{u}/", "type": "status"},
    {"name": "Spotify", "cat": "Медиа & Музыка", "icon": "fa-spotify", "url": "https://open.spotify.com/user/{u}", "check": "https://open.spotify.com/user/{u}", "type": "status"},
    {"name": "SoundCloud", "cat": "Медиа & Музыка", "icon": "fa-soundcloud", "url": "https://soundcloud.com/{u}", "check": "https://soundcloud.com/{u}", "type": "status"},
    {"name": "Bandcamp", "cat": "Медиа & Музыка", "icon": "fa-music", "url": "https://{u}.bandcamp.com", "check": "https://{u}.bandcamp.com", "type": "status"},
    {"name": "Last.fm", "cat": "Медиа & Музыка", "icon": "fa-lastfm", "url": "https://www.last.fm/user/{u}", "check": "https://www.last.fm/user/{u}", "type": "status"},
    {"name": "Vimeo", "cat": "Медиа & Музыка", "icon": "fa-vimeo", "url": "https://vimeo.com/{u}", "check": "https://vimeo.com/{u}", "type": "status"},

    # Блоги & Форумы
    {"name": "Pikabu", "cat": "Блоги & Форумы", "icon": "fa-comments", "url": "https://pikabu.ru/@{u}", "check": "https://pikabu.ru/@{u}", "type": "status"},
    {"name": "DTF.ru", "cat": "Блоги & Форумы", "icon": "fa-gamepad", "url": "https://dtf.ru/u/{u}", "check": "https://dtf.ru/u/{u}", "type": "status"},
    {"name": "VC.ru", "cat": "Блоги & Форумы", "icon": "fa-chart-line", "url": "https://vc.ru/u/{u}", "check": "https://vc.ru/u/{u}", "type": "status"},
    {"name": "4PDA", "cat": "Блоги & Форумы", "icon": "fa-mobile-screen", "url": "https://4pda.to/forum/index.php?showuser={u}", "check": "https://4pda.to/forum/index.php?showuser={u}", "type": "status"},
    {"name": "LiveJournal", "cat": "Блоги & Форумы", "icon": "fa-pen-nib", "url": "https://{u}.livejournal.com", "check": "https://{u}.livejournal.com", "type": "status"},
    {"name": "Pastebin", "cat": "Блоги & Форумы", "icon": "fa-file-lines", "url": "https://pastebin.com/u/{u}", "check": "https://pastebin.com/u/{u}", "type": "status"},
    {"name": "Wattpad", "cat": "Блоги & Форумы", "icon": "fa-book-open", "url": "https://www.wattpad.com/user/{u}", "check": "https://www.wattpad.com/user/{u}", "type": "status"},
    {"name": "Letterboxd", "cat": "Блоги & Форумы", "icon": "fa-film", "url": "https://letterboxd.com/{u}", "check": "https://letterboxd.com/{u}", "type": "status"},
    {"name": "MyAnimeList", "cat": "Блоги & Форумы", "icon": "fa-tv", "url": "https://myanimelist.net/profile/{u}", "check": "https://myanimelist.net/profile/{u}", "type": "status"},
    {"name": "Duolingo", "cat": "Блоги & Форумы", "icon": "fa-language", "url": "https://www.duolingo.com/profile/{u}", "check": "https://www.duolingo.com/profile/{u}", "type": "status"},

    # Донаты, Контакты & Фриланс
    {"name": "Boosty", "cat": "Контакты & Донаты", "icon": "fa-bolt", "url": "https://boosty.to/{u}", "check": "https://boosty.to/{u}", "type": "status"},
    {"name": "Patreon", "cat": "Контакты & Донаты", "icon": "fa-patreon", "url": "https://www.patreon.com/{u}", "check": "https://www.patreon.com/{u}", "type": "status"},
    {"name": "Linktree", "cat": "Контакты & Донаты", "icon": "fa-link", "url": "https://linktr.ee/{u}", "check": "https://linktr.ee/{u}", "type": "status"},
    {"name": "BuyMeACoffee", "cat": "Контакты & Донаты", "icon": "fa-mug-hot", "url": "https://www.buymeacoffee.com/{u}", "check": "https://www.buymeacoffee.com/{u}", "type": "status"},
    {"name": "Kwork", "cat": "Контакты & Донаты", "icon": "fa-briefcase", "url": "https://kwork.ru/user/{u}", "check": "https://kwork.ru/user/{u}", "type": "status"},
    {"name": "FL.ru", "cat": "Контакты & Донаты", "icon": "fa-laptop", "url": "https://www.fl.ru/users/{u}", "check": "https://www.fl.ru/users/{u}", "type": "status"},
    {"name": "Freelance.ru", "cat": "Контакты & Донаты", "icon": "fa-user-tie", "url": "https://freelance.ru/{u}", "check": "https://freelance.ru/{u}", "type": "status"},
]


def load_wmn_sites() -> list:
    """Загружает базу WhatsMyName (716+ платформ) из локального кэша или GitHub."""
    if WMN_FILE.exists():
        try:
            return json.loads(WMN_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    try:
        import urllib.request
        url = "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"
        with urllib.request.urlopen(url, timeout=6.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sites = data.get("sites", [])
            if sites:
                WMN_FILE.write_text(json.dumps(sites, ensure_ascii=False, indent=2), encoding="utf-8")
                return sites
    except Exception:
        pass
    return []


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


# --- СИНТЕЗ И ДЕДУКЦИЯ НАИВЕРОЯТНЕЙШИХ ДАННЫХ ---

def synthesize_heuristic_dossier(username: str, found_profiles: list, intel_signals: dict) -> tuple[dict, str]:
    names = intel_signals.get("names", [])
    locations = intel_signals.get("locations", [])
    bios = intel_signals.get("bios", [])
    reg_years = intel_signals.get("reg_years", [])
    
    # 1. Наивероятнейшее имя
    best_name = names[0].split(" (")[0] if names else username
    for n in names:
        if " " in n:
            best_name = n.split(" (")[0]
            break

    # 2. Наивероятнейшая локация
    best_loc = locations[0].split(" (")[0] if locations else "Определяется по часовому поясу / СНГ"

    # 3. Реалистичная оценка возраста
    current_year = datetime.now().year
    oldest_yr_str = reg_years[0].split(" ")[0] if reg_years else ""
    est_age = "20–30 лет (активный цифровой возраст)"

    if oldest_yr_str:
        try:
            yr = int(re.search(r"\d{4}", oldest_yr_str).group())
            years_online = current_year - yr
            est_age = f"~{18 + max(0, years_online)}–{24 + max(0, years_online)} лет (аккаунты в сети с {yr} г.)"
        except Exception:
            pass
    else:
        num_match = re.search(r"(\d{2,4})$", username)
        if num_match:
            num = int(num_match.group(1))
            if 1960 <= num <= 2010:
                est_age = f"~{current_year - num} лет ({num} г.р.)"
            elif 70 <= num <= 99:
                birth_yr = 1900 + num
                est_age = f"~{current_year - birth_yr} лет ({birth_yr} г.р.)"
            elif 0 <= num <= 10:
                birth_yr = 2000 + num
                est_age = f"~{current_year - birth_yr} лет ({birth_yr} г.р.)"
            elif 14 <= num <= 40:
                est_age = f"~{num}–{num+4} лет (маркер возраста '{num}' в никнейме)"

    confidence = min(98, 45 + len(found_profiles) * 2 + (15 if names else 0) + (10 if locations else 0))
    cats = [p.get("category", "Прочее") for p in found_profiles]

    probable_data = {
        "name": best_name,
        "location": best_loc,
        "age_estimate": est_age,
        "oldest_account": reg_years[0] if reg_years else "2019–2022 гг.",
        "confidence": f"{confidence}%",
        "total_active": len(found_profiles)
    }

    markdown_dossier = f"""### 🎯 НАИВЕРОЯТНЕЙШИЕ ДАННЫЕ (СВОДНЫЙ ВЫВОД):
- 👤 **Вероятное реальное имя / ФИО**: `{best_name}` {'(подтверждено: ' + ', '.join(names[:2]) + ')' if names else '(доминирующий цифровой псевдоним)'}
- 🎂 **Вероятный возраст / Год рождения**: `{est_age}`
- 🏙️ **Вероятный город / Страна**: `{best_loc}`
- 📊 **Индекс совпадения личности (Confidence)**: `{confidence}%` — {'высокая' if confidence >= 80 else 'средняя'} степень корреляции

---

### 🧠 ГЛУБОКИЙ АНАЛИТИЧЕСКИЙ РАЗБОР СВЯЗЕЙ:
1. **Пересечение аккаунтов**: Идентификатор `{username}` подтвержден на {len(found_profiles)} платформах (категории: {', '.join(set(cats))}).
2. **Цифровой след**: {'Обнаружены совпадающие профили, гео-метки и метаданные.' if bios or names else 'Никнейм уникален и имеет высокую плотность совпадений в базах.'}
3. **Рекомендованные следующие шаги**:
   - Выполнить `/tg @{username}` для углубленного анализа Telegram.
   - Проверить аватар через модуль «Фото Экспертиза» (Google Lens / Яндекс).
   - Использовать `/export {username}` для сохранения полного отчета в файл.
"""
    return probable_data, markdown_dossier


# --- API ЭНДПОИНТЫ ДЛЯ СИСТЕМЫ АККАУНТОВ ---

@app.post("/api/auth/login")
async def api_auth_login(request: Request):
    body = await request.json()
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", "")).strip()

    users = load_users()
    if username in users and users[username]["password"] == password:
        user = users[username]
        if user.get("status") == "blocked":
            return JSONResponse({"ok": False, "error": "Аккаунт заблокирован администратором"}, status_code=403)
        return {
            "ok": True,
            "username": user["username"],
            "role": user["role"],
            "token": f"token_{user['username']}_{user['role']}"
        }
    return JSONResponse({"ok": False, "error": "Неверный логин или пароль"}, status_code=401)


@app.get("/api/admin/users")
async def api_admin_get_users():
    users = load_users()
    user_list = []
    for u in users.values():
        user_list.append({
            "username": u.get("username"),
            "role": u.get("role", "user"),
            "status": u.get("status", "active"),
            "created_at": u.get("created_at", "—"),
            "total_scans": u.get("total_scans", 0),
            "notes": u.get("notes", "")
        })
    return {"ok": True, "users": user_list}


@app.post("/api/admin/users/create")
async def api_admin_create_user(request: Request):
    body = await request.json()
    username = str(body.get("username", "")).strip().lower()
    password = str(body.get("password", "")).strip()
    role = str(body.get("role", "user")).strip().lower()
    notes = str(body.get("notes", "")).strip()

    if not username or not password:
        return JSONResponse({"ok": False, "error": "Заполните логин и пароль"}, status_code=400)

    users = load_users()
    if username in users:
        return JSONResponse({"ok": False, "error": "Пользователь с таким логином уже существует"}, status_code=400)

    users[username] = {
        "username": username,
        "password": password,
        "role": role if role in ["admin", "vip", "user"] else "user",
        "status": "active",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_scans": 0,
        "notes": notes
    }
    save_users(users)
    return {"ok": True, "message": f"Пользователь {username} успешно создан"}


@app.post("/api/admin/users/toggle_status")
async def api_admin_toggle_user(request: Request):
    body = await request.json()
    username = str(body.get("username", "")).strip()

    users = load_users()
    if username not in users:
        return JSONResponse({"ok": False, "error": "Пользователь не найден"}, status_code=404)

    current_status = users[username].get("status", "active")
    users[username]["status"] = "blocked" if current_status == "active" else "active"
    save_users(users)
    return {"ok": True, "new_status": users[username]["status"]}


@app.post("/api/admin/users/delete")
async def api_admin_delete_user(request: Request):
    body = await request.json()
    username = str(body.get("username", "")).strip()

    if username == "admin":
        return JSONResponse({"ok": False, "error": "Нельзя удалить главного администратора"}, status_code=400)

    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        return {"ok": True, "message": f"Пользователь {username} удален"}
    return JSONResponse({"ok": False, "error": "Пользователь не найден"}, status_code=404)


# --- КАТАЛОГ И ЛОГИ ВИЗИТОВ ---

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


# --- ГЛОБАЛЬНЫЙ КРОСС-ПОИСК SHERLOCK + WHATSMYNAME (750+ БАЗ ДАННЫХ) ---

@app.post("/api/scan/username")
async def scan_username_sherlock(request: Request):
    """
    Глобальный высокоскоростной поиск по 750+ мировым и СНГ базам данных (Sherlock + WhatsMyName),
    извлечение метаданных и сопоставление цифрового следа.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}
    username = str(body.get("target", "")).strip().lstrip("@")
    caller_user = str(body.get("caller", "guest")).strip()
    increment_user_scan(caller_user)

    if not username or len(username) < 2:
        return JSONResponse({"ok": False, "error": "Введите никнейм длиной от 2 символов"}, status_code=400)

    found = []
    found_names_set = set()

    intel_signals = {
        "names": [],
        "locations": [],
        "bios": [],
        "emails": [],
        "reg_years": [],
        "social_links": [],
        "interests": []
    }
    
    sem = asyncio.Semaphore(45)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 1. Проверка основных обогащенных сервисов (GitHub, Telegram, Steam, Chess, Reddit, VK, Habr...)
    async def check_core_site(client: httpx.AsyncClient, site: dict):
        target_url = site["check"].format(u=username)
        profile_url = site["url"].format(u=username)
        stype = site.get("type", "status")

        async with sem:
            try:
                r = await client.get(target_url, headers=headers, timeout=3.5, follow_redirects=True)
                if r.status_code == 200:
                    extra_meta = {}

                    # GitHub API
                    if stype == "github_api":
                        js = r.json()
                        if js.get("id"):
                            real_name = js.get("name")
                            loc = js.get("location")
                            bio = js.get("bio")
                            created = js.get("created_at", "")[:4]
                            if real_name: intel_signals["names"].append(f"{real_name} (GitHub)")
                            if loc: intel_signals["locations"].append(f"{loc} (GitHub)")
                            if bio: intel_signals["bios"].append(f"{bio} (GitHub)")
                            if created: intel_signals["reg_years"].append(f"{created} г. (GitHub)")
                            extra_meta = {"name": real_name, "location": loc, "bio": bio}

                    # Telegram Web
                    elif stype == "tg":
                        if "tgme_page_extra" not in r.text and "@" not in r.text:
                            return
                        soup = BeautifulSoup(r.text, "html.parser")
                        t_elem = soup.find("div", class_="tgme_page_title")
                        d_elem = soup.find("div", class_="tgme_page_description")
                        t_name = t_elem.get_text(strip=True) if t_elem else ""
                        d_bio = d_elem.get_text(strip=True) if d_elem else ""
                        if t_name and t_name != username: intel_signals["names"].append(f"{t_name} (Telegram)")
                        if d_bio and "If you have Telegram" not in d_bio: intel_signals["bios"].append(f"{d_bio} (Telegram)")
                        extra_meta = {"name": t_name, "bio": d_bio}

                    # Chess.com API
                    elif stype == "chess_api":
                        js = r.json()
                        c_name = js.get("name")
                        c_country = js.get("country", "").split("/")[-1] if js.get("country") else ""
                        if c_name: intel_signals["names"].append(f"{c_name} (Chess.com)")
                        if c_country: intel_signals["locations"].append(f"Страна: {c_country} (Chess.com)")
                        extra_meta = {"name": c_name, "country": c_country}

                    # Dev.to API
                    elif stype == "devto_api":
                        js = r.json()
                        d_name = js.get("name")
                        d_loc = js.get("location")
                        d_summary = js.get("summary")
                        if d_name: intel_signals["names"].append(f"{d_name} (Dev.to)")
                        if d_loc: intel_signals["locations"].append(f"{d_loc} (Dev.to)")
                        if d_summary: intel_signals["bios"].append(f"{d_summary} (Dev.to)")
                        extra_meta = {"name": d_name, "location": d_loc}

                    # Reddit API
                    elif stype == "reddit_api":
                        js = r.json()
                        sub = js.get("data", {}).get("subreddit", {})
                        r_title = sub.get("title")
                        if r_title and r_title != username: intel_signals["names"].append(f"{r_title} (Reddit)")

                    else:
                        if "user not found" in r.text.lower() or "страница не найдена" in r.text.lower() or "404 not found" in r.text.lower():
                            return

                    found.append({
                        "platform": site["name"],
                        "category": site["cat"],
                        "icon": site["icon"],
                        "url": profile_url,
                        "status": "Активен",
                        "meta": extra_meta
                    })
                    found_names_set.add(site["name"].lower())
            except Exception:
                pass

    # 2. Проверка WhatsMyName Registry (716+ платформ)
    wmn_sites = load_wmn_sites()

    async def check_wmn_site(client: httpx.AsyncClient, site: dict):
        sname = site.get("name", "")
        if sname.lower() in found_names_set:
            return

        check_url = site.get("uri_check", "").replace("{account}", username)
        if not check_url or not check_url.startswith("http"):
            return

        e_code = site.get("e_code", 200)
        m_str = (site.get("m_string") or "").lower()
        e_str = (site.get("e_string") or "").lower()
        cat = site.get("cat", "Прочее").capitalize()

        async with sem:
            try:
                r = await client.get(check_url, headers=headers, timeout=2.8, follow_redirects=True)
                if r.status_code == e_code:
                    txt = r.text.lower()
                    if m_str and m_str in txt:
                        return
                    if e_str and e_str not in txt:
                        return
                    
                    found.append({
                        "platform": sname,
                        "category": cat,
                        "icon": "fa-globe",
                        "url": check_url,
                        "status": "Активен",
                        "meta": {}
                    })
            except Exception:
                pass

    async with httpx.AsyncClient() as client:
        core_tasks = [check_core_site(client, s) for s in CORE_ENRICHED_SITES]
        await asyncio.gather(*core_tasks)

        wmn_tasks = [check_wmn_site(client, s) for s in wmn_sites]
        await asyncio.gather(*wmn_tasks)

    # --- ИИ-СИНТЕЗ И ДЕДУКЦИЯ НАИВЕРОЯТНЕЙШИХ ДАННЫХ ---
    total_db_count = len(CORE_ENRICHED_SITES) + len(wmn_sites)
    probable_data, default_markdown = synthesize_heuristic_dossier(username, found, intel_signals)

    if GEMINI_API_KEY:
        categories_found = list(set(p["category"] for p in found))
        platforms_str = ", ".join([p["platform"] for p in found[:30]])

        prompt = f"""Ты — главный аналитик расследований OSINT.
Проведен автоматизированный сбор по 750+ базам данных для цели: '{username}'.

СОБРАННЫЕ ДАННЫЕ И СИГНАЛЫ:
- Найденные платформы ({len(found)} шт.): {platforms_str}
- Категории активности: {categories_found}
- Извлеченные имена/псевдонимы из профилей: {intel_signals['names']}
- Извлеченные геолокации/города: {intel_signals['locations']}
- Извлеченные описания (Bio): {intel_signals['bios']}
- Года регистраций аккаунтов: {intel_signals['reg_years']}

ТВОЯ ЗАДАЧА:
Свяжи все эти источники воедино и сделай вывод о НАИВЕРОЯТНЕЙШИХ данных человека (без указания рода деятельности).
Верни ответ строго в таком формате:

### 🎯 НАИВЕРОЯТНЕЙШИЕ ДАННЫЕ (СВОДНЫЙ ВЫВОД):
- 👤 **Вероятное реальное имя / ФИО**: (укажи самое вероятное имя и из каких источников оно подтверждено)
- 🎂 **Вероятный возраст / Год рождения**: (сопоставь даты старейших регистраций, цифры в никнейме, сленг в bio и дай четкую оценку возраста)
- 🏙️ **Вероятный город / Страна**: (сопоставь геолокации из GitHub/Steam/Chess/часовых поясов)
- 📊 **Индекс совпадения личности (Confidence)**: (например: 94% — высокая точность совпадения)

---

### 🧠 ГЛУБОКИЙ АНАЛИТИЧЕСКИЙ РАЗБОР СВЯЗЕЙ:
(Опиши логику расследования: почему эти профили принадлежат одному человеку, какие пересечения обнаружены, и дай 3 точных шага для дальнейшей проверки)
"""
        gemini_dossier = await run_gemini_prompt(prompt)
        if gemini_dossier:
            default_markdown = gemini_dossier

    res = {
        "ok": True,
        "type": "username",
        "username": username,
        "found_count": len(found),
        "total_checked": total_db_count,
        "probable_data": probable_data,
        "intelligence_signals": intel_signals,
        "profiles": found,
        "ai_summary": default_markdown,
        "cached": False
    }

    SCAN_CACHE[cache_key] = (res, now_ts)
    return res


# --- СКАНИРОВАНИЕ И АНАЛИЗ ФОТОГРАФИЙ (EXIF + GEMINI VISION AI) ---

@app.post("/api/scan/photo")
async def scan_photo_endpoint(request: Request, file: Optional[UploadFile] = File(None)):
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

    exif_result = extract_exif_data(image_bytes)

    prompt = (
        "Ты — профессиональный эксперт по GeoINT и анализу изображений в расследованиях.\n"
        "Внимательно изучи прикрепленное фото и предоставь детальный OSINT-отчет:\n\n"
        "1. 🌍 **Геолокация и местоположение**: Определи страну, регион, город или тип ландшафта (по архитектуре, дорогам, растительности, розеткам, солнцу, номерам авто).\n"
        "2. 🔍 **Текст, вывески и надписи**: Распознай все видимые тексты, язык, бренды, дорожные указатели.\n"
        "3. ☀️ **Освещение и тени**: Оцени примерное время суток и угол падения лучей солнца.\n"
        "4. 💡 **Рекомендации по подтверждению локации**: Какие ориентиры проверить через спутники (Google Earth / Overpass)."
    )

    vision_ai_report = await run_gemini_prompt(prompt, image_bytes=image_bytes, mime_type=mime_type)
    if not vision_ai_report:
        gps = exif_result.get("gps")
        gps_txt = f"Координаты: {gps['latitude']}, {gps['longitude']}" if gps else "GPS метки отсутствуют в EXIF."
        vision_ai_report = (
            f"📸 **Экспертиза изображения завершена:**\n\n"
            f"• **Метаданные камеры:** {exif_result.get('camera_make') or '—'} {exif_result.get('camera_model') or ''}\n"
            f"• **Дата и время:** {exif_result.get('date_time') or 'Скрыто'}\n"
            f"• **GPS статус:** {gps_txt}\n\n"
            "💡 **Рекомендация:** Для определения точной геолокации используйте обратный поиск по картинкам в Google Lens и Яндекс Картинках."
        )

    return {
        "ok": True,
        "type": "photo",
        "exif": exif_result,
        "vision_ai_report": vision_ai_report,
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
    if not ai_text:
        ai_text = (
            f"💜 **Аналитическое досье на цель:** `{target}`\n\n"
            f"1. 👤 **Цифровой идентификатор:** `{target}`\n"
            f"2. 🔍 **Векторы анализа:** Рекомендуется запустить перекрестный поиск по 750+ базам через основную панель.\n"
            f"3. 🌐 **Telegram и мессенджеры:** Проверьте публичный статус через `/tg @{target}`."
        )
    return {"ok": True, "target": target, "dossier": ai_text}


# --- FRONTEND ИНТЕРФЕЙС WEBAPP PRO ---

HTML_CONTENT = Path(__file__).resolve().parent.parent / "index.html"


@app.get("/", response_class=HTMLResponse)
async def root():
    if HTML_CONTENT.exists():
        return HTML_CONTENT.read_text(encoding="utf-8")
    return "<h1>OSINT Cyber Hub Active</h1>"


@app.get("/lab", response_class=HTMLResponse)
async def lab():
    if HTML_CONTENT.exists():
        return HTML_CONTENT.read_text(encoding="utf-8")
    return "<h1>OSINT Cyber Hub Active</h1>"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
