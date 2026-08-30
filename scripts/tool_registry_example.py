CATALOG_ENTRY_TEMPLATE = {
    "id": "sherlock",
    "name": "Sherlock",
    "repo": "https://github.com/sherlock-project/sherlock",
    "purpose": "Поиск аккаунтов по никнейму на публичных платформах.",
    "input": "username",
    "launch": {
        "type": "local",
        "label": "Запустить локально",
        "command": "powershell -NoExit -Command \"cd d:/osint-bot/tools/sherlock; python sherlock.py --help\""
    }
}

print("template ready")
