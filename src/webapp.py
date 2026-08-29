import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from catalog import CATALOG

load_dotenv("/app/config/.env")
load_dotenv("config/.env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
VISITS_FILE = DATA_DIR / "visits.jsonl"

app = FastAPI(title="OSINT Lab")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def client_ip(request: Request) -> str:
    xff = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def append_visit(record: dict) -> None:
    with VISITS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


async def notify_admin(text: str) -> None:
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(url, json={"chat_id": ADMIN_CHAT_ID, "text": text})
    except Exception:
        pass


@app.middleware("http")
async def log_visits(request: Request, call_next):
    path = request.url.path
    skip = path.startswith("/api/") or path.startswith("/admin") or path == "/favicon.ico"
    response = await call_next(request)
    if skip:
        return response
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "ip": client_ip(request),
        "path": path,
        "ua": request.headers.get("user-agent", "")[:300],
        "country": request.headers.get("cf-ipcountry", ""),
    }
    try:
        append_visit(rec)
    except Exception:
        pass
    if path in ("/", "/lab"):
        geo = f" / {rec['country']}" if rec["country"] else ""
        await notify_admin(
            f"Визит в панель\nIP: {rec['ip']}{geo}\npath: {path}\nUA: {rec['ua'][:120]}"
        )
    return response


@app.get("/api/catalog")
async def api_catalog(q: Optional[str] = None):
    query = (q or "").strip().lower()
    if not query:
        return {"groups": CATALOG}
    groups = []
    for g in CATALOG:
        tools = [
            t
            for t in g["tools"]
            if query in t["name"].lower()
            or query in t["purpose"].lower()
            or query in t.get("input", "").lower()
            or query in g["title"].lower()
        ]
        if tools:
            groups.append({**g, "tools": tools})
    return {"groups": groups}


@app.get("/api/health")
async def health():
    return {"ok": True, "tools": sum(len(g["tools"]) for g in CATALOG)}


@app.get("/admin/visits")
async def admin_visits(token: str = "", limit: int = 100):
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        return JSONResponse({"error": "forbidden"}, status_code=403)
    rows = []
    if VISITS_FILE.exists():
        for line in VISITS_FILE.read_text(encoding="utf-8").splitlines()[-max(1, min(limit, 500)) :]:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    rows.reverse()
    return {"count": len(rows), "visits": rows}


@app.get("/admin/visits-html")
async def admin_visits_html(token: str = ""):
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        return HTMLResponse("<h1>❌ Доступ запрещен</h1>", status_code=403)
    
    rows = []
    if VISITS_FILE.exists():
        for line in VISITS_FILE.read_text(encoding="utf-8").splitlines()[-500:]:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    rows.reverse()
    
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Panel - IP Logs</title>
        <style>
            :root { --g: #00ff41; --bg: #050505; --warn: #ff6600; }
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { background: var(--bg); color: var(--g); font-family: 'Courier New', monospace; min-height: 100vh; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { border-bottom: 2px solid var(--g); padding-bottom: 16px; margin-bottom: 24px; }
            h1 { font-size: 28px; letter-spacing: 2px; }
            .stats { display: flex; gap: 16px; margin-bottom: 20px; }
            .stat { border: 1px solid var(--g); padding: 12px; background: #080808; min-width: 150px; }
            .stat-num { font-size: 24px; font-weight: bold; }
            .stat-label { font-size: 12px; opacity: 0.7; margin-top: 4px; }
            table { width: 100%; border-collapse: collapse; border: 1px solid var(--g); background: #0a0a0a; }
            th { background: #031003; padding: 12px; text-align: left; border-bottom: 1px solid var(--g); font-weight: bold; }
            td { padding: 10px 12px; border-bottom: 1px solid #144; }
            tr:hover { background: #0f0f0f; }
            .ip { color: #7dff9a; font-weight: bold; }
            .time { opacity: 0.7; font-size: 12px; }
            .country { color: var(--warn); }
            .warn { color: var(--warn); }
            .success { color: var(--g); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 OSINT Lab Admin Panel</h1>
                <p style="opacity: 0.7; margin-top: 8px;">IP Visitor Logs</p>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-num">""" + str(len(rows)) + """</div>
                    <div class="stat-label">Total Visits</div>
                </div>
                <div class="stat">
                    <div class="stat-num">""" + str(len(set(r.get("ip") for r in rows))) + """</div>
                    <div class="stat-label">Unique IPs</div>
                </div>
                <div class="stat">
                    <div class="stat-num">""" + str(len(set(r.get("country") for r in rows if r.get("country")))) + """</div>
                    <div class="stat-label">Countries</div>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Время 🕐</th>
                        <th>IP Адрес 📍</th>
                        <th>Страна 🌍</th>
                        <th>Путь 🛣️</th>
                        <th>User-Agent 🖥️</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for visit in rows[:50]:  # Show last 50
        ts = visit.get("ts", "")[:19]  # Format: YYYY-MM-DD HH:MM:SS
        ip = visit.get("ip", "unknown")
        country = visit.get("country", "—")
        path = visit.get("path", "/")
        ua = visit.get("ua", "—")[:60]
        
        html += f"""
                    <tr>
                        <td class="time">{ts}</td>
                        <td class="ip">{ip}</td>
                        <td class="country">{country if country else "—"}</td>
                        <td>{path}</td>
                        <td style="font-size: 11px; opacity: 0.8;">{ua}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
            
            <div style="margin-top: 24px; opacity: 0.6; font-size: 12px;">
                <p>📌 Это образовательный панель для учебных целей</p>
                <p>🔐 Доступ защищен ADMIN_TOKEN</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html)


@app.post("/api/lab/sqli")
async def sqli_sim(request: Request):
    body = await request.json()
    inp = str(body.get("payload", ""))
    db = [
        {"id": 1, "login": "admin", "pass": "flag{un1on_s3l3ct}", "role": "admin"},
        {"id": 2, "login": "user", "pass": "123456", "role": "user"},
        {"id": 3, "login": "guest", "pass": "guest", "role": "guest"},
    ]
    result, tech, explain = [], "", ""
    low = inp.lower()
    compact = low.replace(" ", "")
    if "' or '1'='1" in low or "'or'1'='1" in compact:
        result, tech = db, "Boolean-based SQLi"
        explain = "Условие 1=1 всегда истинно. Учебная база вернула все строки."
    elif "union" in low:
        result, tech = db, "UNION-based SQL Injection"
        explain = "UNION склеивает результаты двух SELECT. Только симуляция."
    elif "sleep(" in low:
        tech = "Time-based Blind SQLi"
        explain = "В реале сервер ждал бы. Здесь без задержки."
    elif "load_file" in low:
        tech = "Out-of-band (симуляция)"
        explain = "Учебный стенд. На живых БД так делать нельзя."
        result = [{"data": "admin:flag{dns_exfil}"}, {"data": "user:123456"}]
    else:
        clean = inp.replace("'", "")
        result = [u for u in db if u["login"] == clean]
        tech = "Обычный запрос"
    return {"tech": tech, "explain": explain, "rows": result}


@app.post("/api/run/{tool_id}")
async def run_tool(tool_id: str):
    return JSONResponse(
        {
            "ok": False,
            "error": "Каталог. Живой запуск утилит против людей не подключён.",
            "tool": tool_id,
        },
        status_code=403,
    )


HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OSINT LAB</title>
<style>
:root { --g:#00ff41; --bg:#050505; --warn:#ff6600; }
* { margin:0; padding:0; box-sizing:border-box; }
body { background:var(--bg); color:var(--g); font-family:'Courier New',monospace; min-height:100vh; padding:16px; }
.container { max-width:980px; margin:0 auto; }
.header { border-bottom:2px solid var(--g); padding-bottom:12px; margin-bottom:16px; }
h1 { font-size:22px; letter-spacing:1px; }
.sub { opacity:.75; font-size:13px; margin-top:6px; }
.search { width:100%; background:#000; color:var(--g); border:1px solid var(--g); padding:10px 12px; font-family:inherit; margin:12px 0 18px; }
.group { border:1px solid var(--g); margin-bottom:16px; background:#080808; }
.group-h { padding:10px 12px; background:#031003; border-bottom:1px solid #0a3; cursor:pointer; display:flex; justify-content:space-between; gap:8px; }
.group-h small { opacity:.7; font-weight:normal; display:block; margin-top:4px; }
.tools { padding:10px; display:grid; gap:10px; }
.card { border:1px solid #144; padding:10px; background:#0a0a0a; }
.purpose { font-size:12px; opacity:.85; margin:6px 0; }
.meta { font-size:11px; opacity:.65; }
.badge { display:inline-block; font-size:10px; padding:2px 6px; border:1px solid currentColor; margin-left:6px; }
.off { color:var(--warn); border-color:var(--warn); }
.on { color:var(--g); }
a { color:#7dff9a; }
.hidden { display:none; }
.terminal { background:#0a0a0a; border:1px solid var(--g); padding:16px; margin-top:16px; }
input.lab { background:#000; color:var(--g); border:1px solid var(--g); padding:8px; font-family:inherit; width:100%; max-width:420px; }
button { background:var(--g); color:#000; border:none; padding:8px 14px; font-family:inherit; font-weight:bold; cursor:pointer; margin-top:8px; }
.result { margin-top:12px; padding:12px; background:#001100; border-left:3px solid var(--g); white-space:pre-wrap; font-size:13px; }
.warn { color:var(--warn); }
#empty { opacity:.6; padding:20px 0; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>> OSINT LAB — каталог</h1>
    <p class="sub">Учебная панель. Ищи модуль по названию. Запуск утилит против людей выключен.</p>
  </div>
  <input class="search" id="q" placeholder="поиск модуля: ник, телефон, метаданные, sql..." oninput="render()">
  <div id="board"></div>
  <p id="empty" class="hidden">ничего не найдено</p>
  <div class="terminal" id="sqli">
    <h3>> SQLi Lab (локальная симуляция)</h3>
    <p class="warn">Только учебный стенд. Не используй payload на чужих сайтах.</p>
    <p style="margin:10px 0">SELECT * FROM users WHERE name = '<span id="qd"></span>'</p>
    <input class="lab" id="sqli-input" placeholder="' OR '1'='1" oninput="document.getElementById('qd').innerText=this.value">
    <br><button type="button" onclick="runSqli()">Выполнить на стенде</button>
    <div id="sqli-result" class="result hidden"></div>
  </div>
</div>
<script>
let CATALOG = [];
async function load() {
  const r = await fetch('/api/catalog');
  const data = await r.json();
  CATALOG = data.groups || [];
  render();
}
function render() {
  const q = (document.getElementById('q').value || '').toLowerCase().trim();
  const board = document.getElementById('board');
  board.innerHTML = '';
  let shown = 0;
  CATALOG.forEach(g => {
    const tools = g.tools.filter(t => {
      if (!q) return true;
      const blob = (g.title + ' ' + g.desc + ' ' + t.name + ' ' + t.purpose + ' ' + (t.input||'')).toLowerCase();
      return blob.includes(q);
    });
    if (!tools.length) return;
    shown++;
    const wrap = document.createElement('div');
    wrap.className = 'group';
    wrap.innerHTML = `<div class="group-h" onclick="this.nextElementSibling.classList.toggle('hidden')">
      <div><strong>${g.title}</strong><small>${g.desc}</small></div>
      <div>${tools.length}</div>
    </div>`;
    const list = document.createElement('div');
    list.className = 'tools';
    tools.forEach(t => {
      const blocked = !!t.blocked;
      const live = !!t.live;
      const badge = live ? '<span class="badge on">СТЕНД</span>' : (blocked ? '<span class="badge off">НЕ ЗАПУСКАЕТСЯ</span>' : '<span class="badge">СПРАВКА</span>');
      const repo = t.repo ? `<a href="${t.repo}" target="_blank" rel="noopener">страница на GitHub</a>` : 'встроено';
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `<b>${t.name}</b>${badge}
        <div class="purpose">${t.purpose}</div>
        <div class="meta">вход: ${t.input || '—'} · ${repo}</div>`;
      list.appendChild(card);
    });
    wrap.appendChild(list);
    board.appendChild(wrap);
  });
  document.getElementById('empty').classList.toggle('hidden', shown !== 0);
  const sqliHit = !q || q.includes('sql') || q.includes('lab') || q.includes('инъек');
  document.getElementById('sqli').classList.toggle('hidden', !sqliHit);
}
async function runSqli() {
  const payload = document.getElementById('sqli-input').value;
  const res = document.getElementById('sqli-result');
  res.classList.remove('hidden');
  const r = await fetch('/api/lab/sqli', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({payload})});
  const data = await r.json();
  let out = `> Техника: ${data.tech}\n`;
  if (data.explain) out += `> ${data.explain}\n`;
  out += `> Строк: ${(data.rows||[]).length}\n\n`;
  (data.rows||[]).forEach(row => { out += Object.values(row).join(' | ') + '\n'; });
  res.innerText = out;
}
load();
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_CONTENT


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
