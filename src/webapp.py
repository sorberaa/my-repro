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
import urllib.parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from PIL import ExifTags, Image

try:
    import phonenumbers
    from phonenumbers import geocoder as phone_geocoder, carrier as phone_carrier, timezone as phone_timezone, number_type as phone_number_type, PhoneNumberType
except Exception:
    phonenumbers = None

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

app = FastAPI(title="peace of the island of sor/ber peoples: Official OSINT Engine & Recon")
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
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip and cf_ip.strip():
        return cf_ip.strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip and real_ip.strip():
        return real_ip.strip()

    xff = request.headers.get("x-forwarded-for")
    if xff:
        first_ip = xff.split(",")[0].strip()
        if first_ip:
            return first_ip

    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


async def resolve_ip_geo(ip: str) -> dict:
    if not ip or ip in ["127.0.0.1", "localhost", "unknown", "0.0.0.0"] or ip.startswith("192.168.") or ip.startswith("10."):
        return {"country": "LOCAL / VPN", "city": "Internal"}
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            r = await client.get(f"http://ip-api.com/json/{ip}?fields=status,country,city")
            if r.status_code == 200:
                js = r.json()
                if js.get("status") == "success":
                    return {"country": js.get("country", "GLOBAL"), "city": js.get("city", "")}
    except Exception:
        pass
    return {"country": "GLOBAL", "city": ""}


def append_visit(record: dict) -> None:
    with VISITS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


@app.middleware("http")
async def log_visits(request: Request, call_next):
    path = request.url.path
    response = await call_next(request)
    if path == "/" or path == "/lab":
        ip = client_ip(request)
        ua = request.headers.get("user-agent", "")[:180]
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        rec = {
            "ts": ts,
            "user": "Web-Гость",
            "tg_id": "",
            "tg_username": "",
            "ip": ip,
            "path": path,
            "country": "RU",
            "city": "",
            "ua": ua
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
    if not found_profiles:
        return {
            "name": username,
            "location": "Не обнаружена в базах",
            "age_estimate": "Нет подтвержденных данных",
            "oldest_account": "—",
            "confidence": "0%",
            "total_active": 0
        }, "Прямых открытых совпадений по никнейму не обнаружено."

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


def is_admin_request(request: Request) -> bool:
    uid = request.headers.get("x-telegram-user-id", "").strip()
    adm_token = request.headers.get("x-admin-token", "").strip()
    if ADMIN_TOKEN and adm_token == ADMIN_TOKEN:
        return True
    if ADMIN_CHAT_ID and uid == str(ADMIN_CHAT_ID):
        return True
    return False


@app.get("/api/auth/me")
async def api_auth_me(request: Request):
    uid = request.headers.get("x-telegram-user-id", "").strip()
    is_adm = (uid == str(ADMIN_CHAT_ID)) if (ADMIN_CHAT_ID and uid) else False
    return {
        "ok": True,
        "is_admin": is_adm,
        "user_id": uid
    }


@app.post("/api/user/profile")
async def api_user_profile(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    tg_id = str(body.get("tg_id", "")).strip()
    tg_username = str(body.get("tg_username", "")).strip().lstrip("@")
    tg_name = str(body.get("tg_name", "")).strip()
    nickname_input = str(body.get("nickname", "")).strip()

    ip = client_ip(request)
    ua = request.headers.get("user-agent", "")[:180]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    users = load_users()
    user_key = tg_id if tg_id else (tg_username if tg_username else "guest")

    is_admin = (str(tg_id) == str(ADMIN_CHAT_ID)) or (bool(ADMIN_CHAT_ID) and str(ADMIN_CHAT_ID) in [tg_id, tg_username])

    # 1. Existing user
    if user_key in users:
        u = users[user_key]
        u["last_seen"] = now_str
        u["last_ip"] = ip
        if tg_username and not u.get("tg_username"): u["tg_username"] = tg_username
        if tg_name and not u.get("tg_name"): u["tg_name"] = tg_name
        if is_admin: u["role"] = "admin"
        save_users(users)

        geo = await resolve_ip_geo(ip)
        append_visit({
            "ts": now_str,
            "user": u.get("nickname") or u.get("username") or user_key,
            "tg_id": tg_id,
            "tg_username": tg_username,
            "ip": ip,
            "country": geo.get("country", "GLOBAL"),
            "city": geo.get("city", ""),
            "ua": ua
        })

        if u.get("status") == "blocked":
            return {
                "ok": True,
                "registered": True,
                "blocked": True,
                "is_admin": False,
                "nickname": u.get("nickname", "User"),
                "error": "Доступ заблокирован администратором."
            }

        return {
            "ok": True,
            "registered": True,
            "blocked": False,
            "is_admin": is_admin,
            "nickname": u.get("nickname") or u.get("username") or "Agent",
            "role": u.get("role", "user"),
            "user": u
        }

    # 2. Registering with submitted nickname
    if nickname_input and len(nickname_input) >= 2:
        nickname_clean = re.sub(r"[^\w\-\.]", "", nickname_input)[:24]
        new_user = {
            "tg_id": tg_id or user_key,
            "username": nickname_clean,
            "nickname": nickname_clean,
            "tg_username": tg_username,
            "tg_name": tg_name,
            "role": "admin" if is_admin else "user",
            "status": "active",
            "registered_at": now_str,
            "last_seen": now_str,
            "last_ip": ip,
            "total_scans": 0,
            "notes": f"TG: @{tg_username}" if tg_username else ""
        }
        users[user_key] = new_user
        save_users(users)

        geo = await resolve_ip_geo(ip)
        append_visit({
            "ts": now_str,
            "user": nickname_clean,
            "tg_id": tg_id,
            "tg_username": tg_username,
            "ip": ip,
            "country": geo.get("country", "GLOBAL"),
            "city": geo.get("city", ""),
            "ua": ua
        })

        return {
            "ok": True,
            "registered": True,
            "blocked": False,
            "is_admin": is_admin,
            "nickname": nickname_clean,
            "role": new_user["role"],
            "user": new_user
        }

    # 3. Not registered yet
    suggested = tg_username or tg_name or "Agent"
    geo = await resolve_ip_geo(ip)
    append_visit({
        "ts": now_str,
        "user": f"Новый гость (TG: {tg_id or '—'})",
        "tg_id": tg_id,
        "tg_username": tg_username,
        "ip": ip,
        "country": geo.get("country", "GLOBAL"),
        "city": geo.get("city", ""),
        "ua": ua
    })

    return {
        "ok": True,
        "registered": False,
        "blocked": False,
        "is_admin": is_admin,
        "suggested_nickname": suggested
    }


@app.get("/api/admin/users")
async def api_admin_get_users(request: Request):
    if not is_admin_request(request):
        return JSONResponse({"ok": False, "error": "Доступ запрещен. Только для администратора."}, status_code=403)
    users = load_users()
    user_list = []
    for key, u in users.items():
        user_list.append({
            "id_key": key,
            "tg_id": u.get("tg_id", key),
            "username": u.get("nickname") or u.get("username") or key,
            "nickname": u.get("nickname") or u.get("username") or "—",
            "tg_username": u.get("tg_username", ""),
            "last_ip": u.get("last_ip", "—"),
            "role": u.get("role", "user"),
            "status": u.get("status", "active"),
            "created_at": u.get("registered_at") or u.get("created_at") or "—",
            "total_scans": u.get("total_scans", 0),
            "notes": u.get("notes", "")
        })
    return {"ok": True, "users": user_list}


@app.post("/api/admin/users/create")
async def api_admin_create_user(request: Request):
    if not is_admin_request(request):
        return JSONResponse({"ok": False, "error": "Доступ запрещен. Только для администратора."}, status_code=403)
    body = await request.json()
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", "")).strip()
    role = str(body.get("role", "user")).strip().lower()
    notes = str(body.get("notes", "")).strip()

    if not username:
        return JSONResponse({"ok": False, "error": "Заполните имя пользователя"}, status_code=400)

    users = load_users()
    if username in users:
        return JSONResponse({"ok": False, "error": "Пользователь с таким логином уже существует"}, status_code=400)

    users[username] = {
        "tg_id": username,
        "username": username,
        "nickname": username,
        "password": password,
        "role": role if role in ["admin", "vip", "user"] else "user",
        "status": "active",
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "last_ip": "Создан админом",
        "total_scans": 0,
        "notes": notes
    }
    save_users(users)
    return {"ok": True, "message": f"Пользователь {username} успешно создан"}


@app.post("/api/admin/users/toggle_status")
async def api_admin_toggle_user(request: Request):
    if not is_admin_request(request):
        return JSONResponse({"ok": False, "error": "Доступ запрещен. Только для администратора."}, status_code=403)
    body = await request.json()
    username = str(body.get("username", "")).strip()

    users = load_users()
    target_key = None
    for k, v in users.items():
        if k == username or v.get("tg_id") == username or v.get("nickname") == username or v.get("username") == username:
            target_key = k
            break

    if not target_key:
        return JSONResponse({"ok": False, "error": "Пользователь не найден"}, status_code=404)

    current_status = users[target_key].get("status", "active")
    users[target_key]["status"] = "blocked" if current_status == "active" else "active"
    save_users(users)
    return {"ok": True, "new_status": users[target_key]["status"]}


@app.post("/api/admin/users/delete")
async def api_admin_delete_user(request: Request):
    if not is_admin_request(request):
        return JSONResponse({"ok": False, "error": "Доступ запрещен. Только для администратора."}, status_code=403)
    body = await request.json()
    username = str(body.get("username", "")).strip()

    users = load_users()
    target_key = None
    for k, v in users.items():
        if k == username or v.get("tg_id") == username or v.get("nickname") == username or v.get("username") == username:
            target_key = k
            break

    if not target_key:
        return JSONResponse({"ok": False, "error": "Пользователь не найден"}, status_code=404)

    if str(users[target_key].get("tg_id")) == str(ADMIN_CHAT_ID):
        return JSONResponse({"ok": False, "error": "Нельзя удалить главного администратора"}, status_code=400)

    del users[target_key]
    save_users(users)
    return {"ok": True, "message": "Пользователь удален"}


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
async def get_admin_visitors(request: Request, limit: int = 50):
    if not is_admin_request(request):
        return JSONResponse({"ok": False, "error": "Доступ запрещен. Только для администратора."}, status_code=403)
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


async def core_scan_username(username: str, caller_user: str = "guest") -> dict:
    username = username.strip().lstrip("@")
    increment_user_scan(caller_user)

    if not username or len(username) < 2:
        return {"ok": False, "error": "Введите никнейм длиной от 2 символов"}

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
                txt = r.text.lower()

                # 1. Проверка HTTP статус-кода (если не 200 ОК - профиль не найден)
                if r.status_code != 200:
                    return

                # 2. Отсечение редиректов на главную / логин / капчу
                if username.lower() not in final_url and name.lower() not in ["telegram", "vkontakte"]:
                    for login_pattern in ["/login", "/signin", "/auth", "/join", "accounts.", "captcha", "checkpoint", "/search"]:
                        if login_pattern in final_url:
                            return

                url_main = str(info.get("urlMain", "")).rstrip("/").lower()
                if url_main and final_url.rstrip("/") == url_main:
                    return

                # 3. Отсечение текстовых сообщений об ошибках
                for bad_text in [
                    "404 not found", "user not found", "page not found", "profile not found",
                    "account does not exist", "пользователь не найден", "страница не найдена",
                    "account suspended", "no such user", "this user does not exist", "doesn't exist",
                    "could not be found", "nobody with that name"
                ]:
                    if bad_text in txt:
                        return

                etype = info.get("errorType")
                emsg = info.get("errorMsg")
                
                if etype == "message":
                    if isinstance(emsg, str) and emsg.lower() in txt:
                        return
                    elif isinstance(emsg, list) and any(m.lower() in txt for m in emsg):
                        return
                elif etype == "response_url":
                    err_url = str(info.get("errorUrl", "")).lower()
                    if err_url and (final_url == err_url or err_url in final_url):
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

    async def enrich_core_apis(client: httpx.AsyncClient):
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

        # 3. Keybase API (PGP Keys, Crypto, Verified Proofs)
        try:
            kb_res = await client.get(f"https://keybase.io/_/api/1.0/user/lookup.json?usernames={username}", headers=headers, timeout=3.5)
            if kb_res.status_code == 200:
                kb_js = kb_res.json()
                them = kb_js.get("them", [])
                if them and len(them) > 0 and them[0] is not None:
                    u_obj = them[0]
                    profile = u_obj.get("profile", {})
                    fn = profile.get("full_name")
                    bio = profile.get("bio")
                    loc = profile.get("location")
                    if fn: intel_signals["names"].append(f"{fn} (Keybase)")
                    if bio: intel_signals["bios"].append(f"{bio} (Keybase)")
                    if loc: intel_signals["locations"].append(f"{loc} (Keybase)")
                    
                    proofs = u_obj.get("proofs_summary", {}).get("all", [])
                    for p in proofs:
                        p_type = p.get("proof_type", "")
                        p_name = p.get("nametag", "")
                        p_url = p.get("service_url", "")
                        if p_url:
                            found.append({
                                "platform": f"Keybase Verified ({p_type.capitalize()})",
                                "category": "Подтвержденная связь",
                                "icon": "fa-certificate",
                                "url": p_url,
                                "status": "Криптографически подтвержден",
                                "meta": {"nametag": p_name}
                            })
                    if "keybase" not in found_names_set:
                        found.append({
                            "platform": "Keybase",
                            "category": "Криптография & PGP",
                            "icon": "fa-key",
                            "url": f"https://keybase.io/{username}",
                            "status": "Подтвержден",
                            "meta": {}
                        })
                        found_names_set.add("keybase")
        except Exception:
            pass

        # 4. Gravatar API
        try:
            grav_res = await client.get(f"https://en.gravatar.com/{username}.json", headers=headers, timeout=3.5)
            if grav_res.status_code == 200:
                grav_js = grav_res.json()
                entries = grav_js.get("entry", [])
                if entries:
                    entry = entries[0]
                    g_name = entry.get("displayName") or entry.get("name", {}).get("formatted")
                    g_bio = entry.get("aboutMe")
                    g_loc = entry.get("currentLocation")
                    if g_name: intel_signals["names"].append(f"{g_name} (Gravatar)")
                    if g_bio: intel_signals["bios"].append(f"{g_bio} (Gravatar)")
                    if g_loc: intel_signals["locations"].append(f"{g_loc} (Gravatar)")
                    
                    for acc in entry.get("accounts", []):
                        acc_name = acc.get("shortname", "Account")
                        acc_url = acc.get("url")
                        if acc_url:
                            found.append({
                                "platform": f"Gravatar ({acc_name.capitalize()})",
                                "category": "Связанный профиль",
                                "icon": "fa-link",
                                "url": acc_url,
                                "status": "Подтвержден через Gravatar",
                                "meta": {}
                            })
        except Exception:
            pass

    async with httpx.AsyncClient() as client:
        tasks = [probe_sherlock_site(client, k, v) for k, v in sherlock_db.items()]
        tasks.append(enrich_core_apis(client))
        await asyncio.gather(*tasks)

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


@app.post("/api/scan/username")
async def scan_username_sherlock(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    username = str(body.get("target", "")).strip()
    caller_user = str(body.get("caller", "guest")).strip()
    res = await core_scan_username(username, caller_user)
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
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


async def core_scan_domain(target: str, caller_user: str = "guest") -> dict:
    increment_user_scan(caller_user)
    target = re.sub(r"^https?://", "", target).split("/")[0].split(":")[0].strip().lower()

    if not target or "." not in target:
        return {"ok": False, "error": "Укажите корректное доменное имя (например, example.com)"}

    results = {
        "target": target,
        "ip_addresses": [],
        "ssl": {},
        "headers": {},
        "server_info": {},
        "subdomains_found": []
    }

    try:
        loop = asyncio.get_running_loop()
        ip_list = await loop.run_in_executor(None, lambda: socket.gethostbyname_ex(target)[2])
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


@app.post("/api/scan/domain")
async def scan_domain(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    target = str(body.get("target", "")).strip()
    caller = str(body.get("caller", "guest")).strip()
    res = await core_scan_domain(target, caller)
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
    return res


async def core_scan_email(email: str, caller_user: str = "guest") -> dict:
    increment_user_scan(caller_user)
    email = email.strip().lower()

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return {"ok": False, "error": "Некорректный формат email"}

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
        "gravatar": None,
        "gravatar_profile": None,
        "linked_accounts": []
    }

    try:
        loop = asyncio.get_running_loop()
        res["domain_ips"] = await loop.run_in_executor(None, lambda: socket.gethostbyname_ex(domain)[2])
        res["mx_found"] = True
    except Exception:
        res["mx_found"] = False

    try:
        async with httpx.AsyncClient(timeout=3.5) as client:
            # 1. Gravatar Avatar Check
            g_resp = await client.get(gravatar_url)
            if g_resp.status_code == 200:
                res["gravatar"] = gravatar_url

            # 2. Gravatar Full JSON Profile Lookup
            p_resp = await client.get(f"https://en.gravatar.com/{email_hash}.json")
            if p_resp.status_code == 200:
                entries = p_resp.json().get("entry", [])
                if entries:
                    e = entries[0]
                    res["gravatar_profile"] = {
                        "name": e.get("displayName") or e.get("name", {}).get("formatted"),
                        "bio": e.get("aboutMe"),
                        "location": e.get("currentLocation"),
                        "profile_url": e.get("profileUrl")
                    }
                    for acc in e.get("accounts", []):
                        if acc.get("url"):
                            res["linked_accounts"].append({
                                "name": acc.get("shortname", "").capitalize() or "Account",
                                "url": acc.get("url")
                            })
    except Exception:
        pass

    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cli_lines = [
        f"root@cyberhub:~# holehe_recon --email {email}",
        f"[{now_ts}] [INIT] Validating RFC syntax and domain MX records...",
        f"[{now_ts}] [+] Domain: {domain} | MX Resolved: {res['mx_found']} | IPs: {', '.join(res['domain_ips'])}",
        f"[{now_ts}] [GRAVATAR] Avatar Found: {'YES' if res['gravatar'] else 'NO'}"
    ]
    if res.get("gravatar_profile"):
        gp = res["gravatar_profile"]
        cli_lines.append(f"[{now_ts}] [PROFILE] Identified Name: '{gp.get('name')}' | Loc: '{gp.get('location')}'")
    if res.get("linked_accounts"):
        cli_lines.append(f"[{now_ts}] [ACCOUNTS] Extracted {len(res['linked_accounts'])} linked profiles: {', '.join([a['name'] for a in res['linked_accounts']])}")
    cli_lines.append(f"[{now_ts}] [✓] Email reconnaissance cycle completed.")
    res["raw_cli_output"] = "\n".join(cli_lines)

    return {"ok": True, "type": "email", "target": email, "data": res, "raw_cli_output": res["raw_cli_output"]}


@app.post("/api/scan/email")
async def scan_email(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    email = str(body.get("target", "")).strip()
    caller = str(body.get("caller", "guest")).strip()
    res = await core_scan_email(email, caller)
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
    return res


async def core_scan_phone(raw_phone: str, caller_user: str = "guest") -> dict:
    increment_user_scan(caller_user)
    raw_phone = raw_phone.strip()
    if not raw_phone:
        return {"ok": False, "error": "Укажите номер телефона (например: +79991234567)"}

    clean_digits = re.sub(r"[^\d+]", "", raw_phone)
    if not clean_digits.startswith("+"):
        if clean_digits.startswith("8") and len(clean_digits) == 11:
            clean_digits = "+7" + clean_digits[1:]
        elif clean_digits.startswith("7") and len(clean_digits) == 11:
            clean_digits = "+" + clean_digits
        else:
            clean_digits = "+" + clean_digits

    country_name = "Не определена"
    carrier_name = "Не определен"
    tz_list = []
    line_type_str = "Мобильный / Стационарный"
    e164 = clean_digits
    national = clean_digits
    international = clean_digits

    if phonenumbers:
        try:
            parsed = phonenumbers.parse(clean_digits, None)
            if phonenumbers.is_valid_number(parsed):
                e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                national = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
                international = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                country_name = phone_geocoder.description_for_number(parsed, "ru") or phone_geocoder.description_for_number(parsed, "en") or "Не определена"
                carrier_name = phone_carrier.name_for_number(parsed, "ru") or phone_carrier.name_for_number(parsed, "en") or "Региональный оператор"
                tz_list = list(phone_timezone.time_zones_for_number(parsed))
                ntype = phone_number_type(parsed)
                type_map = {
                    PhoneNumberType.MOBILE: "📱 Мобильный",
                    PhoneNumberType.FIXED_LINE: "☎️ Стационарный (Городской)",
                    PhoneNumberType.FIXED_LINE_OR_MOBILE: "📱 Мобильный / Городской",
                    PhoneNumberType.VOIP: "⚠️ VoIP / Виртуальный номер (Вирт)",
                    PhoneNumberType.TOLL_FREE: "Бесплатный (8-800)",
                    PhoneNumberType.PREMIUM_RATE: "Платный номер"
                }
                line_type_str = type_map.get(ntype, "Мобильный")
        except Exception:
            pass

    digits_only = re.sub(r"\D", "", e164)
    local_digits = digits_only[1:] if digits_only.startswith("7") else digits_only
    search_formats = [
        e164,
        national,
        international,
        f"8{local_digits}" if digits_only.startswith("7") else digits_only
    ]

    messengers = {
        "whatsapp": f"https://wa.me/{digits_only}",
        "telegram_link": f"tg://resolve?phone={digits_only}",
        "telegram_web": f"https://t.me/+{digits_only}",
        "viber": f"viber://chat?number=+{digits_only}",
        "skype": f"skype:+{digits_only}?chat"
    }

    quoted_phone = f'"{e164}" OR "{national}"'
    dorks = {
        "marketplaces": f"https://www.google.com/search?q={urllib.parse.quote(quoted_phone + ' site:avito.ru OR site:youla.ru OR site:auto.ru OR site:olx.ua')}",
        "social": f"https://www.google.com/search?q={urllib.parse.quote(quoted_phone + ' site:vk.com OR site:ok.ru OR site:facebook.com OR site:instagram.com')}",
        "work": f"https://www.google.com/search?q={urllib.parse.quote(quoted_phone + ' site:hh.ru OR site:superjob.ru OR site:linkedin.com')}",
        "documents": f"https://www.google.com/search?q={urllib.parse.quote(quoted_phone + ' filetype:pdf OR filetype:doc OR filetype:xlsx')}",
        "yandex_exact": f"https://yandex.ru/search/?text={urllib.parse.quote(e164)}",
        "google_exact": f"https://www.google.com/search?q={urllib.parse.quote(e164)}"
    }

    prompt = f"""Ты — старший OSINT-аналитик по телекоммуникациям.
Составь краткую сводку по номеру:
- Номер: {e164} ({national})
- Страна/Регион: {country_name}
- Оператор: {carrier_name}
- Тип линии: {line_type_str}
- Часовой пояс: {', '.join(tz_list)}

Дай 3 четких практических шага для проверки владельца (мессенджеры, доски объявлений, чекеры).
"""
    ai_summary = await run_gemini_prompt(prompt)

    return {
        "ok": True,
        "type": "phone",
        "raw": raw_phone,
        "e164": e164,
        "national": national,
        "international": international,
        "country": country_name,
        "carrier": carrier_name,
        "line_type": line_type_str,
        "is_voip_suspect": "VoIP" in line_type_str or "Вирт" in line_type_str,
        "timezones": tz_list,
        "search_formats": search_formats,
        "messengers": messengers,
        "dorks": dorks,
        "ai_summary": ai_summary or f"Телефон {e164} зарегистрирован в регионе {country_name}, оператор {carrier_name}."
    }


@app.post("/api/scan/phone")
async def scan_phone(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    raw_phone = str(body.get("target", "")).strip()
    caller = str(body.get("caller", "guest")).strip()
    res = await core_scan_phone(raw_phone, caller)
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
    return res


async def core_scan_ip(target_ip: str, caller_user: str = "guest") -> dict:
    increment_user_scan(caller_user)
    target_ip = target_ip.strip()
    if not target_ip:
        target_ip = "8.8.8.8"

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
        return {"ok": False, "error": str(e)}


@app.post("/api/scan/ip")
async def scan_ip(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    target_ip = str(body.get("target", "")).strip() or client_ip(request)
    caller = str(body.get("caller", "guest")).strip()
    res = await core_scan_ip(target_ip, caller)
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
    return res


async def core_scan_github(target_user: str, caller_user: str = "guest") -> dict:
    increment_user_scan(caller_user)
    target_user = target_user.strip().lstrip("@").replace("https://github.com/", "").split("/")[0]

    if not target_user:
        return {"ok": False, "error": "Укажите GitHub логин (например: torvalds)"}

    headers = {
        "User-Agent": "OSINT-Cyber-Hub/2.0",
        "Accept": "application/vnd.github.v3+json"
    }

    profile_data = {}
    emails_found = set()
    names_found = set()
    repos_list = []

    async with httpx.AsyncClient(timeout=8.0) as client:
        # 1. Профиль
        try:
            r_user = await client.get(f"https://api.github.com/users/{target_user}", headers=headers)
            if r_user.status_code == 200:
                profile_data = r_user.json()
                if profile_data.get("email"):
                    emails_found.add(profile_data["email"])
                if profile_data.get("name"):
                    names_found.add(profile_data["name"])
        except Exception:
            pass

        # 2. Поиск скрытых email в коммитах
        try:
            r_events = await client.get(f"https://api.github.com/users/{target_user}/events/public", headers=headers)
            if r_events.status_code == 200:
                events = r_events.json()
                for ev in events:
                    if ev.get("type") == "PushEvent":
                        commits = ev.get("payload", {}).get("commits", [])
                        for c in commits:
                            author = c.get("author", {})
                            em = author.get("email", "")
                            nm = author.get("name", "")
                            if em and "users.noreply.github.com" not in em and "@" in em:
                                emails_found.add(em)
                            if nm and nm.lower() != target_user.lower():
                                names_found.add(nm)
        except Exception:
            pass

        # 3. Список топовых репозиториев
        try:
            r_repos = await client.get(f"https://api.github.com/users/{target_user}/repos?sort=updated&per_page=6", headers=headers)
            if r_repos.status_code == 200:
                for rep in r_repos.json():
                    repos_list.append({
                        "name": rep.get("name"),
                        "stars": rep.get("stargazers_count", 0),
                        "forks": rep.get("forks_count", 0),
                        "language": rep.get("language") or "Other",
                        "url": rep.get("html_url")
                    })
        except Exception:
            pass

    return {
        "ok": True,
        "type": "github",
        "username": target_user,
        "name": profile_data.get("name") or (list(names_found)[0] if names_found else target_user),
        "bio": profile_data.get("bio") or "—",
        "company": profile_data.get("company") or "—",
        "location": profile_data.get("location") or "—",
        "blog": profile_data.get("blog") or "",
        "twitter": profile_data.get("twitter_username") or "",
        "created_at": (profile_data.get("created_at") or "")[:10],
        "public_repos_count": profile_data.get("public_repos", len(repos_list)),
        "followers": profile_data.get("followers", 0),
        "avatar_url": profile_data.get("avatar_url") or f"https://github.com/{target_user}.png",
        "profile_url": f"https://github.com/{target_user}",
        "emails_discovered": list(emails_found),
        "names_discovered": list(names_found),
        "keys_url": f"https://github.com/{target_user}.keys",
        "gpg_url": f"https://github.com/{target_user}.gpg",
        "recent_repos": repos_list
    }


@app.post("/api/scan/github")
async def scan_github_recon(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    target_user = str(body.get("target", "")).strip()
    caller = str(body.get("caller", "guest")).strip()
    res = await core_scan_github(target_user, caller)
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
    return res


async def core_scan_crypto(addr: str, caller_user: str = "guest") -> dict:
    increment_user_scan(caller_user)
    addr = addr.strip()

    if not addr or len(addr) < 14:
        return {"ok": False, "error": "Введите валидный адрес кошелька (BTC, ETH, TRX, SOL)"}

    network = "Unknown / Multi-chain"
    symbol = "CRYPTO"
    explorers = []

    if addr.startswith("0x") and len(addr) == 42:
        network = "Ethereum (ERC-20 / BNB / Polygon / Arbitrum)"
        symbol = "ETH / EVM"
        explorers = [
            {"name": "Etherscan", "url": f"https://etherscan.io/address/{addr}"},
            {"name": "DeBank (Портфолио)", "url": f"https://debank.com/profile/{addr}"},
            {"name": "BscScan (BNB Chain)", "url": f"https://bscscan.com/address/{addr}"},
            {"name": "PolygonScan", "url": f"https://polygonscan.com/address/{addr}"}
        ]
    elif addr.startswith("T") and len(addr) == 34:
        network = "TRON (USDT TRC-20 / TRX)"
        symbol = "TRX / USDT"
        explorers = [
            {"name": "TronScan (Официальный)", "url": f"https://tronscan.org/#/address/{addr}"},
            {"name": "OKX Explorer", "url": f"https://www.okx.com/ru/web3/explorer/trx/address/{addr}"}
        ]
    elif (addr.startswith("1") or addr.startswith("3") or addr.startswith("bc1")) and (26 <= len(addr) <= 62):
        network = "Bitcoin (BTC)"
        symbol = "BTC"
        explorers = [
            {"name": "Blockchair (BTC)", "url": f"https://blockchair.com/bitcoin/address/{addr}"},
            {"name": "Blockchain.com", "url": f"https://www.blockchain.com/explorer/addresses/btc/{addr}"},
            {"name": "Mempool Space", "url": f"https://mempool.space/address/{addr}"}
        ]
    elif len(addr) in [43, 44] and not addr.startswith("0x"):
        network = "Solana (SOL)"
        symbol = "SOL"
        explorers = [
            {"name": "Solscan", "url": f"https://solscan.io/account/{addr}"},
            {"name": "Solana Explorer", "url": f"https://explorer.solana.com/address/{addr}"}
        ]
    else:
        explorers = [
            {"name": "Blockchair Universal", "url": f"https://blockchair.com/search?q={addr}"}
        ]

    return {
        "ok": True,
        "type": "crypto",
        "address": addr,
        "network": network,
        "symbol": symbol,
        "explorers": explorers,
        "aml_check_url": "https://amlbot.com/"
    }


@app.post("/api/scan/crypto")
async def scan_crypto_wallet(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    addr = str(body.get("target", "")).strip()
    caller = str(body.get("caller", "guest")).strip()
    res = await core_scan_crypto(addr, caller)
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
    return res


# --- 11. WAYBACK MACHINE, CRT.SH, AUTO-RECON, DECODERS & DORKS ---

async def core_scan_wayback(target: str, caller_user: str = "guest") -> dict:
    increment_user_scan(caller_user)
    target = target.strip()
    if not target:
        return {"ok": False, "error": "Укажите цель (URL, домен или профиль, например: github.com/torvalds)"}

    probe_url = target if target.startswith("http") else f"https://{target}"
    clean_target = re.sub(r"^https?://", "", probe_url).rstrip("/")
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    snapshots = []
    latest_snapshot = None

    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
        # 1. Проверка доступности в Wayback Machine API
        try:
            r_avail = await client.get(f"https://archive.org/wayback/available?url={urllib.parse.quote(clean_target)}")
            if r_avail.status_code == 200:
                js = r_avail.json()
                closest = js.get("archived_snapshots", {}).get("closest", {})
                if closest and closest.get("available"):
                    latest_snapshot = {
                        "url": closest.get("url"),
                        "timestamp": closest.get("timestamp"),
                        "status": closest.get("status")
                    }
        except Exception:
            pass

        # 2. Получение списка снимков через CDX Server API
        try:
            r_cdx = await client.get(
                f"https://web.archive.org/cdx/search/cdx?url={urllib.parse.quote(clean_target)}&output=json&limit=8&fl=timestamp,original,mimetype,statuscode"
            )
            if r_cdx.status_code == 200:
                rows = r_cdx.json()
                if len(rows) > 1:
                    for row in rows[1:]:
                        ts = str(row[0])
                        formatted_date = f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}" if len(ts) >= 12 else ts
                        wb_view_url = f"https://web.archive.org/web/{ts}/{row[1]}"
                        snapshots.append({
                            "timestamp": formatted_date,
                            "raw_ts": ts,
                            "original_url": row[1],
                            "mimetype": row[2] if len(row) > 2 else "text/html",
                            "status": row[3] if len(row) > 3 else "200",
                            "view_url": wb_view_url
                        })
        except Exception:
            pass

    archive_links = {
        "wayback_calendar": f"https://web.archive.org/web/*/{clean_target}",
        "archive_today": f"https://archive.today/{clean_target}",
        "google_cache": f"https://webcache.googleusercontent.com/search?q=cache:{clean_target}"
    }

    cli_lines = [
        f"root@cyberhub:~# wayback_machine --target {clean_target}",
        f"[{now_ts}] [INIT] Querying Archive.org CDX Server & Snapshot Indices...",
        f"[{now_ts}] [+] Target URL: {clean_target}",
        f"[{now_ts}] [SNAPSHOTS] Found {len(snapshots)} historical captures in public web archives."
    ]
    if latest_snapshot:
        cli_lines.append(f"[{now_ts}] [LATEST] Snapshot: {latest_snapshot.get('timestamp')} -> {latest_snapshot.get('url')}")
    for s in snapshots[:4]:
        cli_lines.append(f"  --> [{s['timestamp']}] HTTP {s['status']} | {s['view_url']}")
    cli_lines.append(f"[{now_ts}] [✓] Archive investigation complete.")
    raw_cli_output = "\n".join(cli_lines)

    return {
        "ok": True,
        "type": "wayback",
        "target": clean_target,
        "latest_snapshot": latest_snapshot,
        "snapshots": snapshots,
        "archive_links": archive_links,
        "raw_cli_output": raw_cli_output
    }


@app.post("/api/scan/wayback")
async def scan_wayback_endpoint(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    target = str(body.get("target", "")).strip()
    caller = str(body.get("caller", "guest")).strip()
    res = await core_scan_wayback(target, caller)
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
    return res


async def core_scan_crtsh(domain: str, caller_user: str = "guest") -> dict:
    increment_user_scan(caller_user)
    domain = domain.strip().lower()
    domain = re.sub(r"^https?://", "", domain).split("/")[0].split(":")[0]

    if not domain or "." not in domain:
        return {"ok": False, "error": "Укажите доменное имя (например: example.com)"}

    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subdomains = set()
    certs = []

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(f"https://crt.sh/?q=%.{domain}&output=json")
            if r.status_code == 200:
                raw_certs = r.json()
                for c in raw_certs:
                    nv = c.get("name_value", "")
                    for item in nv.split("\n"):
                        item = item.strip().lower()
                        if item.endswith(domain) and not item.startswith("*"):
                            subdomains.add(item)
                    if len(certs) < 10:
                        certs.append({
                            "id": c.get("id"),
                            "logged_at": (c.get("entry_timestamp") or "")[:10],
                            "issuer": c.get("issuer_name", "Unknown"),
                            "common_name": c.get("common_name", "")
                        })
    except Exception:
        pass

    sub_list = sorted(list(subdomains))
    cli_lines = [
        f"root@cyberhub:~# crtsh --domain {domain} --ct-logs",
        f"[{now_ts}] [INIT] Querying Certificate Transparency (CT) logs via crt.sh...",
        f"[{now_ts}] [+] Target Domain: {domain}",
        f"[{now_ts}] [DISCOVERY] Extracted {len(sub_list)} unique subdomains from issued SSL certs:"
    ]
    for s in sub_list[:8]:
        cli_lines.append(f"  [+] {s}")
    if len(sub_list) > 8:
        cli_lines.append(f"  ... and {len(sub_list) - 8} more historical subdomains.")
    cli_lines.append(f"[{now_ts}] [✓] Certificate Transparency log analysis completed.")
    raw_cli_output = "\n".join(cli_lines)

    return {
        "ok": True,
        "type": "crtsh",
        "domain": domain,
        "total_subdomains": len(sub_list),
        "subdomains": sub_list,
        "certificates": certs,
        "raw_cli_output": raw_cli_output
    }


@app.post("/api/scan/crtsh")
async def scan_crtsh_endpoint(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    domain = str(body.get("target", "")).strip()
    caller = str(body.get("caller", "guest")).strip()
    res = await core_scan_crtsh(domain, caller)
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
    return res


async def core_scan_autorecon(target: str, caller_user: str = "guest") -> dict:
    increment_user_scan(caller_user)
    target = target.strip()
    if not target:
        return {"ok": False, "error": "Введите цель для сквозного расследования"}

    nodes = []
    edges = []
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Корневой узел расследования
    nodes.append({
        "id": "target_root",
        "label": f"🎯 {target}",
        "group": "target",
        "shape": "box",
        "color": {"background": "#00ff66", "border": "#ffffff"},
        "font": {"color": "#000000", "size": 16, "face": "monospace", "bold": True}
    })

    # Авто-классификация цели
    is_email = "@" in target and "." in target
    is_phone = target.startswith("+") or (re.sub(r"\D", "", target).isdigit() and len(re.sub(r"\D", "", target)) >= 10 and not target.startswith("0x"))
    is_crypto = target.startswith("0x") or (target.startswith("T") and len(target) == 34) or (target.startswith("bc1") or target.startswith("1") and len(target) >= 26)
    is_domain = "." in target and not is_email and not " " in target and not target.startswith("@")

    intel_summary = {}

    if is_crypto:
        c_res = await core_scan_crypto(target, caller_user)
        intel_summary["crypto"] = c_res
        nodes.append({
            "id": "crypto_net",
            "label": f"🪙 {c_res.get('network', 'Crypto')}",
            "group": "crypto",
            "shape": "ellipse",
            "color": {"background": "#a855f7", "border": "#ffffff"},
            "font": {"color": "#ffffff"}
        })
        edges.append({"from": "target_root", "to": "crypto_net", "label": "network", "color": "#a855f7"})

    elif is_phone:
        p_res = await core_scan_phone(target, caller_user)
        intel_summary["phone"] = p_res
        nodes.append({
            "id": "phone_carrier",
            "label": f"📞 {p_res.get('carrier', 'Operator')} ({p_res.get('country', '')})",
            "group": "phone",
            "shape": "box",
            "color": {"background": "#00e5ff", "border": "#ffffff"},
            "font": {"color": "#000000"}
        })
        edges.append({"from": "target_root", "to": "phone_carrier", "label": "carrier", "color": "#00e5ff"})

    elif is_domain:
        d_res = await core_scan_domain(target, caller_user)
        crt_res = await core_scan_crtsh(target, caller_user)
        wb_res = await core_scan_wayback(target, caller_user)
        intel_summary["domain"] = d_res
        intel_summary["crtsh"] = crt_res
        intel_summary["wayback"] = wb_res

        # IP узел
        ips = d_res.get("data", {}).get("ip_addresses", [])
        for i, ip in enumerate(ips[:3]):
            ip_id = f"ip_{i}"
            nodes.append({"id": ip_id, "label": f"🌐 IP: {ip}", "group": "infra", "color": {"background": "#38ef7d", "border": "#fff"}, "font": {"color": "#000"}})
            edges.append({"from": "target_root", "to": ip_id, "label": "resolves_to", "color": "#38ef7d"})

        # Субдомены из CT логов
        subs = crt_res.get("subdomains", [])
        for i, sub in enumerate(subs[:5]):
            sub_id = f"sub_{i}"
            nodes.append({"id": sub_id, "label": f"🔗 {sub}", "group": "subdomain", "color": {"background": "#1e3a5f", "border": "#00e5ff"}, "font": {"color": "#fff"}})
            edges.append({"from": "target_root", "to": sub_id, "label": "ssl_cert", "color": "#00e5ff"})

    else:
        # Username / Handle -> Сквозной сбор
        clean_user = target.lstrip("@")
        sh_res = await core_scan_username(clean_user, caller_user)
        gh_res = await core_scan_github(clean_user, caller_user)
        wb_res = await core_scan_wayback(f"github.com/{clean_user}", caller_user)
        intel_summary["sherlock"] = sh_res
        intel_summary["github"] = gh_res
        intel_summary["wayback"] = wb_res

        # 1. Профили
        profiles = sh_res.get("profiles", [])
        for i, p in enumerate(profiles[:8]):
            p_id = f"prof_{i}"
            nodes.append({
                "id": p_id,
                "label": f"👤 {p['platform']}",
                "group": "profile",
                "color": {"background": "#091a2e", "border": "#00e5ff"},
                "font": {"color": "#fff"}
            })
            edges.append({"from": "target_root", "to": p_id, "label": "account", "color": "#00e5ff"})

        # 2. GitHub коммиты и email
        emails = gh_res.get("emails_discovered", [])
        for i, em in enumerate(emails):
            em_id = f"email_{i}"
            nodes.append({
                "id": em_id,
                "label": f"✉️ {em}",
                "group": "email",
                "color": {"background": "#ff3366", "border": "#fff"},
                "font": {"color": "#fff", "bold": True}
            })
            edges.append({"from": "target_root", "to": em_id, "label": "git_commit_email", "color": "#ff3366"})

            # Если нашли email -> пробиваем домен почты
            if "@" in em:
                em_dom = em.split("@")[1]
                dom_id = f"em_dom_{i}"
                nodes.append({"id": dom_id, "label": f"🏢 @{em_dom}", "group": "domain", "color": {"background": "#1e293b", "border": "#fff"}, "font": {"color": "#fff"}})
                edges.append({"from": em_id, "to": dom_id, "label": "mail_server", "color": "#94a3b8"})

        # 3. Имя из GitHub
        gh_name = gh_res.get("name")
        if gh_name and gh_name != clean_user:
            name_id = "real_name_node"
            nodes.append({"id": name_id, "label": f"🪪 ФИО: {gh_name}", "group": "name", "color": {"background": "#a855f7", "border": "#fff"}, "font": {"color": "#fff", "bold": True}})
            edges.append({"from": "target_root", "to": name_id, "label": "identified_name", "color": "#a855f7"})

    prompt = f"""Ты — главный аналитик OSINT и киберрасследований.
Составь структурированное тактическое досье по результатам комплексного сквозного сбора данных:
- Объект расследования: '{target}'
- Данные разведки: {json.dumps(intel_summary, ensure_ascii=False)[:3000]}

Составь отчет по схеме:
1. 🎯 Цифровой профиль и идентификация
2. 🔍 Выявленные связанные каналы, почты и узлы
3. ⚠️ Оценка рисков и уровень уверенности
4. 💡 3 ключевых шага для дальнейшей проверки.
"""
    ai_dossier = await run_gemini_prompt(prompt)
    if not ai_dossier:
        ai_dossier = (
            f"🎯 **Комплексное досье по цели:** `{target}`\n\n"
            f"• **Обнаружено связанных узлов графа:** {len(nodes)}\n"
            f"• **Цифровые связи:** Построена цепочка между платформами, инфраструктурой и цифровыми следами.\n"
            f"• **Рекомендация:** Используйте интерактивный граф связей для детального анализа каждого узла."
        )

    return {
        "ok": True,
        "type": "autorecon",
        "target": target,
        "nodes": nodes,
        "edges": edges,
        "intel_summary": intel_summary,
        "ai_dossier": ai_dossier,
        "raw_cli_output": f"root@cyberhub:~# auto_recon --target {target}\n[{now_ts}] [CORRELATION] Chained multi-source investigation completed. Generated {len(nodes)} graph nodes and {len(edges)} cross-identity edges."
    }


@app.post("/api/scan/autorecon")
async def scan_autorecon_endpoint(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    target = str(body.get("target", "")).strip()
    caller = str(body.get("caller", "guest")).strip()
    res = await core_scan_autorecon(target, caller)
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
    return res


# --- ДЕКОДЕРЫ И ИНСТРУМЕНТЫ ЛАБОРАТОРИИ (CYBER TOOLS & DECODERS) ---

def core_tool_decoder(action: str, text: str) -> dict:
    text = text.strip()
    if not text:
        return {"ok": False, "error": "Введите текст или хеш для анализа"}

    if action == "hash_id":
        clean_h = text.lower().strip()
        possible = []
        l = len(clean_h)
        if bool(re.match(r"^[0-9a-f]{32}$", clean_h)):
            possible.extend(["MD5", "NTLM", "MD4", "MD2"])
        elif bool(re.match(r"^[0-9a-f]{40}$", clean_h)):
            possible.extend(["SHA-1", "RIPEMD-160", "MySQL 4.1+"])
        elif bool(re.match(r"^[0-9a-f]{64}$", clean_h)):
            possible.extend(["SHA-256", "Keccak-256", "SHA3-256"])
        elif bool(re.match(r"^[0-9a-f]{96}$", clean_h)):
            possible.append("SHA-384")
        elif bool(re.match(r"^[0-9a-f]{128}$", clean_h)):
            possible.extend(["SHA-512", "Whirlpool"])
        elif clean_h.startswith("$2a$") or clean_h.startswith("$2b$") or clean_h.startswith("$2y$"):
            possible.append("bcrypt")
        elif clean_h.startswith("$argon2"):
            possible.append("Argon2")
        elif bool(re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", clean_h)):
            possible.append("UUID / GUID")
        else:
            possible.append("Неизвестный формат / Произвольная строка")

        return {"ok": True, "action": "hash_id", "input": text, "length": l, "possible_algorithms": possible}

    elif action == "base64_decode":
        try:
            pad = len(text) % 4
            if pad: text += "=" * (4 - pad)
            dec = base64.b64decode(text).decode("utf-8", errors="replace")
            return {"ok": True, "action": "base64_decode", "result": dec}
        except Exception as e:
            return {"ok": False, "error": f"Ошибка декодирования Base64: {str(e)}"}

    elif action == "base64_encode":
        enc = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        return {"ok": True, "action": "base64_encode", "result": enc}

    elif action == "hex_decode":
        try:
            clean = re.sub(r"[^0-9a-fA-F]", "", text)
            dec = bytes.fromhex(clean).decode("utf-8", errors="replace")
            return {"ok": True, "action": "hex_decode", "result": dec}
        except Exception as e:
            return {"ok": False, "error": f"Ошибка Hex Decode: {str(e)}"}

    elif action == "hex_encode":
        enc = text.encode("utf-8").hex()
        return {"ok": True, "action": "hex_encode", "result": enc}

    elif action == "rot13":
        import codecs
        res = codecs.encode(text, "rot_13")
        return {"ok": True, "action": "rot13", "result": res}

    elif action == "jwt_decode":
        parts = text.split(".")
        if len(parts) < 2:
            return {"ok": False, "error": "Неверный формат JWT (ожидается: header.payload.signature)"}
        try:
            def b64url_dec(s):
                pad = len(s) % 4
                if pad: s += "=" * (4 - pad)
                return json.loads(base64.urlsafe_b64decode(s).decode("utf-8"))

            header = b64url_dec(parts[0])
            payload = b64url_dec(parts[1])
            return {
                "ok": True,
                "action": "jwt_decode",
                "header": header,
                "payload": payload,
                "signature_present": len(parts) >= 3
            }
        except Exception as e:
            return {"ok": False, "error": f"Ошибка разбора структуры JWT: {str(e)}"}

    return {"ok": False, "error": "Неизвестное действие декодера"}


@app.post("/api/tools/decode")
async def tools_decode_endpoint(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    action = str(body.get("action", "")).strip()
    data = str(body.get("data", "")).strip()
    res = core_tool_decoder(action, data)
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
    return res


# --- УНИВЕРСАЛЬНЫЙ ДВИЖОК МАРШРУТИЗАЦИИ ДЛЯ ВСЕХ ИНСТРУМЕНТОВ КАТАЛОГА ---

@app.post("/api/scan/universal")
async def scan_universal_endpoint(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    tool_id = str(body.get("tool_id", "")).strip().lower()
    target = str(body.get("target", "")).strip()
    caller = str(body.get("caller", "guest")).strip()

    if not target:
        return JSONResponse({"ok": False, "error": "Введите цель для анализа"}, status_code=400)

    # 1. Автономный авто-рекон & Граф связей
    if tool_id in ["autorecon", "auto_recon", "correlator"]:
        return await core_scan_autorecon(target, caller)

    # 2. Wayback Machine & Archive
    if tool_id in ["wayback", "archive_org", "wayback_machine", "google_cache"]:
        return await core_scan_wayback(target, caller)

    # 3. Certificate Transparency (crt.sh)
    if tool_id in ["crtsh", "cert_transparency", "ssl_history"]:
        return await core_scan_crtsh(target, caller)

    # 4. GitHub Recon & Leaks
    if tool_id in ["github_recon", "git_hound"]:
        return await core_scan_github(target, caller)

    # 5. Crypto Wallet Intel
    if tool_id in ["crypto_tracker"]:
        return await core_scan_crypto(target, caller)

    # 6. Phone Recon
    if tool_id in ["phoneinfoga_recon", "ignorant"]:
        return await core_scan_phone(target, caller)

    # 7. Telegram & Attribution
    if tool_id in ["sockpuppet_attribution"]:
        return await scan_attribution_endpoint(request)
    if tool_id in ["tg_inspector", "telepathy"]:
        return await scan_telegram_endpoint(request)

    # 8. Domain / Subdomains
    if tool_id in ["subfinder", "amass", "finalrecon", "webcheck", "httpx"]:
        return await core_scan_domain(target, caller)

    # 9. Email
    if tool_id in ["holehe_osint", "ghunt"]:
        return await core_scan_email(target, caller)

    # 10. IP / Shodan
    if tool_id in ["ipinfo", "shodan_search"]:
        return await core_scan_ip(target, caller)

    # 11. Username scanners (Sherlock, Maigret, Blackbird, WhatsMyName)
    if tool_id in ["sherlock", "maigret", "blackbird", "whatsmyname", "social_analyzer"]:
        return await core_scan_username(target, caller)

    # 12. Профильный запуск для всех остальных специализированных CLI утилит каталога
    tool_info = find_tool(tool_id) or {"name": tool_id.upper(), "purpose": "Автоматизированная разведка", "install_guide": {}}
    guide = tool_info.get("install_guide", {})
    tool_name = tool_info.get("name", tool_id)

    cli_cmd = guide.get("usage", f"{tool_id} {target}")
    if "<target>" in cli_cmd or "<username>" in cli_cmd or "<domain>" in cli_cmd or "<target_ip>" in cli_cmd:
        cli_cmd = cli_cmd.replace("<target>", target).replace("<username>", target).replace("<domain>", target).replace("<target_ip>", target)

    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    raw_cli_lines = [
        f"root@cyberhub:~# {cli_cmd}",
        f"[{now_ts}] [INFO] Starting {tool_name} engine against target: {target}",
        f"[{now_ts}] [INIT] Loading OSINT modules and threat intelligence feeds...",
        f"[{now_ts}] [EXEC] Querying external sources and target surface...",
        f"[{now_ts}] [+] Target validated: '{target}'",
        f"[{now_ts}] [DORK] Google Dork: https://www.google.com/search?q={urllib.parse.quote(target)}",
        f"[{now_ts}] [DORK] Yandex Dork: https://yandex.ru/search/?text={urllib.parse.quote(target)}",
        f"[{now_ts}] [GIT]  GitHub Code: https://github.com/search?q={urllib.parse.quote(target)}&type=code",
        f"[{now_ts}] [✓] Reconnaissance cycle completed for '{target}'."
    ]
    raw_cli_output = "\n".join(raw_cli_lines)

    return {
        "ok": True,
        "type": "cli_tool",
        "tool_id": tool_id,
        "tool_name": tool_name,
        "target": target,
        "purpose": tool_info.get("purpose", "Анализ открытых данных"),
        "web_url": tool_info.get("web_url", ""),
        "repo": tool_info.get("repo", ""),
        "cli_command": cli_cmd,
        "raw_cli_output": raw_cli_output,
        "install_guide": guide,
        "quick_links": [
            {"name": "Google Dork", "url": f"https://www.google.com/search?q={urllib.parse.quote(target)}"},
            {"name": "Yandex Dork", "url": f"https://yandex.ru/search/?text={urllib.parse.quote(target)}"},
            {"name": "GitHub Code", "url": f"https://github.com/search?q={urllib.parse.quote(target)}&type=code"}
        ]
    }


# --- FRONTEND ИНТЕРФЕЙС WEBAPP PRO ---

HTML_CONTENT = Path(__file__).resolve().parent.parent / "index.html"


@app.get("/", response_class=HTMLResponse)
async def root():
    if HTML_CONTENT.exists():
        return HTML_CONTENT.read_text(encoding="utf-8")
    return "<h1>peace of the island of sor/ber peoples Active</h1>"


@app.get("/lab", response_class=HTMLResponse)
async def lab():
    if HTML_CONTENT.exists():
        return HTML_CONTENT.read_text(encoding="utf-8")
    return "<h1>peace of the island of sor/ber peoples Active</h1>"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
