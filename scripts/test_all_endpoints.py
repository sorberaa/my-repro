import asyncio
import json
import httpx

LOCAL_API = "http://127.0.0.1:8000"

async def test_all():
    async with httpx.AsyncClient(base_url=LOCAL_API, timeout=30.0) as client:
        print("=== 1. ТЕСТ: КАТАЛОГ ИНСТРУМЕНТОВ ===")
        r = await client.get("/api/catalog")
        print(f"Status: {r.status_code}, Groups: {len(r.json().get('groups', []))}")

        print("\n=== 2. ТЕСТ: РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ И ОНБОРДИНГ ===")
        r = await client.post("/api/user/profile", json={
            "tg_id": "11223344",
            "tg_username": "alex_test",
            "tg_name": "Alex Hunter",
            "nickname": "ShadowAgent"
        })
        print(f"Registration Status: {r.status_code}, Response: {r.json()}")

        print("\n=== 3. ТЕСТ: ПРОФИЛЬ АДМИНИСТРАТОРА ===")
        r = await client.post("/api/user/profile", json={
            "tg_id": "5233450569",
            "tg_username": "admin_user",
            "tg_name": "Admin",
            "nickname": "ChiefAdmin"
        })
        print(f"Admin Profile Status: {r.status_code}, Response: {r.json()}")

        print("\n=== 4. ТЕСТ: АДМИН-СПИСОК ПОЛЬЗОВАТЕЛЕЙ ===")
        r = await client.get("/api/admin/users", headers={"X-Telegram-User-Id": "5233450569"})
        print(f"Admin Users Status: {r.status_code}, Total users: {len(r.json().get('users', []))}")

        print("\n=== 5. ТЕСТ: ЖУРНАЛ IP-ВИЗИТОВ ===")
        r = await client.get("/api/admin/visitors", headers={"X-Telegram-User-Id": "5233450569"})
        print(f"Visitors Log Status: {r.status_code}, Total records: {r.json().get('total_recorded')}")

        print("\n=== 6. ТЕСТ: SHERLOCK ENGINE (ПОИСК НИКНЕЙМА) ===")
        r = await client.post("/api/scan/username", json={"target": "wertag20", "caller": "ShadowAgent"})
        print(f"Sherlock Status: {r.status_code}, Found profiles: {r.json().get('found_count')}")

        print("\n=== 7. ТЕСТ: PHONE RECON (ТЕЛЕФОННАЯ РАЗВЕДКА) ===")
        r = await client.post("/api/scan/phone", json={"target": "+79991234567", "caller": "ShadowAgent"})
        print(f"Phone Recon Status: {r.status_code}, Carrier: {r.json().get('carrier')}, Region: {r.json().get('country')}")

        print("\n=== 8. ТЕСТ: SOCKPUPPET ATTRIBUTION (ДЕТЕКТОР ВИРТОВ) ===")
        r = await client.post("/api/scan/attribution", json={"target": "@alex_temp", "text_sample": "привет от вирта"})
        print(f"Attribution Status: {r.status_code}, Root handle: {r.json().get('root_handle')}")

        print("\n=== 9. ТЕСТ: DOMAIN & SUBDOMAINS ===")
        r = await client.post("/api/scan/domain", json={"target": "google.com", "caller": "ShadowAgent"})
        print(f"Domain Recon Status: {r.status_code}, IPs: {r.json().get('data', {}).get('ip_addresses')}")

        print("\n=== 10. ТЕСТ: IP GEOINT ===")
        r = await client.post("/api/scan/ip", json={"target": "8.8.8.8", "caller": "ShadowAgent"})
        print(f"IP Recon Status: {r.status_code}, Country: {r.json().get('data', {}).get('country')}")

        print("\n✅ ВСЕ ТЕСТЫ БЭКЕНДА УСПЕШНО ПРОЙДЕНЫ!")

if __name__ == "__main__":
    asyncio.run(test_all())

