import asyncio
import base64
import datetime
import hashlib
import io
import json
import logging
import math
import os
import random
import re
import secrets
import socket
import ssl
import string
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlsplit

import httpx
from bs4 import BeautifulSoup
import qrcode

logger = logging.getLogger("multitool")

# -------------------------------------------------------------
# 1. MEDIA DOWNLOADER (TikTok, Reels, YouTube Shorts, X/Twitter, etc.)
# -------------------------------------------------------------

DOWNLOAD_CACHE_DIR = Path(tempfile.gettempdir()) / "multitool_media"
DOWNLOAD_CACHE_DIR.mkdir(parents=True, exist_ok=True)
MAX_DOWNLOAD_BYTES = 45 * 1024 * 1024
DOWNLOAD_LINK_TTL_SECONDS = 30 * 60
_ALLOWED_MEDIA_DOMAINS = (
    "tiktok.com",
    "instagram.com",
    "youtube.com",
    "youtu.be",
    "pin.it",
    "pinterest.com",
    "twitter.com",
    "x.com",
    "reddit.com",
    "vk.com",
)
_download_links: dict[str, tuple[Path, float]] = {}


def _is_allowed_public_media_url(url: str) -> bool:
    try:
        parsed = urlsplit(url.strip())
        hostname = parsed.hostname
        port = parsed.port
    except (AttributeError, ValueError):
        return False

    if (
        parsed.scheme.lower() != "https"
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
    ):
        return False

    hostname = hostname.rstrip(".").lower()
    return any(
        hostname == domain or hostname.endswith(f".{domain}")
        for domain in _ALLOWED_MEDIA_DOMAINS
    )


def create_download_ticket(filepath: str) -> str:
    """Create a short-lived opaque URL token for a file in the media cache."""
    path = Path(filepath).resolve(strict=True)
    cache_dir = DOWNLOAD_CACHE_DIR.resolve()
    if path.parent != cache_dir or not path.is_file():
        raise ValueError("Download file is outside the media cache")

    now = time.time()
    for ticket, (old_path, expires_at) in list(_download_links.items()):
        if expires_at <= now:
            _download_links.pop(ticket, None)
            try:
                old_path.unlink(missing_ok=True)
            except OSError:
                pass

    ticket = secrets.token_urlsafe(24)
    _download_links[ticket] = (path, now + DOWNLOAD_LINK_TTL_SECONDS)
    return ticket


def resolve_download_ticket(ticket: str) -> Optional[Path]:
    """Resolve a short-lived download token without accepting filesystem paths."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{32}", ticket):
        return None

    entry = _download_links.get(ticket)
    if entry is None:
        return None

    path, expires_at = entry
    if expires_at <= time.time():
        _download_links.pop(ticket, None)
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        return None

    try:
        resolved = path.resolve(strict=True)
    except OSError:
        _download_links.pop(ticket, None)
        return None

    if resolved.parent != DOWNLOAD_CACHE_DIR.resolve() or not resolved.is_file():
        _download_links.pop(ticket, None)
        return None
    return resolved


class MediaDownloader:
    @staticmethod
    def is_media_url(url: str) -> bool:
        """Проверяет, является ли ссылка поддерживаемым медиа-ресурсом."""
        return _is_allowed_public_media_url(url)

    @staticmethod
    async def download_media(url: str, extract_audio: bool = False) -> Dict[str, Any]:
        """
        Скачивает медиа по ссылке без водяных знаков с помощью yt-dlp.
        Возвращает метаданные и путь к скачанному файлу.
        """
        if not MediaDownloader.is_media_url(url):
            return {
                "ok": False,
                "error": "Используйте общедоступную HTTPS-ссылку с поддерживаемой платформы.",
            }

        import yt_dlp

        # Очистка старых временных файлов (старше 2 часов)
        now = time.time()
        for f in DOWNLOAD_CACHE_DIR.glob("*"):
            try:
                if f.is_file() and now - f.stat().st_mtime > 7200:
                    f.unlink(missing_ok=True)
            except Exception:
                pass

        file_id = f"media_{int(time.time())}_{secrets.token_hex(4)}"
        out_tmpl = str(DOWNLOAD_CACHE_DIR / f"{file_id}.%(ext)s")

        ydl_opts: Dict[str, Any] = {
            "outtmpl": out_tmpl,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "max_filesize": MAX_DOWNLOAD_BYTES,
            "socket_timeout": 20,
            "retries": 1,
            "fragment_retries": 1,
        }

        if extract_audio:
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            })
        else:
            # Универсальный безопасный формат: mp4 с видео и аудио
            ydl_opts.update({
                "format": "best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
            })

        loop = asyncio.get_running_loop()

        def _run_ydl():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if "entries" in info:
                    info = info["entries"][0]
                filename = ydl.prepare_filename(info)
                if extract_audio and not filename.endswith(".mp3"):
                    filename = os.path.splitext(filename)[0] + ".mp3"
                return info, filename

        try:
            info, filepath = await loop.run_in_executor(None, _run_ydl)
            
            # Если файл с другим расширением был создан
            p = Path(filepath)
            if not p.exists():
                matching = list(DOWNLOAD_CACHE_DIR.glob(f"{file_id}.*"))
                if matching:
                    p = matching[0]

            p = p.resolve(strict=True)
            if p.parent != DOWNLOAD_CACHE_DIR.resolve() or not p.is_file():
                return {"ok": False, "error": "Скачанный файл не найден в кэше."}

            filesize = p.stat().st_size
            if filesize > MAX_DOWNLOAD_BYTES:
                p.unlink(missing_ok=True)
                return {
                    "ok": False,
                    "error": "Файл превышает допустимый размер 45 МБ.",
                }

            return {
                "ok": True,
                "title": info.get("title") or "Медиафайл",
                "duration": info.get("duration") or 0,
                "uploader": info.get("uploader") or info.get("channel") or "Unknown",
                "filesize": filesize,
                "filepath": str(p),
                "is_audio": extract_audio,
            }
        except Exception as e:
            logger.warning("Media download failed (%s)", type(e).__name__)
            return {
                "ok": False,
                "error": "Не удалось скачать файл. Проверьте доступность ссылки и попробуйте ещё раз."
            }


# -------------------------------------------------------------
# 2. TEMP MAIL SERVICE (mail.tm - мгновенная одноразовая почта)
# -------------------------------------------------------------

class TempMailService:
    API_BASE = "https://api.mail.tm"

    @classmethod
    async def create_inbox(cls) -> Dict[str, Any]:
        """Создает новый временный ящик и возвращает токен доступа."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Получаем активный домен
            dom_res = await client.get(f"{cls.API_BASE}/domains")
            domains = dom_res.json().get("hydra:member", [])
            if not domains:
                return {"ok": False, "error": "Нет доступных почтовых доменов"}

            chosen_domain = domains[0]["domain"]
            username = "box_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
            address = f"{username}@{chosen_domain}"
            password = f"P@{secrets.token_hex(6)}!"

            # Создаем аккаунт
            acc_res = await client.post(
                f"{cls.API_BASE}/accounts",
                json={"address": address, "password": password}
            )
            if acc_res.status_code not in (200, 201):
                return {"ok": False, "error": "Не удалось зарегистрировать почтовый ящик"}

            # Получаем JWT токен
            tok_res = await client.post(
                f"{cls.API_BASE}/token",
                json={"address": address, "password": password}
            )
            data = tok_res.json()
            token = data.get("token")

            return {
                "ok": True,
                "email": address,
                "password": password,
                "token": token,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }

    @classmethod
    async def get_messages(cls, token: str) -> Dict[str, Any]:
        """Возвращает список сообщений для данного токена ящика."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{cls.API_BASE}/messages",
                headers={"Authorization": f"Bearer {token}"}
            )
            if res.status_code != 200:
                return {"ok": False, "messages": [], "error": f"HTTP {res.status_code}"}

            items = res.json().get("hydra:member", [])
            messages = []
            for m in items:
                messages.append({
                    "id": m.get("id"),
                    "from": m.get("from", {}).get("address"),
                    "subject": m.get("subject", "Без темы"),
                    "intro": m.get("intro", ""),
                    "created_at": m.get("createdAt")
                })
            return {"ok": True, "messages": messages, "count": len(messages)}

    @classmethod
    async def get_message_detail(cls, token: str, message_id: str) -> Dict[str, Any]:
        """Получает полный текст письма."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{cls.API_BASE}/messages/{message_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if res.status_code != 200:
                return {"ok": False, "error": f"HTTP {res.status_code}"}

            data = res.json()
            return {
                "ok": True,
                "id": data.get("id"),
                "from": data.get("from", {}).get("address"),
                "subject": data.get("subject"),
                "text": data.get("text") or "",
                "html": data.get("html") or "",
                "created_at": data.get("createdAt")
            }


# -------------------------------------------------------------
# 3. DEV & CYBER SECURITY UTILITIES
# -------------------------------------------------------------

class DevSecurityTools:
    @staticmethod
    def generate_password(
        length: int = 16,
        use_upper: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True
    ) -> Dict[str, Any]:
        """Генерирует криптографически стойкий пароль с расчетом энтропии."""
        length = max(8, min(64, length))
        chars = string.ascii_lowercase
        if use_upper:
            chars += string.ascii_uppercase
        if use_digits:
            chars += string.digits
        if use_symbols:
            chars += "!@#$%^&*()-_=+[]{}<>?"

        pwd = "".join(secrets.choice(chars) for _ in range(length))
        pool_size = len(chars)
        entropy = math.log2(pool_size ** length)

        strength = "Слабый"
        if entropy > 80:
            strength = "Очень надежный (Военный класс)"
        elif entropy > 60:
            strength = "Высокий"
        elif entropy > 45:
            strength = "Средний"

        return {
            "ok": True,
            "password": pwd,
            "length": length,
            "entropy_bits": round(entropy, 1),
            "strength": strength
        }

    @staticmethod
    def cyber_decode(action: str, data: str) -> Dict[str, Any]:
        """Универсальный кибер-декодер и инспектор токенов/хешей."""
        data = (data or "").strip()
        try:
            if action == "base64_encode":
                res = base64.b64encode(data.encode("utf-8")).decode("utf-8")
                return {"ok": True, "result": res}
            elif action == "base64_decode":
                # Добиваем padding если нужно
                pad = len(data) % 4
                if pad:
                    data += "=" * (4 - pad)
                res = base64.b64decode(data).decode("utf-8", errors="replace")
                return {"ok": True, "result": res}
            elif action == "hex_encode":
                res = data.encode("utf-8").hex()
                return {"ok": True, "result": res}
            elif action == "hex_decode":
                res = bytes.fromhex(data.replace(" ", "")).decode("utf-8", errors="replace")
                return {"ok": True, "result": res}
            elif action == "hashes":
                b = data.encode("utf-8")
                return {
                    "ok": True,
                    "md5": hashlib.md5(b).hexdigest(),
                    "sha1": hashlib.sha1(b).hexdigest(),
                    "sha256": hashlib.sha256(b).hexdigest(),
                    "sha512": hashlib.sha512(b).hexdigest()
                }
            elif action == "jwt_inspect":
                parts = data.split(".")
                if len(parts) < 2:
                    return {"ok": False, "error": "Неверный формат JWT (ожидается header.payload.signature)"}
                
                def _b64_url_decode(s):
                    s += "=" * ((4 - len(s) % 4) % 4)
                    return json.loads(base64.urlsafe_b64decode(s).decode("utf-8"))

                header = _b64_url_decode(parts[0])
                payload = _b64_url_decode(parts[1])
                return {
                    "ok": True,
                    "header": header,
                    "payload": payload,
                    "is_expired": (payload.get("exp") and payload.get("exp") < time.time())
                }
            else:
                return {"ok": False, "error": f"Неизвестное действие: {action}"}
        except Exception as e:
            return {"ok": False, "error": f"Ошибка декодирования: {str(e)}"}

    @staticmethod
    async def probe_website(target: str) -> Dict[str, Any]:
        """
        Проверяет доступность веб-сайта, код ответа, заголовки безопасности
        и срок действия SSL-сертификата.
        """
        clean = re.sub(r"^https?://", "", target.strip()).split("/")[0].split(":")[0]
        url = f"https://{clean}"
        http_url = f"http://{clean}"

        res_data: Dict[str, Any] = {
            "ok": True,
            "host": clean,
            "ip": "Unknown",
            "ssl_valid": False,
            "ssl_days_left": None,
            "http_status": None,
            "server": "Unknown",
            "security_headers": {},
            "response_time_ms": 0
        }

        # 1. DNS Lookup
        loop = asyncio.get_running_loop()
        try:
            ip = await loop.run_in_executor(None, socket.gethostbyname, clean)
            res_data["ip"] = ip
        except Exception:
            pass

        # 2. SSL Check
        def _check_ssl():
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=clean) as s:
                s.settimeout(5.0)
                s.connect((clean, 443))
                cert = s.getpeercert()
                not_after = cert["notAfter"]
                exp_date = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=datetime.timezone.utc)
                now = datetime.datetime.now(datetime.timezone.utc)
                days_left = (exp_date - now).days
                issuer = dict(x[0] for x in cert.get("issuer", ()))
                return True, days_left, issuer.get("organizationName", "Verified CA")

        try:
            valid, days, issuer = await loop.run_in_executor(None, _check_ssl)
            res_data["ssl_valid"] = valid
            res_data["ssl_days_left"] = days
            res_data["ssl_issuer"] = issuer
        except Exception as e:
            res_data["ssl_error"] = str(e)

        # 3. HTTP Probe
        t0 = time.time()
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                resp = await client.get(url)
                res_data["http_status"] = resp.status_code
                res_data["response_time_ms"] = int((time.time() - t0) * 1000)
                res_data["server"] = resp.headers.get("server", "Protected")
                
                # Анализ заголовков безопасности
                headers = resp.headers
                res_data["security_headers"] = {
                    "Strict-Transport-Security (HSTS)": "strict-transport-security" in headers,
                    "Content-Security-Policy (CSP)": "content-security-policy" in headers,
                    "X-Frame-Options": "x-frame-options" in headers,
                    "X-Content-Type-Options": "x-content-type-options" in headers,
                }
        except Exception:
            # Fallback HTTP
            try:
                async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                    resp = await client.get(http_url)
                    res_data["http_status"] = resp.status_code
                    res_data["response_time_ms"] = int((time.time() - t0) * 1000)
                    res_data["server"] = resp.headers.get("server", "Protected")
            except Exception as e:
                res_data["http_error"] = str(e)

        return res_data

    @staticmethod
    def generate_qr(text: str) -> bytes:
        """Создает PNG изображение QR-кода."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#000000", back_color="#ffffff")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()


# -------------------------------------------------------------
# 4. AI & PRODUCTIVITY HUB (Summarizer & Web Extractor)
# -------------------------------------------------------------

class AIProductivity:
    @staticmethod
    async def summarize_page_or_text(target: str) -> Dict[str, Any]:
        """
        Читает содержимое ссылки или текст и формирует структурированный TL;DR дайджест.
        """
        text = target.strip()
        title = "Текстовая выжимка"

        if target.startswith("http://") or target.startswith("https://"):
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    resp = await client.get(target, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                    soup = BeautifulSoup(resp.text, "html.parser")
                    if soup.title:
                        title = soup.title.string.strip()
                    
                    # Удаляем скрипты и стили
                    for tag in soup(["script", "style", "nav", "footer", "header"]):
                        tag.decompose()
                    
                    paragraphs = [p.get_text(strip=True) for p in soup.find_all(["p", "h1", "h2", "article"]) if len(p.get_text(strip=True)) > 40]
                    text = "\n".join(paragraphs[:30])
            except Exception as e:
                return {"ok": False, "error": f"Не удалось прочесть страницу: {e}"}

        if len(text) < 50:
            return {"ok": False, "error": "Слишком короткий текст для анализа"}

        # Извлечение ключевых тезисов (эвристический NLP дайджест)
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 35]
        
        # Выбираем наиболее информативные предложения
        key_points = []
        for s in sentences:
            if any(k in s.lower() for k in ["главн", "итог", "потому", "важн", "показал", "утвержда", "сообщ", "отмет", "вывод", "перв"]):
                key_points.append(s)
            if len(key_points) >= 5:
                break

        if len(key_points) < 3:
            key_points = sentences[:5]

        return {
            "ok": True,
            "title": title,
            "char_count": len(text),
            "key_takeaways": key_points[:5],
            "reading_time_mins": max(1, round(len(text.split()) / 180))
        }
