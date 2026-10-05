#!/bin/bash
set -e

echo "[*] Запуск Web App на порту 8000..."
python /app/src/webapp.py &
WEBAPP_PID=$!

sleep 3

echo "[*] Запуск Telegram Bot..."
python /app/src/bot.py &
BOT_PID=$!

cleanup() {
    kill "$BOT_PID" "$WEBAPP_PID" 2>/dev/null || true
    wait "$BOT_PID" "$WEBAPP_PID" 2>/dev/null || true
}
trap cleanup EXIT

# The web app stays available if Telegram polling exits; Docker restarts the
# container if the web process itself stops.
wait "$WEBAPP_PID"
