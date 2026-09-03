"""
Каталог OSINT-инструментов с GitHub, расширенными возможностями Telegram-разведки,
GeoINT, поиском по соцсетям, инструкциями и запуском в WebApp.
"""

CATALOG = [
    {
        "id": "killer_monetization",
        "title": "💎 AI-Профайлинг, Шпион активности & AML Аудит (Premium)",
        "desc": "Высокоточные интеллектуальные модули: генерация психологических досье через нейросети, трекинг активности, AML-аудит криптовалют и Face AI.",
        "tools": [
            {
                "id": "ai_detective_profiler",
                "name": "🧠 AI Detective Profiler & Досье (Scam Score)",
                "repo": "https://github.com/sherlock-project/sherlock",
                "web_url": "",
                "purpose": "🎯 Сквозной сбор по всем базам + глубокий психологический профайлинг личности: оценка Scam/Catfish Score (0–100%), паттерны поведения, уровень дохода и детектор легенд.",
                "input": "username / nickname / full name / target",
                "web_runnable": True,
                "scan_type": "ai_profiler",
                "install_guide": {
                    "git": "# Встроенный в платформу когнитивный аналитический модуль",
                    "pip_or_pkg": "pip install google-genai httpx",
                    "docker": "# Работает автономно",
                    "usage": "Введите никнейм цели для генерации полного психологического досье",
                    "notes": "Агрегирует данные Sherlock, GitHub, Instagram, Crypto и формирует отчет с AI-заключениями."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Сформировать AI Досье",
                    "action": "scan_ai_profiler"
                }
            },
            {
                "id": "tg_activity_tracker",
                "name": "⏱️ Telegram Activity & Sleep Tracker (Шпион активности)",
                "repo": "https://github.com/TelegramDB/TelegramDB",
                "web_url": "",
                "purpose": "📊 24-часовая тепловая карта активности и режима сна цели. Функция Mutual Spy — сопоставление времени онлайна двух пользователей на предмет тайного общения.",
                "input": "@username1 [и опционально @username2]",
                "web_runnable": True,
                "scan_type": "activity_tracker",
                "install_guide": {
                    "git": "# Алгоритмический анализатор временных меток и сессий",
                    "pip_or_pkg": "pip install httpx asyncio",
                    "docker": "# Встроенный сервис",
                    "usage": "Введите юзернейм или два юзернейма через запятую",
                    "notes": "Определяет часовой пояс, фазы бодрствования и корреляцию активности."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Анализировать активность",
                    "action": "scan_activity_tracker"
                }
            },
            {
                "id": "crypto_aml_auditor",
                "name": "🚨 Crypto AML & Sanctions Risk Auditor (OFAC & Mixers)",
                "repo": "https://github.com/bitcoin/bitcoin",
                "web_url": "https://blockchair.com/",
                "purpose": "🛡️ Проверка криптокошельков BTC, ETH, TRC20 (USDT), SOL на шкалу риска AML (0–100%), связь с санкциями OFAC, миксерами Tornado Cash, даркнетом и дрейнерами.",
                "input": "BTC / ETH / TRON (TRC20) / SOL address",
                "web_runnable": True,
                "scan_type": "crypto_aml",
                "install_guide": {
                    "git": "# Движок блокчейн-форензики и проверки списков санкций",
                    "pip_or_pkg": "pip install httpx",
                    "docker": "# Встроенный аудит",
                    "usage": "Введите адрес кошелька для оценки риска чистоты активов",
                    "notes": "Помогает избежать блокировок на биржах перед приемом оплаты."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Проверить AML Риск",
                    "action": "scan_crypto_aml"
                }
            },
            {
                "id": "face_search_ai",
                "name": "👤 Reverse Face AI Search & Deepfake Detector",
                "repo": "https://github.com/ageitgey/face_recognition",
                "web_url": "",
                "purpose": "🔍 Поиск совпадений человека по фото лица в открытых аватарах соцсетей (Telegram, VK, GitHub) + проверка на AI-генерацию (Deepfake / ThisPersonDoesNotExist).",
                "input": "фото лица (JPG / PNG / WebP)",
                "web_runnable": True,
                "scan_type": "face_search",
                "install_guide": {
                    "git": "# Нейросетевой модуль биометрического анализа",
                    "pip_or_pkg": "pip install Pillow numpy",
                    "docker": "# Встроенный в WebApp",
                    "usage": "Загрузите фото для поиска совпадений и анализа артефактов лица",
                    "notes": "Выявляет фейковые профили в дейтинге и соцсетях."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Анализ лица и Deepfake",
                    "action": "scan_face_search"
                }
            },
            {
                "id": "digital_hygiene_audit",
                "name": "🛡️ Digital Hygiene & Personal Breach Audit (Аудит себя)",
                "repo": "https://github.com/sherlock-project/sherlock",
                "web_url": "",
                "purpose": "🔐 Проверка цифрового следа и истории утечек по email/телефону: расчет индекса уязвимости (Exposure Score) и чек-лист защиты личных данных.",
                "input": "email / телефон / юзернейм",
                "web_runnable": True,
                "scan_type": "breach_audit",
                "install_guide": {
                    "git": "# Модуль аудита собственной цифровой гигиены",
                    "pip_or_pkg": "pip install httpx",
                    "docker": "# Не требуется",
                    "usage": "Введите свою почту для проверки наличия в базах утечек",
                    "notes": "Формирует персональный отчет по закрытию уязвимостей."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Проверить свои утечки",
                    "action": "scan_breach_audit"
                }
            },
            {
                "id": "target_monitor_alerts",
                "name": "🔔 Real-Time Target Monitor (Слежка в Telegram)",
                "repo": "https://github.com/TelegramDB/TelegramDB",
                "web_url": "",
                "purpose": "📡 Постановка цели (профиль TG, канал, криптокошелек) на непрерывное отслеживание: бот присылает уведомление при смене аватарки, био, юзернейма или крупных переводах.",
                "input": "@username / channel / wallet",
                "web_runnable": True,
                "scan_type": "target_alerts",
                "install_guide": {
                    "git": "# Фоновый агент мониторинга целей",
                    "pip_or_pkg": "pip install aiogram httpx",
                    "docker": "# Работает в фоновом демоне",
                    "usage": "Укажите цель для добавления в список активного наблюдения",
                    "notes": "Уведомления приходят прямо в личные сообщения бота."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Поставить на мониторинг",
                    "action": "subscribe_target_alerts"
                }
            }
        ]
    },
    {
        "id": "telegram_osint",
        "title": "✈️ Telegram Разведка & Анализ профилей",
        "desc": "Специализированные инструменты поиска и анализа Telegram-аккаунтов, каналов, групп и метаданных.",
        "tools": [
            {
                "id": "sockpuppet_attribution",
                "name": "🕵️ Детектор виртов & Атрибуция основы (Attribution Engine)",
                "repo": "https://github.com/sherlock-project/sherlock",
                "web_url": "https://t.me/",
                "purpose": "🎯 Выявление основного аккаунта и реальной личности по виртуальным, вторым или купленным профилям Telegram через анализ мутаций никнеймов, возраста ID, аватаров и баз данных.",
                "input": "telegram username / id / text",
                "web_runnable": True,
                "scan_type": "attribution",
                "install_guide": {
                    "git": "# Встроенный в систему аналитический движок корреляции",
                    "pip_or_pkg": "pip install httpx beautifulsoup4",
                    "docker": "# Работает автономно в Docker",
                    "usage": "Введите юзернейм или ID вирта для поиска цифровых связей",
                    "notes": "Сопоставляет метаданные ID, цифровые следы и выявляет родительские аккаунты."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Найти основу вирта",
                    "action": "scan_attribution"
                }
            },
            {
                "id": "tg_inspector",
                "name": "Telegram Profile & ID Inspector",
                "repo": "https://github.com/TelegramDB/TelegramDB",
                "web_url": "https://t.me/",
                "purpose": "🔍 Анализ публичного Telegram-профиля: извлечение Bio, имени, аватарки, статуса бота/канала и примерная оценка даты регистрации по ID.",
                "input": "telegram username / id",
                "web_runnable": True,
                "scan_type": "telegram",
                "install_guide": {
                    "git": "# Встроенный веб-сканер прямо в этой панели",
                    "pip_or_pkg": "pip install httpx beautifulsoup4",
                    "docker": "# Работает автономно в Docker",
                    "usage": "Введите юзернейм в поле выше (например, @durov)",
                    "notes": "Позволяет быстро получить публичные метаданные профиля без авторизации."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Проверить Telegram",
                    "action": "scan_telegram"
                }
            },
            {
                "id": "telepathy",
                "name": "Telepathy",
                "repo": "https://github.com/jordanwildon/Telepathy",
                "web_url": "https://github.com/jordanwildon/Telepathy",
                "purpose": "📊 Всесторонний сбор и анализ публичных Telegram-чатов и каналов: экспорт участников, форварды сообщений, связи и частота постов.",
                "input": "telegram channel / chat",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/jordanwildon/Telepathy.git\ncd Telepathy",
                    "pip_or_pkg": "pip3 install telepathy-osint",
                    "docker": "docker run -it telepathy-osint",
                    "usage": "telepathy -t @target_channel --export csv",
                    "notes": "Требует API ID и API Hash с my.telegram.org для глубокого сбора публичных сообщений."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/jordanwildon/Telepathy"
                }
            },
            {
                "id": "telegramdb",
                "name": "TelegramDB Search",
                "repo": "https://github.com/TelegramDB/TelegramDB",
                "web_url": "https://telegramdb.org/",
                "purpose": "🌐 Глобальный поисковик и каталог открытых каналов, чатов и публичных сообщений Telegram.",
                "input": "keyword / handle / channel",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "# Общедоступный веб-сервис",
                    "pip_or_pkg": "# Доступен через онлайн-интерфейс",
                    "docker": "# Не требуется",
                    "usage": "Открыть https://telegramdb.org/ и ввести ключевое слово или ник",
                    "notes": "Помогает найти публичные чаты и каналы, связанные с интересующей темой."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Открыть TelegramDB Онлайн",
                    "href": "https://telegramdb.org/"
                }
            },
            {
                "id": "tgstat",
                "name": "TGStat Analytics",
                "repo": "https://tgstat.ru/",
                "web_url": "https://tgstat.ru/",
                "purpose": "📈 Глубокая статистика каналов, упоминаний, репостов, охватов и индексация постов в Telegram.",
                "input": "channel / post / keyword",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "# Официальный аналитический портал",
                    "pip_or_pkg": "# Открытый веб-сервис",
                    "docker": "# Не требуется",
                    "usage": "Открыть https://tgstat.ru/ и ввести @channel",
                    "notes": "Крупнейший публичный каталог статистики каналов и истории изменения названий/аватаров."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Открыть TGStat",
                    "href": "https://tgstat.ru/"
                }
            }
        ]
    },
    {
        "id": "amazing_osint",
        "title": "🌟 Удивительный OSINT, GeoINT & Фото-детектив",
        "desc": "Необычные методики: определение времени съемки по тени от солнца, машина времени удаленных страниц, спутники и Vision AI.",
        "tools": [
            {
                "id": "suncalc",
                "name": "SunCalc (Теневой GeoINT)",
                "repo": "https://github.com/mourner/suncalc",
                "web_url": "https://suncalc.org/",
                "purpose": "☀️ Определение точного времени и даты съемки фото по углу солнца, высоте и длине отбрасываемой тени на объектах.",
                "input": "location / photo / date",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "git clone https://github.com/mourner/suncalc.git",
                    "pip_or_pkg": "npm install suncalc",
                    "docker": "# Работает в браузере на suncalc.org",
                    "usage": "Открыть https://suncalc.org, указать точку на карте и сопоставить тень со снимка",
                    "notes": "Ключевой инструмент международных OSINT-расследователей для подтверждения подлинности времени событий."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Открыть SunCalc Онлайн",
                    "href": "https://suncalc.org/"
                }
            },
            {
                "id": "wayback",
                "name": "Wayback Machine (Машина времени)",
                "repo": "https://github.com/internetarchive/wayback",
                "web_url": "https://web.archive.org/",
                "purpose": "⏳ Поиск удаленных профилей, старых постов, удаленных страниц сайтов и архивных копий с 1996 года.",
                "input": "url / profile link",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "# Официальный архив интернета",
                    "pip_or_pkg": "pip install waybackpy",
                    "docker": "# Не требуется",
                    "usage": "waybackpy --url \"https://twitter.com/target\" --oldest",
                    "notes": "Позволяет восстановить удаленный аккаунт или старые аватарки/био, сохраненные краулерами."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Открыть Wayback Machine",
                    "href": "https://web.archive.org/"
                }
            },
            {
                "id": "overpass_turbo",
                "name": "Overpass Turbo (Поиск по деталям карты)",
                "repo": "https://github.com/tyrasd/overpass-turbo",
                "web_url": "https://overpass-turbo.eu/",
                "purpose": "📍 Сверхточный гео-поиск: найти локацию по косвенным признакам (например, 'перекресток с трамвайными путями и кирпичной башней').",
                "input": "OSM query / filters",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "git clone https://github.com/tyrasd/overpass-turbo.git",
                    "pip_or_pkg": "# Онлайн песочница запросов",
                    "docker": "# Не требуется",
                    "usage": "Открыть https://overpass-turbo.eu/ и запустить фильтрацию по тегам OpenStreetMap",
                    "notes": "Позволяет отыскать точные координаты места съемки по элементам ландшафта."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Открыть Overpass Turbo",
                    "href": "https://overpass-turbo.eu/"
                }
            },
            {
                "id": "zoom_earth",
                "name": "Zoom Earth & Спутники",
                "repo": "https://zoom.earth/",
                "web_url": "https://zoom.earth/",
                "purpose": "🛰️ Спутниковые снимки планеты высокого разрешения в реальном времени, штормы, пожары и метеорологические данные.",
                "input": "coordinates / city",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "# Спутниковая платформа",
                    "pip_or_pkg": "# Онлайн интерфейс",
                    "docker": "# Не требуется",
                    "usage": "Открыть https://zoom.earth/ для просмотра спутниковых слоев NASA/NOAA",
                    "notes": "Обновление спутниковых снимков каждые 10-15 минут."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Открыть Zoom Earth",
                    "href": "https://zoom.earth/"
                }
            }
        ]
    },
    {
        "id": "username_osint",
        "title": "🔍 Поиск по никнеймам (Sherlock & WhatsMyName 750+ баз)",
        "desc": "Инструменты для поиска профилей и открытых аккаунтов по псевдониму на сотнях платформ.",
        "tools": [
            {
                "id": "sherlock",
                "name": "Sherlock & WhatsMyName Engine (750+ Баз)",
                "repo": "https://github.com/sherlock-project/sherlock",
                "web_url": "https://sherlock-project.github.io/",
                "purpose": "⚡ Глобальный мульти-поиск аккаунтов по 750+ базам данных (Steam, Telegram, GitHub, VK, TikTok, Reddit, Twitch, Habr, Pikabu, WhatsMyName и др.) с дедукцией данных.",
                "input": "username",
                "web_runnable": True,
                "scan_type": "username",
                "install_guide": {
                    "git": "git clone https://github.com/sherlock-project/sherlock.git\ncd sherlock",
                    "pip_or_pkg": "python3 -m pip install -r requirements.txt",
                    "docker": "docker run --rm -t mysherlock user123",
                    "usage": "python3 sherlock.py <username> --print-found",
                    "notes": "В панель интегрирован быстрый асинхронный движок, опрашивающий сервисы параллельно."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Запустить в WebApp",
                    "action": "scan_username"
                }
            },
            {
                "id": "maigret",
                "name": "Maigret",
                "repo": "https://github.com/soxoj/maigret",
                "web_url": "https://maigret.readthedocs.io/",
                "purpose": "Мощный сборщик досье по нику с проверкой 3000+ сайтов, парсингом профилей и генерацией графа связей.",
                "input": "username",
                "web_runnable": True,
                "scan_type": "username",
                "install_guide": {
                    "git": "git clone https://github.com/soxoj/maigret.git\ncd maigret",
                    "pip_or_pkg": "pip3 install maigret",
                    "docker": "docker run --rm -it soxoj/maigret <username> --html",
                    "usage": "maigret <username> -a --html",
                    "notes": "Генерирует наглядные HTML и PDF отчеты с найденными аватарками и ссылками."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Запустить в WebApp",
                    "action": "scan_username"
                }
            },
            {
                "id": "blackbird",
                "name": "Blackbird",
                "repo": "https://github.com/p1ngul1n0/blackbird",
                "web_url": "https://github.com/p1ngul1n0/blackbird",
                "purpose": "Асинхронный быстрый чекер никнеймов со встроенным локальным Web UI и REST API.",
                "input": "username",
                "web_runnable": True,
                "scan_type": "username",
                "install_guide": {
                    "git": "git clone https://github.com/p1ngul1n0/blackbird\ncd blackbird",
                    "pip_or_pkg": "pip3 install -r requirements.txt",
                    "docker": "docker build -t blackbird .\ndocker run -p 9797:9797 blackbird",
                    "usage": "python3 blackbird.py -u <username>\n# Или веб-интерфейс:\npython3 blackbird.py --web",
                    "notes": "При запуске с ключом --web поднимает локальную веб-панель на порту 9797."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Запустить в WebApp",
                    "action": "scan_username"
                }
            },
            {
                "id": "social_analyzer",
                "name": "Social-Analyzer",
                "repo": "https://github.com/qeeqbox/social-analyzer",
                "web_url": "https://github.com/qeeqbox/social-analyzer",
                "purpose": "API и веб-инструмент для глубокого анализа профилей на 1000+ платформах с автоматическими скриншотами.",
                "input": "username / profile name",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/qeeqbox/social-analyzer.git\ncd social-analyzer",
                    "pip_or_pkg": "pip3 install social-analyzer",
                    "docker": "docker run -p 9005:9005 -it qeeqbox/social-analyzer",
                    "usage": "python3 app.py --username \"wertag20\"",
                    "notes": "Поддерживает обнаружение аккаунтов по шаблонам профилей и строкам поиска."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/qeeqbox/social-analyzer"
                }
            },
            {
                "id": "whatsmyname",
                "name": "WhatsMyName",
                "repo": "https://github.com/WebBreacher/WhatsMyName",
                "web_url": "https://whatsmyname.app/",
                "purpose": "Популярный каталог и веб-сервис для мгновенного поиска аккаунтов по открытой JSON-базе паттернов.",
                "input": "username",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "git clone https://github.com/WebBreacher/WhatsMyName.git",
                    "pip_or_pkg": "pip3 install -r requirements.txt",
                    "docker": "# Сервис полностью доступен онлайн на https://whatsmyname.app/",
                    "usage": "python3 wmn-data.py -u <username>",
                    "notes": "База WhatsMyName используется в большинстве мировых OSINT-фреймворков."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Открыть WhatsMyName WebApp",
                    "href": "https://whatsmyname.app/"
                }
            }
        ]
    },
    {
        "id": "social_google_instagram",
        "title": "📱 Google, Instagram & Социальная разведка",
        "desc": "Специализированные утилиты для извлечения скрытых ID, почт, привязок телефонов и Google-аккаунтов.",
        "tools": [
            {
                "id": "ghunt",
                "name": "GHunt (Google Account Recon)",
                "repo": "https://github.com/mxrch/GHunt",
                "web_url": "https://github.com/mxrch/GHunt",
                "purpose": "🔍 Разведка аккаунтов Google по почте: Gaia ID, отзывы на Google Картах, фотографии, Google Drive, YouTube канал и календарь.",
                "input": "gmail address",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/mxrch/GHunt.git\ncd GHunt",
                    "pip_or_pkg": "pip install ghunt",
                    "docker": "docker run -v $(pwd)/resources:/usr/src/app/resources -it ghunt email target@gmail.com",
                    "usage": "ghunt email target@gmail.com",
                    "notes": "Позволяет составить гео-трек пользователя по его публичным отзывам на Google Maps."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/mxrch/GHunt"
                }
            },
            {
                "id": "instaloader",
                "name": "Instaloader (Python Instagram Downloader & Metadata Extractor)",
                "repo": "https://github.com/instaloader/instaloader",
                "web_url": "https://instaloader.github.io/",
                "purpose": "📥 Мощнейший Python-инструмент для выгрузки постов, историй, видео и сохранения оригинальных EXIF-метаданных, геопозиций и текстовых описаний для анализа.",
                "input": "instagram username / post link",
                "web_runnable": True,
                "scan_type": "cli_tool",
                "install_guide": {
                    "git": "git clone https://github.com/instaloader/instaloader.git\ncd instaloader",
                    "pip_or_pkg": "pip3 install instaloader",
                    "docker": "docker run --rm -v $(pwd):/data instaloader/instaloader --geotags profile <target>",
                    "usage": "instaloader --geotags --comments --stories profile <username>",
                    "notes": "Сохраняет геометки фотографий и выгружает полный дамп текстовых комментариев."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Анализ Instagram в WebApp",
                    "action": "scan_universal"
                }
            },
            {
                "id": "osintgram",
                "name": "Osintgram (Интерактивная консоль Instagram-разведки)",
                "repo": "https://github.com/Datalux/Osintgram",
                "web_url": "https://github.com/Datalux/Osintgram",
                "purpose": "🕵️ Интерактивный терминал разведки по Instagram: анализ подписчиков, извлечение телефонных номеров, почт, геотегов с фото и истории комментариев.",
                "input": "instagram username",
                "web_runnable": True,
                "scan_type": "cli_tool",
                "install_guide": {
                    "git": "git clone https://github.com/Datalux/Osintgram.git\ncd Osintgram",
                    "pip_or_pkg": "pip3 install -r requirements.txt",
                    "docker": "docker build -t osintgram .\ndocker run --rm -it -v \"$PWD/output:/output\" osintgram <target>",
                    "usage": "python3 main.py <target_username>",
                    "notes": "Команды внутри шелла: `addrs` (геометки), `comments` (комментарии), `followers` (подписчики)."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Запустить Osintgram",
                    "action": "scan_universal"
                }
            },
            {
                "id": "toutatis",
                "name": "Toutatis (Instagram Phone/Email Mask Extractor)",
                "repo": "https://github.com/megadose/toutatis",
                "web_url": "https://github.com/megadose/toutatis",
                "purpose": "📸 Извлечение скрытых данных из Instagram: маскированный номер телефона (+7***42), частичная почта, числовой ID аккаунта через API восстановления.",
                "input": "instagram handle",
                "web_runnable": True,
                "scan_type": "cli_tool",
                "install_guide": {
                    "git": "git clone https://github.com/megadose/toutatis.git\ncd toutatis",
                    "pip_or_pkg": "pip3 install toutatis",
                    "docker": "docker build -t toutatis .\ndocker run -it toutatis",
                    "usage": "toutatis -u <username> -s \"YOUR_SESSIONID\"",
                    "notes": "Использует официальные эндпоинты Instagram для получения масок телефона и почты."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Пробить Toutatis",
                    "action": "scan_universal"
                }
            },
            {
                "id": "instagram_followers_parser",
                "name": "Instagram Followers DOM Parser (VladiStep)",
                "repo": "https://github.com/VladiStep/instagram_followers_parser",
                "web_url": "https://github.com/VladiStep/instagram_followers_parser",
                "purpose": "⚡ Быстрый JavaScript-скрипт для консоли браузера (F12) для автоматического скролла и парсинга подписчиков страницы.",
                "input": "instagram profile url",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "git clone https://github.com/VladiStep/instagram_followers_parser.git",
                    "pip_or_pkg": "# Браузерный скрипт для консоли Chrome DevTools",
                    "docker": "# Не требуется",
                    "usage": "Вставить код `instagramFollowersParser.js` в консоль F12 на странице подписчиков",
                    "notes": "Использует MutationObserver для оптимизированного скролла без нагрузки на RAM."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/VladiStep/instagram_followers_parser"
                }
            },
            {
                "id": "vk_recon",
                "name": "ВКонтакте Deep Recon & Hidden Friends Finder",
                "repo": "https://github.com/sherlock-project/sherlock",
                "web_url": "https://vk.com/",
                "purpose": "🌐 Разведка по профилям VK: извлечение открытых записей, привязок к городу, альбомов, скрытых друзей и старых id.",
                "input": "vk id / screen_name",
                "web_runnable": True,
                "scan_type": "username",
                "install_guide": {
                    "git": "# Встроенный в систему веб-сканер",
                    "pip_or_pkg": "pip install httpx",
                    "docker": "# Работает автономно",
                    "usage": "Введите ник или ID страницы (например, durov или id1)",
                    "notes": "Генерирует поисковые дорки по стене и архивам записей."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Анализ VK в WebApp",
                    "action": "scan_username"
                }
            },
            {
                "id": "tiktok_osint",
                "name": "TikTok Profile & Metadata Recon",
                "repo": "https://github.com/drawrowfly/tiktok-scraper",
                "web_url": "https://www.tiktok.com/",
                "purpose": "🎵 Извлечение числового SecUID, аватаров высокого разрешения, даты регистрации и истории хэштегов из TikTok.",
                "input": "tiktok handle (@username)",
                "web_runnable": True,
                "scan_type": "username",
                "install_guide": {
                    "git": "git clone https://github.com/drawrowfly/tiktok-scraper.git",
                    "pip_or_pkg": "npm install -g tiktok-scraper",
                    "docker": "docker run -it drawrowfly/tiktok-scraper user <username>",
                    "usage": "tiktok-scraper user <username> -d --history",
                    "notes": "Позволяет скачать медиа и извлечь скрытый идентификатор автора."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Проверить TikTok",
                    "action": "scan_username"
                }
            }
        ]
    },
    {
        "id": "web_infra_secrets",
        "title": "🌐 Разведка сайтов, доменов и поиск утечек ключей",
        "desc": "Инструменты для исследования веб-ресурсов, поиска субдоменов, проверки DNS, краулинга и поиска утекших секретов.",
        "tools": [
            {
                "id": "photon",
                "name": "Photon Web OSINT Crawler",
                "repo": "https://github.com/s0md3v/Photon",
                "web_url": "https://github.com/s0md3v/Photon",
                "purpose": "🕷️ Невероятно быстрый веб-краулер: извлечение ссылок, email-адресов, аккаунтов соцсетей, ключей API, файлов и поддоменов с целевого сайта.",
                "input": "website url",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/s0md3v/Photon.git\ncd Photon",
                    "pip_or_pkg": "pip3 install -r requirements.txt",
                    "docker": "docker build -t photon .\ndocker run -it --name photon-running photon -u target.com",
                    "usage": "python3 photon.py -u https://target.com --keys --export",
                    "notes": "Автоматически находит скрытые ссылки и эндпоинты в JavaScript файлах."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/s0md3v/Photon"
                }
            },
            {
                "id": "trufflehog",
                "name": "TruffleHog (Поиск утекших ключей)",
                "repo": "https://github.com/trufflesecurity/trufflehog",
                "web_url": "https://trufflesecurity.com/",
                "purpose": "🔑 Сканирование репозиториев, коммитов и веб-страниц на наличие утекших API-ключей, токенов AWS, Telegram Bot API, OpenAI и приватных SSH-ключей.",
                "input": "git repo / url / s3",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/trufflesecurity/trufflehog.git",
                    "pip_or_pkg": "curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin",
                    "docker": "docker run -it --rm trufflesecurity/trufflehog:latest github --repo https://github.com/target/repo",
                    "usage": "trufflehog github --repo https://github.com/target/repo",
                    "notes": "Проверяет валидность найденных ключей через реальные API запросы."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/trufflesecurity/trufflehog"
                }
            },
            {
                "id": "finalrecon",
                "name": "FinalRecon",
                "repo": "https://github.com/thewhiteh4t/FinalRecon",
                "web_url": "https://github.com/thewhiteh4t/FinalRecon",
                "purpose": "🎯 Универсальный швейцарский нож разведки веб-целей: Whois, DNS, SSL, заголовки, краулинг, порты и архивные ссылки Wayback.",
                "input": "domain / url",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/thewhiteh4t/FinalRecon.git\ncd FinalRecon",
                    "pip_or_pkg": "pip3 install -r requirements.txt",
                    "docker": "docker build -t finalrecon .\ndocker run -it finalrecon --full https://target.com",
                    "usage": "python3 finalrecon.py --full https://target.com",
                    "notes": "Генерирует аккуратный сводный отчет в консоли и сохраняет данные в формате TXT."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/thewhiteh4t/FinalRecon"
                }
            },
            {
                "id": "webcheck",
                "name": "Web-Check",
                "repo": "https://github.com/Lissy93/web-check",
                "web_url": "https://web-check.xyz/",
                "purpose": "Комплексный веб-комбайн: SSL, DNS, открытые порты, заголовки безопасности, Whois, хостинг и cookies.",
                "input": "domain",
                "web_runnable": True,
                "scan_type": "domain",
                "install_guide": {
                    "git": "git clone https://github.com/Lissy93/web-check.git\ncd web-check",
                    "pip_or_pkg": "npm install && npm run build",
                    "docker": "docker run -p 3000:3000 lissy93/web-check",
                    "usage": "# Запустить локально:\nyarn start # (порт 3000)",
                    "notes": "Доступен публичный облачный сервис https://web-check.xyz/ без необходимости локальной установки."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Открыть Web-Check Онлайн",
                    "href": "https://web-check.xyz/"
                }
            },
            {
                "id": "subfinder",
                "name": "Subfinder",
                "repo": "https://github.com/projectdiscovery/subfinder",
                "web_url": "https://github.com/projectdiscovery/subfinder",
                "purpose": "Скоростной инструмент пассивного поиска субдоменов через открытые источники данных.",
                "input": "domain",
                "web_runnable": True,
                "scan_type": "domain",
                "install_guide": {
                    "git": "git clone https://github.com/projectdiscovery/subfinder.git\ncd subfinder/v2/cmd/subfinder\ngo build .",
                    "pip_or_pkg": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
                    "docker": "docker run projectdiscovery/subfinder:latest -d example.com",
                    "usage": "subfinder -d target.com -o subdomains.txt",
                    "notes": "Пассивный поиск поддоменов без прямого сканирования целевого сервера."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Пассивный скан домена",
                    "action": "scan_domain"
                }
            }
        ]
    },
    {
        "id": "mapping_investigation",
        "title": "🗺️ Картирование связей, графы и фреймворки",
        "desc": "Инструменты для построения графов расследования, визуализации связей и сводных OSINT-панелей.",
        "tools": [
            {
                "id": "spiderfoot",
                "name": "SpiderFoot OSINT Framework",
                "repo": "https://github.com/smicallef/spiderfoot",
                "web_url": "https://www.spiderfoot.net/",
                "purpose": "🕷️ Автоматизированный комбайн сбора разведданных по 200+ источникам данных: сопоставление IP, доменов, почт, телефонов и графы связей.",
                "input": "domain / ip / email / name",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/smicallef/spiderfoot.git\ncd spiderfoot",
                    "pip_or_pkg": "pip3 install -r requirements.txt",
                    "docker": "docker run -p 5001:5001 spiderfoot",
                    "usage": "python3 sf.py -l 127.0.0.1:5001 # Веб-панель",
                    "notes": "Поднимает полноценную веб-лабораторию с интерактивным графом связей расследования."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/smicallef/spiderfoot"
                }
            },
            {
                "id": "maltego",
                "name": "Maltego Visual Link Analysis",
                "repo": "https://github.com/maltego",
                "web_url": "https://www.maltego.com/",
                "purpose": "🌐 Отраслевой стандарт визуального картирования связей между людьми, организациями, доменами, IP и соцсетями на интерактивном графе.",
                "input": "entity graph / transforms",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "# Десктопное приложение",
                    "pip_or_pkg": "# Доступна бесплатная версия Maltego Community Edition",
                    "docker": "# Не требуется",
                    "usage": "Скачать с https://www.maltego.com/ и запустить визуальные трансформации (Transforms)",
                    "notes": "Позволяет исследовать сложные цепочки связей в виде интерактивной карты."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Сайт Maltego",
                    "href": "https://www.maltego.com/"
                }
            },
            {
                "id": "osint_framework",
                "name": "OSINT Framework Tree",
                "repo": "https://github.com/lockfale/osint-framework",
                "web_url": "https://osintframework.com/",
                "purpose": "🌳 Интерактивное дерево-навигатор по всем мировым открытым источникам данных, реестрам, архивам и инструментам.",
                "input": "interactive tree",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "git clone https://github.com/lockfale/osint-framework.git",
                    "pip_or_pkg": "# Доступно онлайн",
                    "docker": "# Не требуется",
                    "usage": "Открыть https://osintframework.com/ и выбрать ветку интересующего типа данных",
                    "notes": "Самый структурированный путеводитель по методикам сбора информации."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Открыть OSINT Framework",
                    "href": "https://osintframework.com/"
                }
            }
        ]
    },
    {
        "id": "email_checks",
        "title": "📧 Почта и Телефонная разведка (Email & Phone OSINT)",
        "desc": "Инструменты проверки валидности email-адресов, MX-записей, привязок и разведки по номерам телефонов.",
        "tools": [
            {
                "id": "phoneinfoga_recon",
                "name": "📱 PhoneInfoga Recon & Number Inspector",
                "repo": "https://github.com/sundowndev/phoneinfoga",
                "web_url": "https://github.com/sundowndev/phoneinfoga",
                "purpose": "🔍 Комплексная разведка по номеру телефона: определение оператора, региона, типа линии (VoIP/Мобильный), мессенджеры (WA/TG/Viber) и поисковые дорки по доскам объявлений и соцсетям.",
                "input": "phone",
                "web_runnable": True,
                "scan_type": "phone",
                "install_guide": {
                    "git": "git clone https://github.com/sundowndev/phoneinfoga.git\ncd phoneinfoga",
                    "pip_or_pkg": "curl -sSL https://raw.githubusercontent.com/sundowndev/phoneinfoga/master/support/run | bash",
                    "docker": "docker run -it sundowndev/phoneinfoga scan -n <phone>",
                    "usage": "./phoneinfoga scan -n +79991234567",
                    "notes": "Определяет оператора, валидность формата E.164 и генерирует поисковые сканеры."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Проверить телефон в WebApp",
                    "action": "scan_phone"
                }
            },
            {
                "id": "holehe",
                "name": "Holehe",
                "repo": "https://github.com/megadose/holehe",
                "web_url": "https://github.com/megadose/holehe",
                "purpose": "Проверка регистрации email на 120+ сервисах (через формы забытого пароля без спама/уведомлений).",
                "input": "email",
                "web_runnable": True,
                "scan_type": "email",
                "install_guide": {
                    "git": "git clone https://github.com/megadose/holehe.git\ncd holehe",
                    "pip_or_pkg": "pip3 install holehe",
                    "docker": "docker run --rm -it megadose/holehe <email>",
                    "usage": "holehe target@example.com --only-used",
                    "notes": "Флаг --only-used показывает только сайты, где адрес действительно найден."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Проверить Email в WebApp",
                    "action": "scan_email"
                }
            },
            {
                "id": "epieos",
                "name": "Epieos",
                "repo": "https://github.com/epieos",
                "web_url": "https://epieos.com/",
                "purpose": "Онлайн-поисковик информации по Email и номеру телефона (Google ID, календарь, профили).",
                "input": "email",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "# Облачный сервис, установка не требуется",
                    "pip_or_pkg": "# Доступно через Web UI",
                    "docker": "# Доступно через https://epieos.com/",
                    "usage": "Открыть https://epieos.com/ и ввести адрес почты",
                    "notes": "Позволяет узнать Google User ID и публичный профиль Google Maps."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Открыть Epieos Web",
                    "href": "https://epieos.com/"
                }
            }
        ]
    },
    {
        "id": "security_utilities",
        "title": "🛠️ Швейцарский нож аналитика и веб-утилиты",
        "desc": "Универсальные веб-комбайны для декодирования данных, проверки IP, ASN и интерактивные лаборатории.",
        "tools": [
            {
                "id": "cyberchef",
                "name": "CyberChef (GCHQ)",
                "repo": "https://github.com/gchq/CyberChef",
                "web_url": "https://gchq.github.io/CyberChef/",
                "purpose": "«Швейцарский нож» аналитика: декодирование Base64, Hex, URL, парсинг регулярных выражений, хеширование и конвертация.",
                "input": "data / string",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "git clone https://github.com/gchq/CyberChef.git\ncd CyberChef\nnpm install && npm run build",
                    "pip_or_pkg": "# Доступна готовая веб-версия в браузере",
                    "docker": "docker run -d -p 8080:80 mpepping/cyberchef",
                    "usage": "Открыть https://gchq.github.io/CyberChef/ в браузере",
                    "notes": "Работает полностью на стороне клиента (в браузере) без отправки данных на сервер."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Открыть CyberChef Онлайн",
                    "href": "https://gchq.github.io/CyberChef/"
                }
            },
            {
                "id": "ipinfo",
                "name": "IP-API & Geolocation",
                "repo": "https://github.com/ipinfo",
                "web_url": "https://ipinfo.io/",
                "purpose": "Определение провайдера (ISP), AS-номера, страны, города и диапазона IP-адресов.",
                "input": "ip",
                "web_runnable": True,
                "scan_type": "ip",
                "install_guide": {
                    "git": "# Публичный REST API",
                    "pip_or_pkg": "curl -s http://ip-api.com/json/8.8.8.8",
                    "docker": "# Не требуется",
                    "usage": "curl http://ip-api.com/json/<target_ip>",
                    "notes": "Быстрая идентификация хостинга, датацентра или мобильного оператора."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Анализ IP в WebApp",
                    "action": "scan_ip"
                }
            },
            {
                "id": "shodan_search",
                "name": "Shodan Search Engine",
                "repo": "https://github.com/achillean/shodan-python",
                "web_url": "https://www.shodan.io/",
                "purpose": "Поисковик по подключенным к интернету устройствам, открытым портам, баннерам и веб-серверам.",
                "input": "ip / domain / query",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "git clone https://github.com/achillean/shodan-python.git\ncd shodan-python",
                    "pip_or_pkg": "pip install shodan",
                    "docker": "docker run -it --rm achillean/shodan shodan search apache",
                    "usage": "shodan init <YOUR_API_KEY>\nshodan host 8.8.8.8",
                    "notes": "Требует бесплатного API-ключа с сайта shodan.io."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Открыть Shodan.io",
                    "href": "https://www.shodan.io/"
                }
            }
        ]
    },
    {
        "id": "hacker_crypto_git",
        "title": "💻 GitHub, Блокчейн & Deep OSINT",
        "desc": "Глубокая разведка по исходному коду, коммитам, криптокошелькам и утечкам.",
        "tools": [
            {
                "id": "github_recon",
                "name": "GitHub Deep Recon & Commit Email Finder",
                "repo": "https://github.com/techgaun/github-dorks",
                "web_url": "https://github.com/",
                "purpose": "🔍 Деанонимизация разработчика: извлечение скрытых email-адресов и реального имени из открытых git-коммитов, анализ SSH/GPG ключей и активности.",
                "input": "github username",
                "web_runnable": True,
                "scan_type": "github",
                "install_guide": {
                    "git": "# Встроенный в систему веб-сканер GitHub API",
                    "pip_or_pkg": "pip install httpx",
                    "docker": "# Работает автономно в Cyber Hub",
                    "usage": "Введите GitHub юзернейм (например: torvalds)",
                    "notes": "Находит реальный email автора из истории PushEvent событий."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Анализ GitHub",
                    "action": "scan_github"
                }
            },
            {
                "id": "crypto_tracker",
                "name": "Crypto Wallet & Blockchain Explorer",
                "repo": "https://github.com/blockchair",
                "web_url": "https://blockchair.com/",
                "purpose": "💰 Разведка по криптокошелькам: определение сети (BTC, ETH, TRON/USDT-TRC20, Solana), баланса, истории транзакций и ссылок на AML-проверку.",
                "input": "crypto wallet address",
                "web_runnable": True,
                "scan_type": "crypto",
                "install_guide": {
                    "git": "# Встроенный мультичейн анализатор блокчейна",
                    "pip_or_pkg": "pip install httpx",
                    "docker": "# Работает автономно в Cyber Hub",
                    "usage": "Введите адрес кошелька (например: 0x... или T...)",
                    "notes": "Позволяет быстро отследить движение средств и биржевые транзакции."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Проверить кошелек",
                    "action": "scan_crypto"
                }
            },
            {
                "id": "holehe_osint",
                "name": "Holehe Multi-Service Email Presence",
                "repo": "https://github.com/megadose/holehe",
                "web_url": "https://github.com/megadose/holehe",
                "purpose": "📧 Проверка привязки Email к 120+ сайтам (Instagram, Twitter, Discord, Amazon, GitHub и др.) без отправки уведомлений жертве.",
                "input": "email",
                "web_runnable": True,
                "scan_type": "email",
                "install_guide": {
                    "git": "git clone https://github.com/megadose/holehe.git\ncd holehe",
                    "pip_or_pkg": "pip install holehe",
                    "docker": "docker run -it --rm megadose/holehe holehe target@email.com",
                    "usage": "holehe target@email.com",
                    "notes": "Позволяет составить полный цифровой профиль человека по его почте."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Проверить Email",
                    "action": "scan_email"
                }
            }
        ]
    },
    {
        "id": "deep_archive_recon",
        "title": "🏛️ Архивы, Удаленные данные & Сквозной Auto-Recon",
        "desc": "Сквозной сбор связей, поиск в Wayback Machine, история SSL-сертификатов и архивных копий.",
        "tools": [
            {
                "id": "autorecon",
                "name": "⚡ Сквозной Auto-Recon & Граф связей (Auto-Investigator)",
                "repo": "https://github.com/sherlock-project/sherlock",
                "web_url": "",
                "purpose": "🕸️ Автоматическое сквозное расследование: сбор профилей, коммит-email, проверка серверов, построение интерактивного графа связей и тактического досье.",
                "input": "username / email / domain / phone",
                "web_runnable": True,
                "scan_type": "autorecon",
                "install_guide": {
                    "git": "# Встроенный в систему авто-движок расследования",
                    "pip_or_pkg": "# Работает автономно в WebApp",
                    "docker": "# Встроенный модуль",
                    "usage": "Введите любую цель для сквозного построения графа связей",
                    "notes": "Объединяет Sherlock, GitHub коммиты, Holehe и Wayback в единый граф."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Запустить Auto-Recon",
                    "action": "scan_autorecon"
                }
            },
            {
                "id": "wayback",
                "name": "🏛️ Wayback Machine & Archive.org Inspector",
                "repo": "https://github.com/internetarchive/wayback",
                "web_url": "https://web.archive.org/",
                "purpose": "⏳ Поиск удаленных страниц, старых версий профилей соцсетей, контактов и снимков сайтов за прошлые годы через Web Archive API.",
                "input": "url / domain / profile link",
                "web_runnable": True,
                "scan_type": "wayback",
                "install_guide": {
                    "git": "# Встроенный модуль обращения к CDX API Archive.org",
                    "pip_or_pkg": "pip install httpx",
                    "docker": "# Доступно в веб-панели",
                    "usage": "wayback_machine --target github.com/username",
                    "notes": "Позволяет увидеть, что было написано на странице до ее удаления."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Проверить архивы",
                    "action": "scan_wayback"
                }
            },
            {
                "id": "crtsh",
                "name": "📜 Certificate Transparency Logs (crt.sh)",
                "repo": "https://github.com/crtsh/crt.sh",
                "web_url": "https://crt.sh/",
                "purpose": "🔍 Поиск скрытых, тестовых и забытых поддоменов через глобальные журналы прозрачности SSL-сертификатов.",
                "input": "domain",
                "web_runnable": True,
                "scan_type": "crtsh",
                "install_guide": {
                    "git": "# Встроенный парсер журналов сертификатов crt.sh",
                    "pip_or_pkg": "curl https://crt.sh/?q=%.target.com&output=json",
                    "docker": "# Работает через API",
                    "usage": "crtsh --domain example.com",
                    "notes": "Находит поддомены, которых нет в открытых записях DNS."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Анализ SSL журналов",
                    "action": "scan_crtsh"
                }
            }
        ]
    },
    {
        "id": "cyber_tools_lab",
        "title": "🧰 Лаборатория Декодеров & Dork Builder",
        "desc": "Конструктор боевых дорков, автоопределение хешей (MD5/SHA256/bcrypt), JWT и мульти-декодеры.",
        "tools": [
            {
                "id": "cyberchef_decoder",
                "name": "🧰 Кибер-декодер (Base64, Hex, ROT13, URL)",
                "repo": "https://github.com/gchq/CyberChef",
                "web_url": "https://gchq.github.io/CyberChef/",
                "purpose": "🔓 Универсальный швейцарский нож декодирования: Base64, Hex, URL, Binary, ROT13 прямо в интерфейсе.",
                "input": "encoded string / payload",
                "web_runnable": True,
                "scan_type": "decoder",
                "install_guide": {
                    "git": "# Встроенная лаборатория декодеров",
                    "pip_or_pkg": "# Доступно в WebApp",
                    "docker": "# Не требуется",
                    "usage": "Введите зашифрованную строку и выберите алгоритм",
                    "notes": "Позволяет быстро разобрать полезную нагрузку."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Открыть декодер",
                    "action": "open_decoder"
                }
            },
            {
                "id": "hash_identifier",
                "name": "🔐 Hash Identifier & Analyzer",
                "repo": "https://github.com/blackploit/hash-identifier",
                "web_url": "https://hashes.com/",
                "purpose": "🎯 Автоматическое определение алгоритма хеширования (MD5, SHA-1, SHA-256, NTLM, bcrypt, Argon2).",
                "input": "hash string",
                "web_runnable": True,
                "scan_type": "decoder",
                "install_guide": {
                    "git": "# Встроенный анализатор хешей",
                    "pip_or_pkg": "# Доступно в WebApp",
                    "docker": "# Не требуется",
                    "usage": "Вставьте хеш (например: e10adc3949ba59abbe56e057f20f883e)",
                    "notes": "Определяет разрядность и вероятные алгоритмы."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Идентифицировать хеш",
                    "action": "open_decoder"
                }
            },
            {
                "id": "jwt_decoder",
                "name": "🛡️ JWT Token & Payload Inspector",
                "repo": "https://jwt.io/",
                "web_url": "https://jwt.io/",
                "purpose": "🔑 Разбор структуры токенов авторизации (Header, Payload, claims, таймстампы) без отправки ключа.",
                "input": "jwt token",
                "web_runnable": True,
                "scan_type": "decoder",
                "install_guide": {
                    "git": "# Встроенный инспектор JWT",
                    "pip_or_pkg": "# Доступно в WebApp",
                    "docker": "# Не требуется",
                    "usage": "Вставьте токен eyJhbGciOi...",
                    "notes": "Показывает права пользователя и время истечения токена."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Анализ JWT",
                    "action": "open_decoder"
                }
            },
            {
                "id": "crypto_forensics",
                "name": "🪙 Crypto & Blockchain Wallet Forensics (BTC, ETH, TRON)",
                "repo": "https://github.com/blockstream/esplora",
                "web_url": "https://blockstream.info/",
                "purpose": "💰 Разведка криптокошельков: проверка баланса, объема всех транзакций, даты первой/последней активности для Bitcoin (BTC), Ethereum (ETH) и TRON/USDT (TRC-20).",
                "input": "crypto address (1..., 3..., bc1..., 0x..., T...)",
                "web_runnable": True,
                "scan_type": "crypto",
                "install_guide": {
                    "git": "# Встроенный чекер публичных блокчейнов",
                    "pip_or_pkg": "pip install httpx",
                    "docker": "# Доступно в WebApp",
                    "usage": "crypto_recon --address 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                    "notes": "Автоматически определяет сеть (BTC, ETH, TRX) и строит сводку баланса."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Проверить кошелек",
                    "action": "scan_crypto"
                }
            },
            {
                "id": "dorking_wizard",
                "name": "🧙‍♂️ OSINT Dorking Matrix & Leak Finder",
                "repo": "https://github.com/BullsEye0/dork-cli",
                "web_url": "https://google.com/",
                "purpose": "🎯 Генератор 25+ боевых поисковых дорков: поиск скрытых документов (.pdf/.xlsx), открытых баз (.sql/.env), утечек на Pastebin и следов в Instagram, VK, TikTok.",
                "input": "target username / keyword / domain",
                "web_runnable": True,
                "scan_type": "dorks",
                "install_guide": {
                    "git": "# Встроенный конструктор поисковых матриц",
                    "pip_or_pkg": "# Доступно в WebApp",
                    "docker": "# Не требуется",
                    "usage": "Введите слово для генерации ссылок под Google, Yandex, DuckDuckGo",
                    "notes": "Позволяет запустить точечный поиск по скрытым документам и паролям в один клик."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Сгенерировать дорки",
                    "action": "scan_dorks"
                }
            }
        ]
    }
]


def normalize_catalog():
    """Нормализует ссылки и параметры запуска для каждого инструмента."""
    for group in CATALOG:
        for tool in group.get("tools", []):
            if "launch" not in tool:
                repo = str(tool.get("repo") or "").strip()
                if repo:
                    tool["launch"] = {
                        "type": "url",
                        "label": "📖 GitHub Репозиторий",
                        "href": repo,
                    }
    return CATALOG


def find_tool(tool_id: str):
    """Поиск инструмента по ID."""
    for group in CATALOG:
        for tool in group.get("tools", []):
            if tool.get("id") == tool_id:
                return tool
    return None
