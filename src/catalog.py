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
        "title": "🌟 Удивительный OSINT & GeoINT",
        "desc": "Необычные методики: определение времени съемки по тени от солнца, машина времени удаленных страниц и спутники.",
        "tools": [
            {
                "id": "suncalc",
                "name": "SunCalc (Теневой GeoINT)",
                "repo": "https://github.com/mourner/suncalc",
                "web_url": "https://suncalc.org/",
                "purpose": "☀️ Определение точного времени и даты съемки фото по углу солнца, высоте и длине отбрасываемой тени на объектах.",
                "input": "location / date",
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
        "title": "🔍 Поиск по никнеймам (Username OSINT)",
        "desc": "Инструменты для поиска профилей и открытых аккаунтов по псевдониму на сотнях платформ.",
        "tools": [
            {
                "id": "sherlock",
                "name": "Sherlock",
                "repo": "https://github.com/sherlock-project/sherlock",
                "web_url": "https://sherlock-project.github.io/",
                "purpose": "Поиск публичных аккаунтов по никнейму на более чем 400 веб-сервисах и соцсетях.",
                "input": "username",
                "web_runnable": True,
                "scan_type": "username",
                "install_guide": {
                    "git": "git clone https://github.com/sherlock-project/sherlock.git\ncd sherlock",
                    "pip_or_pkg": "python3 -m pip install -r requirements.txt",
                    "docker": "docker build -t mysherlock .\ndocker run --rm -t mysherlock user123",
                    "usage": "python3 sherlock.py <username> --print-found",
                    "notes": "Поддерживает выгрузку в CSV/JSON и сохранение в папку отчетов."
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
            },
            {
                "id": "zehef",
                "name": "Zehef",
                "repo": "https://github.com/N0rz3/Zehef",
                "web_url": "https://github.com/N0rz3/Zehef",
                "purpose": "Автоматизированный OSINT-инструмент поиска профилей и открытых следов по псевдонимам.",
                "input": "username / query",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/N0rz3/Zehef.git\ncd Zehef",
                    "pip_or_pkg": "pip install -r requirements.txt",
                    "docker": "docker build -t zehef .\ndocker run -it zehef",
                    "usage": "python3 zehef.py -u <username>",
                    "notes": "Быстрый сбор открытых профилей с форматированием результатов в консоли."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/N0rz3/Zehef"
                }
            }
        ]
    },
    {
        "id": "mapping_investigation",
        "title": "🗺️ Картирование связей и комплексные фреймворки",
        "desc": "Инструменты для построения графов расследования, визуализации связей и сводных OSINT-панелей.",
        "tools": [
            {
                "id": "osint_mapping_tool",
                "name": "OSINT Mapping Tool",
                "repo": "https://github.com/anonymousRAID/OSINT-Mapping-Tool",
                "web_url": "https://github.com/anonymousRAID/OSINT-Mapping-Tool",
                "purpose": "Инструмент визуализации и картирования связей между объектами расследования (IP, домены, никнеймы, персоны).",
                "input": "entities / graph data",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/anonymousRAID/OSINT-Mapping-Tool.git\ncd OSINT-Mapping-Tool",
                    "pip_or_pkg": "pip install -r requirements.txt",
                    "docker": "docker build -t osint-mapping .\ndocker run -p 5000:5000 osint-mapping",
                    "usage": "python3 app.py # Запуск веб-интерфейса карты",
                    "notes": "Позволяет строить наглядные блок-схемы и экспортировать графы связей расследования."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/anonymousRAID/OSINT-Mapping-Tool"
                }
            },
            {
                "id": "seekr",
                "name": "Seekr OSINT",
                "repo": "https://github.com/seekr-osint/seekr",
                "web_url": "https://github.com/seekr-osint/seekr",
                "purpose": "Многофункциональная веб-панель для сбора данных, скрейпинга открытых веб-страниц и организации расследований.",
                "input": "query / target",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/seekr-osint/seekr.git\ncd seekr",
                    "pip_or_pkg": "pip install -r requirements.txt",
                    "docker": "docker-compose up -d",
                    "usage": "python3 run.py # Открыть http://localhost:5000",
                    "notes": "Удобно разворачивать через docker-compose для получения готового дашборда в браузере."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/seekr-osint/seekr"
                }
            },
            {
                "id": "daprofiler",
                "name": "DaProfiler",
                "repo": "https://github.com/daprofiler/DaProfiler",
                "web_url": "https://github.com/daprofiler/DaProfiler",
                "purpose": "Инструмент структурирования публичных данных и составления профиля по имени/фамилии.",
                "input": "name / surname",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/daprofiler/DaProfiler.git\ncd DaProfiler",
                    "pip_or_pkg": "pip3 install -r requirements.txt",
                    "docker": "docker build -t daprofiler .\ndocker run -it daprofiler",
                    "usage": "python3 profiler.py -n \"Имя Фамилия\"",
                    "notes": "Поиск по публичным реестрам, справочникам и открытым базам компаний."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/daprofiler/DaProfiler"
                }
            }
        ]
    },
    {
        "id": "domain_network",
        "title": "🌐 Разведка сайтов, доменов и инфраструктуры",
        "desc": "Инструменты для исследования веб-ресурсов, поиска субдоменов, проверки DNS и сертификатов.",
        "tools": [
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
                    "notes": "Для максимальной глубины можно добавить бесплатные API-ключи в $HOME/.config/subfinder/provider-config.yaml."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Пассивный скан домена",
                    "action": "scan_domain"
                }
            },
            {
                "id": "amass",
                "name": "OWASP Amass",
                "repo": "https://github.com/owasp-amass/amass",
                "web_url": "https://owasp.org/www-project-amass/",
                "purpose": "Отраслевой стандарт инфраструктурного картирования, сопоставления AS-номеров и DNS.",
                "input": "domain",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/owasp-amass/amass.git\ncd amass\ngo install ./...",
                    "pip_or_pkg": "go install -v github.com/owasp-amass/amass/v4/...@master",
                    "docker": "docker run -v ~/.config/amass:/root/.config/amass/ caffix/amass enum -d example.com",
                    "usage": "amass enum -passive -d target.com",
                    "notes": "Рекомендуется для построения графов инфраструктуры и связей сетевых узлов."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 GitHub Репозиторий",
                    "href": "https://github.com/owasp-amass/amass"
                }
            },
            {
                "id": "theharvester",
                "name": "theHarvester",
                "repo": "https://github.com/laramies/theHarvester",
                "web_url": "https://github.com/laramies/theHarvester",
                "purpose": "Сбор публичных корпоративных почт, субдоменов, имен сотрудников и открытых портов из поисковых систем.",
                "input": "domain",
                "web_runnable": True,
                "scan_type": "domain",
                "install_guide": {
                    "git": "git clone https://github.com/laramies/theHarvester.git\ncd theHarvester",
                    "pip_or_pkg": "pip3 install -r requirements/base.txt",
                    "docker": "docker run --rm -it theharvester/theharvester -d example.com -b all",
                    "usage": "python3 theHarvester.py -d company.com -l 500 -b google,bing,duckduckgo,crtsh",
                    "notes": "Позволяет за пару секунд собрать открытые контакты и структуру компании."
                },
                "launch": {
                    "type": "api",
                    "label": "⚡ Проверить домен в WebApp",
                    "action": "scan_domain"
                }
            },
            {
                "id": "crtsh",
                "name": "crt.sh (Certificate Search)",
                "repo": "https://github.com/google/certificate-transparency-community-site",
                "web_url": "https://crt.sh/",
                "purpose": "Поиск всех когда-либо выпущенных SSL-сертификатов домена в публичных логах Certificate Transparency.",
                "input": "domain",
                "web_runnable": True,
                "scan_type": "web_link",
                "install_guide": {
                    "git": "# Общедоступный веб-сервис без необходимости установки",
                    "pip_or_pkg": "curl -s \"https://crt.sh/?q=%.example.com&output=json\"",
                    "docker": "# Используйте онлайн интерфейс",
                    "usage": "curl -s \"https://crt.sh/?q=%.example.com&output=json\" | jq '.[].name_value'",
                    "notes": "Позволяет мгновенно находить забытые поддомены и тестовые сервисы."
                },
                "launch": {
                    "type": "url",
                    "label": "🌐 Открыть crt.sh Веб-поиск",
                    "href": "https://crt.sh/"
                }
            }
        ]
    },
    {
        "id": "email_checks",
        "title": "📧 Почта и проверка привязок (Email & Phone OSINT)",
        "desc": "Инструменты проверки валидности email-адресов, MX-записей, привязок и телефонных номеров.",
        "tools": [
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
            },
            {
                "id": "phone_osint_guide",
                "name": "Поиск по номерам (Phone OSINT)",
                "repo": "https://github.com/osint-and-search/OSINT_i_poisk_po_telefonu",
                "web_url": "https://github.com/osint-and-search/OSINT_i_poisk_po_telefonu",
                "purpose": "Справочник и методология анализа телефонных номеров (HLR-запросы, мессенджеры, операторы).",
                "input": "phone",
                "web_runnable": False,
                "install_guide": {
                    "git": "git clone https://github.com/osint-and-search/OSINT_i_poisk_po_telefonu.git",
                    "pip_or_pkg": "# Каталог и методические материалы",
                    "docker": "# Откройте репозиторий для изучения ссылок",
                    "usage": "Изучение структуры чекеров и публичных ботов для валидации номеров",
                    "notes": "Содержит подробную базу знаний по идентификации мобильных диапазонов и кодов регионов."
                },
                "launch": {
                    "type": "url",
                    "label": "📖 База знаний на GitHub",
                    "href": "https://github.com/osint-and-search/OSINT_i_poisk_po_telefonu"
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
