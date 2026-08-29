#!/bin/bash

clear
echo "================================"
echo " OSINT LAB - Docker"
echo "================================"
echo ""

if ! command -v docker &> /dev/null; then
    echo "[!] Docker не найден."
    exit 1
fi

DC="docker compose"
if ! docker compose version &> /dev/null; then
    if command -v docker-compose &> /dev/null; then
        DC="docker-compose"
    else
        echo "[!] docker compose не найден."
        exit 1
    fi
fi

if [ -f config/.env ]; then
    echo "[ok] config/.env есть"
    echo ""
    echo "1. Запустить"
    echo "2. Остановить"
    echo "3. Логи"
    echo "4. Перенастроить"
    echo "5. Пересобрать"
    echo "6. Статус"
    echo ""
    read -p "Выбор (1-6): " choice
else
    echo "[!] Нужна настройка."
    choice="4"
fi

case $choice in
    1)
        mkdir -p data
        $DC up -d
        echo "[+] Запущено. Бот: /start  Админ: /visits"
        ;;
    2)
        $DC down
        echo "[+] Остановлено."
        ;;
    3)
        $DC logs -f
        ;;
    4)
        mkdir -p config data
        read -p "BOT_TOKEN: " token
        read -p "DOMAIN (https://osint.qrport.eu): " domain
        read -p "CF_TUNNEL_TOKEN: " cf_token
        read -p "ADMIN_CHAT_ID (свой id, бот ответит /id): " admin_id
        read -p "ADMIN_TOKEN (пароль для /admin/visits): " admin_token
        cat > config/.env <<EOF
BOT_TOKEN=${token}
DOMAIN=${domain:-https://osint.qrport.eu}
CF_TUNNEL_TOKEN=${cf_token}
ADMIN_CHAT_ID=${admin_id}
ADMIN_TOKEN=${admin_token}
DATA_DIR=/app/data
EOF
        echo "[+] Сохранено config/.env"
        read -p "Запустить сейчас? (y/n): " run
        if [ "$run" = "y" ]; then
            $DC up -d --build
            echo "[+] Запущено!"
        fi
        ;;
    5)
        mkdir -p data
        $DC up -d --build
        echo "[+] Готово."
        ;;
    6)
        $DC ps
        ;;
    *)
        echo "[!] Неверный выбор"
        ;;
esac
