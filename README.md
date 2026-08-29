# OSINT LAB — Docker

Образовательный каталог модулей + учебный SQLi + лог визитов в панель.

Живой запуск утилит против людей не включён.

## Домен

```
DOMAIN=https://osint.qrport.eu
```

Только https, без `/` в конце. Иначе Telegram WebApp не откроется.

## Локально / на сервере

```bash
cp config/.env.example config/.env
# заполни BOT_TOKEN, DOMAIN, CF_TUNNEL_TOKEN, ADMIN_CHAT_ID
mkdir -p data
chmod +x panel.sh entrypoint.sh
./panel.sh
```

Или:

```bash
docker compose up -d --build
```

Админ: напиши боту `/id`, вставь число в `ADMIN_CHAT_ID`.  
Визиты: `/visits` в боте или `https://osint.qrport.eu/admin/visits?token=ТВОЙ_ADMIN_TOKEN`

## Git (без секретов)

`config/.env` и `data/` в git не попадают (см. `.gitignore`).

```bash
git add .
git commit -m "OSINT lab catalog + visit log"
git push
```

Друг на сервере:

```bash
git pull
cp config/.env.example config/.env   # если ещё нет
# правит .env на сервере, .env из git не берётся
docker compose up -d --build
```
