# Локальная установка безопасных OSINT-инструментов

Этот проект поддерживает режим, где ты можешь держать набор публичных OSINT-инструментов локально и подключать их в панель как launch-элементы.

## 1. Установить набор инструментов

Запусти PowerShell-скрипт:

```powershell
cd d:\osint-bot
powershell -ExecutionPolicy Bypass -File .\scripts\install_safe_osint_tools.ps1
```

Инструменты будут скачаны в папку:

```text
d:\osint-bot\tools\
```

## 2. Проверить, что они скачались

```powershell
Get-ChildItem d:\osint-bot\tools
```

## 3. Подключить в панель

Для каждого инструмента добавь в `src/catalog.py` элемент вида:

```python
{
    "id": "sherlock",
    "name": "Sherlock",
    "repo": "https://github.com/sherlock-project/sherlock",
    "purpose": "Поиск аккаунтов по нику.",
    "input": "username",
    "launch": {
        "type": "local",
        "label": "Запустить локально",
        "command": "powershell -NoExit -Command \"cd d:/osint-bot/tools/sherlock; python sherlock.py --help\""
    }
}
```

## 4. Безопасность и ограничения

- только публичные данные
- только учебный / личный проект
- никакой таргетинг на конкретных людей
- личные данные и социальные профили без согласия не использовать

## 5. Расширение

Ты можешь добавлять новые инструменты в тот же каталог, просто подставляя:
- GitHub URL
- локальную команду запуска
- короткое описание
- тип данных: username / domain / email / file

