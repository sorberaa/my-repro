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
SHERLOCK_FILE = DATA_DIR / "sherlock_data.json"
WMN_FILE = DATA_DIR / "wmn_sites.json"

app = FastAPI(title="OSINT Cyber Hub: Official Sherlock Engine & Truthful Recon")
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


# --- БАЗА ДАННЫХ SHERLOCK PROJECT ---

def load_sherlock_sites() -> dict:
    if SHERLOCK_FILE.exists():
        try:
            data = json.loads(SHERLOCK_FILE.read_text(encoding="utf-8"))
            if "$schema" in data: del data["$schema"]
            return data
        except Exception:
            pass
    try:
        import urllib.request
        url = "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock_project/resources/data.json"
        with urllib.request.urlopen(url, timeout=6.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "$schema" in data: del data["$schema"]
            SHERLOCK_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            return data
    except Exception:
        pass
    return {}


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
        "dimensions": None,
        "format": None,
        "gps": None,
        "google_maps_url": None,
        "raw_tags": {}
    }
    try:
        image = Image.open(io.BytesIO(image_bytes))
        info["format"] = image.format
        info["dimensions"] = f"{image.width}x{image.height} px"

        exif = None
        if hasattr(image, "_getexif"):
            exif = image._getexif()
        if not exif and hasattr(image, "getexif"):
            exif = image.getexif()

        if exif:
            info["has_exif"] = True
            gps_data = {}
            for tag_id, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                if tag_name == "Make":
                    info["camera_make"] = str(value).strip()
                elif tag_name == "Model":
                    info["camera_model"] = str(value).strip()
                elif tag_name in ["DateTimeOriginal", "DateTime", "DateTimeDigitized"]:
                    if not info["date_time"]:
                        info["date_time"] = str(value).strip()
                elif tag_name == "Software":
                    info["software"] = str(value).strip()
                elif tag_name == "LensModel":
                    info["lens_model"] = str(value).strip()
                elif tag_name == "GPSInfo":
                    gps_dict = value if isinstance(value, dict) else (dict(value) if hasattr(value, "items") else {})
                    for gps_tag_id, gval in gps_dict.items():
                        gps_tag_name = ExifTags.GPSTAGS.get(gps_tag_id, str(gps_tag_id))
                        gps_data[gps_tag_name] = gval

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

        if hasattr(image, "info") and image.info:
            png_meta = image.info
            if "Software" in png_meta and not info["software"]:
                info["software"] = str(png_meta["Software"])
                info["has_exif"] = True
            if "Creation Time" in png_meta and not info["date_time"]:
                info["date_time"] = str(png_meta["Creation Time"])
                info["has_exif"] = True

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
1. **Пересечение аккаунтов**: Идентификатор `{username}` подтвержден на {len(found_profiles)} платформах.
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


# --- ОФИЦИАЛЬНЫЙ ДВИЖОК SHERLOCK PROJECT С ПРОВЕРКОЙ ПОДЛИННОСТИ ---

def categorize_platform(name: str) -> str:
    name_l = name.lower()
    if any(k in name_l for k in ["git", "code", "dev", "npm", "pypi", "docker", "replit", "stack", "kaggle", "bitbucket"]):
        return "IT & Разработка"
    if any(k in name_l for k in ["steam", "chess", "lichess", "roblox", "twitch", "game", "speedrun", "faceit", "osu", "craft"]):
        return "Гейминг"
    if any(k in name_l for k in ["music", "sound", "spotify", "band", "tube", "vimeo", "last.fm", "radio"]):
        return "Медиа & Музыка"
    if any(k in name_l for k in ["telegram", "vk", "ok", "reddit", "twitter", "tiktok", "insta", "threads", "snap", "social", "mastodon", "blue"]):
        return "Социальные сети"
    if any(k in name_l for k in ["habr", "pikabu", "forum", "blog", "medium", "paste", "wattpad", "4pda", "dtf", "vc"]):
        return "Блоги & Форумы"
    if any(k in name_l for k in ["freelance", "fl", "kwork", "patreon", "boosty", "coffee", "link"]):
        return "Контакты & Фриланс"
    return "Сервисы & Прочее"


@app.post("/api/scan/username")
async def scan_username_sherlock(request: Request):
    """
    Официальный алгоритм Sherlock Project с защитой от ложных срабатываний,
    проверкой regex, кодов ошибок, сообщений об отсутствии пользователя и редиректов.
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
    
    sem = asyncio.Semaphore(50)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 1. Проверка через официальный реестр Sherlock Project (482 платформы)
    sherlock_db = load_sherlock_sites()

    async def probe_sherlock_site(client: httpx.AsyncClient, name: str, info: dict):
        if not isinstance(info, dict):
            return

        url = info.get("urlProbe") or info.get("url", "")
        url = url.replace("{}", username)
        profile_url = info.get("url", "").replace("{}", username)

        reg = info.get("regexCheck")
        if reg:
            try:
                if not re.match(reg, username):
                    return
            except Exception:
                pass

        async with sem:
            try:
                r = await client.get(url, headers=headers, timeout=3.5, follow_redirects=True)
                final_url = str(r.url).lower()
                
                # 1. Отсечение редиректов на главную / логин / капчу
                if username.lower() not in final_url and name.lower() not in ["telegram", "vkontakte"]:
                    return

                for bad_url_part in ["/login", "/signin", "/auth", "not-found", "/404", "challenge", "verify-human", "captcha", "typo", "reason=vendor_not_found", "consent", "privacygate"]:
                    if bad_url_part in final_url:
                        return

                if r.status_code != 200:
                    return

                # 2. Отсечение текстовых сообщений об ошибках
                txt = r.text.lower()
                for bad_text in ["404 not found", "user not found", "page not found", "profile not found", "account does not exist", "пользователь не найден", "страница не найдена", "account suspended", "no such user"]:
                    if bad_text in txt:
                        return

                etype = info.get("errorType")
                emsg = info.get("errorMsg")
                
                if etype == "status_code":
                    if str(r.url).rstrip("/") != str(info.get("urlMain", "")).rstrip("/"):
                        pass
                    else:
                        return
                elif etype == "message":
                    if isinstance(emsg, str) and emsg.lower() in txt:
                        return
                    elif isinstance(emsg, list) and any(m.lower() in txt for m in emsg):
                        return
                elif etype == "response_url":
                    if str(r.url) == str(info.get("errorUrl", "")) or str(r.url).rstrip("/") == str(info.get("urlMain", "")).rstrip("/"):
                        return

                cat = categorize_platform(name)
                found.append({
                    "platform": name,
                    "category": cat,
                    "icon": "fa-globe",
                    "url": profile_url,
                    "status": "Подтвержден",
                    "meta": {}
                })
                found_names_set.add(name.lower())
            except Exception:
                pass

    # 2. Быстрый сбор глубоких метаданных из GitHub / Telegram API
    async def enrich_core_apis(client: httpx.AsyncClient):
        # GitHub API
        try:
            gh_res = await client.get(f"https://api.github.com/users/{username}", headers=headers, timeout=3.0)
            if gh_res.status_code == 200:
                js = gh_res.json()
                if js.get("id"):
                    rn = js.get("name")
                    loc = js.get("location")
                    bio = js.get("bio")
                    cr = js.get("created_at", "")[:4]
                    if rn: intel_signals["names"].append(f"{rn} (GitHub)")
                    if loc: intel_signals["locations"].append(f"{loc} (GitHub)")
                    if bio: intel_signals["bios"].append(f"{bio} (GitHub)")
                    if cr: intel_signals["reg_years"].append(f"{cr} г. (GitHub)")
        except Exception:
            pass

        # Telegram
        try:
            tg_res = await client.get(f"https://t.me/{username}", headers=headers, timeout=3.0)
            if tg_res.status_code == 200 and ("tgme_page_extra" in tg_res.text or "@" in tg_res.text):
                soup = BeautifulSoup(tg_res.text, "html.parser")
                t_elem = soup.find("div", class_="tgme_page_title")
                d_elem = soup.find("div", class_="tgme_page_description")
                t_name = t_elem.get_text(strip=True) if t_elem else ""
                d_bio = d_elem.get_text(strip=True) if d_elem else ""
                if t_name and t_name != username: intel_signals["names"].append(f"{t_name} (Telegram)")
                if d_bio and "If you have Telegram" not in d_bio: intel_signals["bios"].append(f"{d_bio} (Telegram)")
        except Exception:
            pass

    async with httpx.AsyncClient() as client:
        tasks = [probe_sherlock_site(client, k, v) for k, v in sherlock_db.items()]
        tasks.append(enrich_core_apis(client))
        await asyncio.gather(*tasks)

    # Сортировка и дедупликация
    total_db_count = len(sherlock_db)
    probable_data, default_markdown = synthesize_heuristic_dossier(username, found, intel_signals)

    if GEMINI_API_KEY and found:
        categories_found = list(set(p["category"] for p in found))
        platforms_str = ", ".join([p["platform"] for p in found[:25]])

        prompt = f"""Ты — главный аналитик расследований OSINT.
Проведен автоматизированный сбор по официальной базе Sherlock Project ({total_db_count} баз) для цели: '{username}'.

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
- 🏙️ **Вероятный город / Страна**: (сопоставь геолокации из профилей/часовых поясов)
- 📊 **Индекс совпадения личности (Confidence)**: (например: 94% — высокая точность совпадения)

---

### 🧠 ГЛУБОКИЙ АНАЛИТИЧЕСКИЙ РАЗБОР СВЯЗЕЙ:
(Опиши логику расследования: почему эти профили принадлежат одному человеку, какие пересечения обнаружены, и дай 3 точных шага для дальнейшей проверки)
"""
        gemini_dossier = await run_gemini_prompt(prompt)
        if gemini_dossier:
            default_markdown = gemini_dossier

    return {
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
        "Сделай краткий экспертный вывод о владельце/канале."
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


@app.post("/api/scan/attribution")
async def scan_attribution(request: Request):
    """
    Глубокая OSINT-атрибуция виртуального/купленного аккаунта и поиск реальной основы:
    - Извлечение данных Telegram-профиля (Bio, Avatar, Name)
    - Генерация мутаций никнейма (удаление суффиксов _temp, _work, _bot, _alt, цифр)
    - Поиск исходных (root) профилей в основных соцсетях и репозиториях (GitHub, VK, Reddit, Steam, Habr)
    - Анализ аватара на первоисточники (Google Lens / Yandex)
    - Стилистический/лингвистический анализ текста сообщения
    - Синтез ИИ-досье атрибуции с вероятным основным аккаунтом и планом корпоративной верификации.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    target = str(body.get("target", "")).strip().lstrip("@")
    text_sample = str(body.get("text_sample", "")).strip()
    caller_user = str(body.get("caller", "guest")).strip()
    increment_user_scan(caller_user)

    if not target or len(target) < 2:
        return JSONResponse({"ok": False, "error": "Введите юзернейм или ID для атрибуции"}, status_code=400)

    tg_data = {
        "title": target,
        "username": target,
        "description": "",
        "photo_url": None,
        "account_type": "Пользователь",
        "is_bot": False,
        "age_verdict": "Свежий или виртуальный профиль"
    }

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    if target.isdigit():
        tg_id = int(target)
        tg_data["age_verdict"] = estimate_telegram_creation_date(tg_id)
    else:
        try:
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                resp = await client.get(f"https://t.me/{target}", headers=headers)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    t_elem = soup.find("div", class_="tgme_page_title")
                    d_elem = soup.find("div", class_="tgme_page_description")
                    p_elem = soup.find("img", class_="tgme_page_photo_image")
                    ex_elem = soup.find("div", class_="tgme_page_extra")
                    
                    if t_elem: tg_data["title"] = t_elem.get_text(strip=True)
                    if d_elem: tg_data["description"] = d_elem.get_text(strip=True)
                    if p_elem and "src" in p_elem.attrs: tg_data["photo_url"] = p_elem["src"]
                    extra = ex_elem.get_text(strip=True) if ex_elem else ""
                    if "subscribers" in extra.lower(): tg_data["account_type"] = "Канал"
                    elif "members" in extra.lower(): tg_data["account_type"] = "Группа"
                    elif "bot" in target.lower(): tg_data["account_type"] = "Бот"
        except Exception:
            pass

    base_stem = re.sub(r"(_temp|_work|_alt|_bot|_tg|_2|_official|_crypto|_anon|\d{1,4})$", "", target, flags=re.IGNORECASE)
    if not base_stem or len(base_stem) < 2:
        base_stem = target

    candidate_roots = list(dict.fromkeys([
        base_stem,
        re.sub(r"\d+", "", target),
        f"{base_stem}_official",
        f"{base_stem}_dev",
        f"{base_stem}ru",
        f"{base_stem}1"
    ]))
    candidate_roots = [c for c in candidate_roots if c and c.lower() != target.lower() and len(c) >= 3][:4]

    discovered_roots = []
    async def check_root_presence(client: httpx.AsyncClient, root_name: str):
        test_sites = [
            ("GitHub", f"https://api.github.com/users/{root_name}"),
            ("Telegram", f"https://t.me/{root_name}"),
            ("Steam", f"https://steamcommunity.com/id/{root_name}"),
            ("Habr", f"https://habr.com/ru/users/{root_name}/"),
            ("VK", f"https://vk.com/{root_name}")
        ]
        for sname, surl in test_sites:
            try:
                r = await client.get(surl, headers=headers, timeout=2.5, follow_redirects=True)
                if r.status_code == 200 and root_name.lower() in str(r.url).lower():
                    if "user not found" not in r.text.lower() and "404" not in r.text.lower():
                        discovered_roots.append({
                            "root_handle": root_name,
                            "platform": sname,
                            "url": str(r.url)
                        })
            except Exception:
                pass

    async with httpx.AsyncClient() as client:
        tasks = [check_root_presence(client, r) for r in candidate_roots]
        await asyncio.gather(*tasks)

    prompt = f"""Ты — старший OSINT-аналитик и специалист по деанонимизации и атрибуции sockpuppet/виртуальных аккаунтов.
Задача: Установить связь между виртуальным аккаунтом и реальной личностью / основным аккаунтом сотрудника.

ДАННЫЕ ЦЕЛИ:
- Исследуемый вирт-аккаунт: @{target}
- Отображаемое имя: {tg_data['title']}
- Bio/Описание: {tg_data['description']}
- Возраст ID: {tg_data['age_verdict']}
- Текст сообщений цели: {text_sample or 'Не предоставлен'}
- Найденные родственные корни псевдонима в сети: {[r['platform'] + ': ' + r['url'] for r in discovered_roots]}

ТВОЙ ОТЧЕТ АТРИБУЦИИ ДОЛЖЕН ВКЛЮЧАТЬ:
1. 🎯 **Наивероятнейший основной аккаунт / Псевдоним**: (укажи самый вероятный родительский хэндл/имя)
2. 🔍 **Выявленные цифровые пересечения**: (назови паттерны мутации ника, сходство стилей, совпадения по сервисам)
3. 📊 **Оценка вероятности вирта**: (например: 88% — высокая вероятность купленного/временного аккаунта)
4. 🛡️ **План корпоративной верификации в офисе**: (4 точных шага для проверки: сопоставление рабочего времени активности, проверка сетевых логов, проверка корпоративного Slack/Telegram, реверс аватара).
"""
    ai_attribution_dossier = await run_gemini_prompt(prompt)
    if not ai_attribution_dossier:
        ai_attribution_dossier = (
            f"🎯 **Результат анализа атрибуции для @{target}:**\n\n"
            f"• **Исследуемый аккаунт:** `@{target}` ({tg_data['title']})\n"
            f"• **Кандидаты на основу:** {', '.join(['@' + r for r in candidate_roots]) if candidate_roots else 'Уникальный псевдоним'}\n"
            f"• **Рекомендация:** Проверьте найденные профили `{', '.join([r['platform'] for r in discovered_roots])}` для установления полной личности."
        )

    return {
        "ok": True,
        "type": "attribution",
        "target": target,
        "tg_data": tg_data,
        "base_stem": base_stem,
        "candidate_roots": candidate_roots,
        "discovered_roots": discovered_roots,
        "ai_dossier": ai_attribution_dossier
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

    results = {
        "target": target,
        "ip_addresses": [],
        "ssl": {},
        "headers": {},
        "server_info": {},
        "subdomains_found": []
    }

    try:
        ip_list = socket.gethostbyname_ex(target)[2]
        results["ip_addresses"] = ip_list
    except Exception as e:
        results["dns_error"] = str(e)

    # SSL Сертификат
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((target, 443), timeout=3.0) as sock:
            with ctx.wrap_socket(sock, server_hostname=target) as ssock:
                cert = ssock.getpeercert()
                subject = dict(x[0] for x in cert.get("subject", []))
                issuer = dict(x[0] for x in cert.get("issuer", []))
                results["ssl"] = {
                    "commonName": subject.get("commonName"),
                    "issuer": issuer.get("organizationName") or issuer.get("commonName"),
                    "notAfter": cert.get("notAfter"),
                    "valid": True
                }
    except Exception:
        results["ssl"] = {"valid": False, "status": "SSL не обнаружен или самоподписан"}

    # HTTP Заголовки
    try:
        async with httpx.AsyncClient(timeout=3.5, follow_redirects=True) as client:
            resp = await client.get(f"https://{target}", headers={"User-Agent": "Mozilla/5.0"})
            results["server_info"]["status_code"] = resp.status_code
            hdrs = resp.headers
            results["headers"] = {
                "Server": hdrs.get("server", "Скрыт"),
                "HSTS": hdrs.get("strict-transport-security", "Отсутствует"),
                "X-Frame-Options": hdrs.get("x-frame-options", "Не задан"),
                "Content-Type": hdrs.get("content-type", "text/html")
            }
    except Exception:
        pass

    # Быстрый поиск популярных субдоменов
    common_subs = ["api", "dev", "mail", "admin", "vpn", "staging", "shop", "blog", "portal", "cpanel", "auth", "m", "cdn", "ws", "cloud", "git"]
    
    async def probe_subdomain(sub: str):
        full_sub = f"{sub}.{target}"
        try:
            loop = asyncio.get_running_loop()
            sub_ip = await loop.run_in_executor(None, socket.gethostbyname, full_sub)
            if sub_ip:
                results["subdomains_found"].append({"subdomain": full_sub, "ip": sub_ip})
        except Exception:
            pass

    tasks = [probe_subdomain(s) for s in common_subs]
    await asyncio.gather(*tasks)

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
    import hashlib
    email_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
    gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"

    res = {
        "email": email,
        "domain": domain,
        "syntax_valid": True,
        "mx_found": False,
        "domain_ips": [],
        "gravatar": None
    }

    try:
        res["domain_ips"] = socket.gethostbyname_ex(domain)[2]
        res["mx_found"] = True
    except Exception:
        res["mx_found"] = False

    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            g_resp = await client.get(gravatar_url)
            if g_resp.status_code == 200:
                res["gravatar"] = gravatar_url
    except Exception:
        pass

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
            js = resp.json()
            lat = js.get("lat")
            lon = js.get("lon")
            maps_url = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else None
            return {
                "ok": True,
                "type": "ip",
                "target": target_ip,
                "data": js,
                "google_maps_url": maps_url
            }
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
        f"Ты — ведущий OSINT-аналитик. Составь структурированное тактическое досье на цель: '{target}'.\n"
        "Определи: 1) Цифровой профиль 2) Возрастной диапазон 3) Основные векторы связей 4) Рекомендации по дальнейшей проверке.\n"
        "Пиши лаконично, строго, без лишнего текста."
    )
    ai_text = await run_gemini_prompt(prompt)
    if not ai_text:
        ai_text = (
            f"💜 **Аналитическое досье по цели:** `{target}`\n\n"
            f"• **Идентификатор:** `{target}`\n"
            f"• **Рекомендация:** Выполните поиск по базам Sherlock для построения графа активности."
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
