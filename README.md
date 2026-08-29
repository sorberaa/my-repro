# 🎯 OSINT LAB — Образовательный проект с Docker

Образовательный каталог OSINT-утилит, интерактивные учебные стенды и логирование IP визитов в админ-панель.

> ⚠️ **Это приложение предназначено ДЛЯ ОБРАЗОВАТЕЛЬНЫХ целей.** Живой запуск утилит против людей БЕЗ СОГЛАСИЯ запрещен.

## 📦 Что включено?

### 🔍 Интегрированные утилиты OSINT

| Категория | Утилита | Функция |
|-----------|---------|---------|
| 👤 **Username** | HandleHawk | Кросс-платформенный поиск по никнейму (Reddit, Mastodon, X, Nostr и т.д.) |
| 🌍 **IP Tracking** | TraxOsint | Полный анализ IP: геолокация, VPN, открытые порты, создание карт |
| 📄 **Метаданные** | MetaDetective | Извлечение EXIF, авторов, GPS, дат из документов и веб-скрейпинг |
| 🌐 **Веб-анализ** | WebCheck-OSINT | Анализ сайтов: SSL, DNS, TLS, технологический стек, угрозы |
| 📱 **Телефоны** | Ignorant | Проверка номера на Instagram, Snapchat, Amazon БЕЗ алертов |
| ☎️ **Информация о номере** | PhoneInfoga | Информация о сотовом операторе, стране, утечках |
| ✉️ **Email-восстановление** | Quidam | Восстановление email через "забытый пароль" на Twitter, Instagram, GitHub |
| 👥 **Профилирование** | DaProfiler | Сборка личности: адреса, соцсети, контакты (архивирован) |
| 🗺️ **Картографирование** | OSINT Mapping Tool | Интерактивная карта + граф для организации информации |
| ✈️ **Telegram** | TelegramDB | Индекс публичных каналов и групп Telegram |
| 📚 **Справочник** | NotLoBi CheatSheet | Полная шпаргалка OSINT по всем инструментам |

### 🧪 Учебные стенды

- **SQL Injection Lab**: Boolean-based, UNION-based, Time-based, OOB симуляции на локальных данных
- **IP Logging**: Логирование IP, браузера, геолокации всех визитов в панель

### 🔐 Админ-панель

- **Dashboard**: Статистика визитов (всего, уникальные IP, страны)
- **Таблица логов**: IP → Время → Страна → Path → User-Agent
- **JSON API**: `/admin/visits?token=ADMIN_TOKEN&limit=50`
- **HTML интерфейс**: `/admin/visits-html?token=ADMIN_TOKEN`

## 🚀 Быстрый старт

### Локально

```bash
# 1. Клонировать
git clone https://github.com/sorberaa/osint-bot.git
cd osint-bot

# 2. Подготовить конфиг
cp config/.env.example config/.env
# Отредактировать config/.env:
#   BOT_TOKEN=...          (от @BotFather)
#   ADMIN_CHAT_ID=...      (твой ID, узнаёшь от бота /id)
#   ADMIN_TOKEN=...        (для админ-панели)
#   DOMAIN=...             (твой домен или IP)

# 3. Запустить
mkdir -p data
docker compose up -d --build

# 4. Открыть в браузере
# http://localhost:8000
```

### На сервере с Cloudflare Tunnel

```bash
# В config/.env добавить:
CF_TUNNEL_TOKEN=ey...

docker compose up -d --build

# Бот доступен через WebApp
```

## 🔧 Конфигурация

### Переменные окружения (config/.env)

```bash
# Telegram Bot
BOT_TOKEN=123456789:ABCdeFg...           # От @BotFather
ADMIN_CHAT_ID=987654321                  # Твой Telegram ID
ADMIN_TOKEN=super_secret_panel_token     # Для админ-панели
DOMAIN=https://osint.example.com         # Домен (https, без /)

# Хранилище
DATA_DIR=/app/data                       # Папка логов

# Cloudflare (опционально)
CF_TUNNEL_TOKEN=ey...
```

## 📊 Админ-панель логирования

### Просмотр визитов

1. **Через бота** (быстро):
   ```
   /visits     # Последние 15 визитов в Telegram
   ```

2. **Через веб-интерфейс** (красиво):
   ```
   https://твой-домен.com/admin/visits-html?token=ADMIN_TOKEN
   ```

3. **JSON API**:
   ```
   GET /admin/visits?token=ADMIN_TOKEN&limit=100
   ```

### Логируется

- ✅ IP адрес (с поддержкой Cloudflare CF-Connecting-IP)
- ✅ User-Agent (браузер, ОС)
- ✅ Страна (Cloudflare CF-IPCountry)
- ✅ Дата/время (ISO 8601)
- ✅ Путь (page URL)
- ✅ Отправление уведомления в Telegram админу

## 📝 Структура проекта

```
osint-bot/
├── Dockerfile              # Python 3.11
├── docker-compose.yml      # Bot + Cloudflare Tunnel
├── entrypoint.sh          # Запуск приложения
├── requirements.txt       # Python зависимости
├── config/
│   └── .env.example       # Шаблон конфигурации
├── data/                  # Логи визитов (git ignore)
├── src/
│   ├── bot.py             # Telegram bot
│   ├── webapp.py          # FastAPI приложение + админ-панель
│   ├── catalog.py         # Каталог OSINT-утилит
│   └── entrypoint.sh      # Запуск скрипта
└── README.md
```

## 🛡️ Безопасность

- 🔒 `config/.env` не попадает в Git (`.gitignore`)
- 🔒 `data/` логи не пушатся
- 🔒 Админ-панель защищена `ADMIN_TOKEN`
- 🔒 Живой запуск утилит против людей отключен
- 🔒 Только HTTPS домены (требование Telegram WebApp)

## 🚀 Деплой

### На VPS через Cloudflare Tunnel

```bash
# 1. Получить токен на https://dash.cloudflare.com/
# 2. Вставить в config/.env
CF_TUNNEL_TOKEN=ey...

# 3. Запустить
docker compose up -d --build

# 4. Настроить Cloudflare Dashboard
# - CNAME: бот-домен → tunnel-uuid.cfargotunnels.com
```

### На GitHub Pages + Vercel (без запуска)

Только читай каталог — живого запуска нет.

## 📚 Примеры использования

### Просмотр каталога утилит

1. Откройте Telegram бота
2. Нажмите кнопку "Открыть OSINT Lab"
3. Выберите категорию (Username, IP, Email и т.д.)
4. Прочитайте описание утилиты и ссылку на GitHub

### SQL Injection Lab

```bash
curl -X POST http://localhost:8000/api/lab/sqli \
  -H "Content-Type: application/json" \
  -d '{"payload": "'\'' or '\''1'\''='\'1"}'
```

Ответ:
```json
{
  "tech": "Boolean-based SQLi",
  "explain": "Условие 1=1 всегда истинно. Учебная база вернула все строки.",
  "rows": [...]
}
```

### Проверка визитов

```bash
curl https://osint.example.com/admin/visits?token=ТВОЙ_ADMIN_TOKEN
```

## 📖 Документация утилит

- [HandleHawk](https://github.com/C3n7ral051nt4g3ncy/HandleHawk) — Username OSINT
- [TraxOsint](https://github.com/N0rz3/TraxOsint) — IP Geolocation  
- [MetaDetective](https://github.com/franckferman/MetaDetective) — Metadata extraction
- [WebCheck](https://github.com/mwakidenis/WebCheck-OSINT) — Website analysis
- [Ignorant](https://github.com/megadose/ignorant) — Phone number OSINT
- [Quidam](https://github.com/megadose/Quidam) — Email recovery
- [OSINT Mapping Tool](https://github.com/anonymousRAID/OSINT-Mapping-Tool) — Visual research

## ⚖️ Правовая информация

**Это приложение создано в образовательных целях.**

- ✋ Не использовать для шпионажа, преследования или хакинга
- ✋ Уважайте приватность людей
- ✋ Используйте только с согласия целевого человека
- ✋ Соблюдайте закон вашей страны

## 🤝 Контриб

Приветствуются:
- 🔧 Баг-репорты и фиксы
- 📚 Новые утилиты в каталог
- 📖 Улучшение документации
- 🎨 UI/UX улучшения

## 📄 Лицензия

MIT License — смотри [LICENSE](./LICENSE)

---

**Made with ❤️ for educational OSINT learning**
```
