"""
Каталог OSINT-инструментов с GitHub, расширенными возможностями Telegram-разведки,
GeoINT, поиском по соцсетям, инструкциями и запуском в WebApp.
"""

CATALOG = [
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
                "id": "toutatis",
                "name": "Toutatis (Instagram OSINT)",
                "repo": "https://github.com/megadose/toutatis",
                "web_url": "https://github.com/megadose/toutatis",
                "purpose": "📸 Извлечение скрытых данных из Instagram: маскированный номер телефона (+7***), частичная почта, числовой ID аккаунта.",
                "input": "instagram handle",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/megadose/toutatis.git\ncd toutatis",
                    "pip_or_pkg": "pip3 install toutatis",
                    "docker": "docker build -t toutatis .\ndocker run -it toutatis",
                    "usage": "toutatis -u target_user -s \"YOUR_SESSIONID\"",
                    "notes": "Использует API мобильного приложения Instagram для получения данных восстановления доступа."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/megadose/toutatis"
                }
            },
            {
                "id": "phoneinfoga",
                "name": "PhoneInfoga (Международный Phone OSINT)",
                "repo": "https://github.com/sundowndev/phoneinfoga",
                "web_url": "https://github.com/sundowndev/phoneinfoga",
                "purpose": "📞 Продвинутый сбор данных по номерам телефонов: оператор, страна, тип связи (VoIP/Mobile), репутация и доркинга в сети.",
                "input": "international phone number",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/sundowndev/phoneinfoga.git\ncd phoneinfoga",
                    "pip_or_pkg": "curl -sSL https://raw.githubusercontent.com/sundowndev/phoneinfoga/master/support/scripts/install | bash",
                    "docker": "docker run --rm -it -p 5000:5000 sundowndev/phoneinfoga serve -p 5000",
                    "usage": "./phoneinfoga scan -n +79991234567\n# Или веб-панель:\n./phoneinfoga serve -p 5000",
                    "notes": "Имеет встроенный веб-интерфейс на порту 5000 для интерактивного сканирования."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/sundowndev/phoneinfoga"
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
