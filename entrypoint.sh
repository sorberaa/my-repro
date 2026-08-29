#!/bin/bash
set -e

export $(grep -v '^#' /app/config/.env | xargs)

echo "[*] Запуск Web App на порту 8000..."
python /app/src/webapp.py &
WEBAPP_PID=$!

sleep 3

echo "[*] Запуск Telegram Bot..."
python /app/src/bot.py || true

kill $WEBAPP_PID 2>/dev/null
