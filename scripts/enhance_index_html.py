import json
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir))

try:
    from catalog import CATALOG
except Exception:
    from src.catalog import CATALOG

html_path = root_dir / "index.html"

catalog_json = json.dumps(CATALOG, ensure_ascii=False, indent=2)

full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>peace of the island of sor/ber peoples</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
:root {{
  --bg: #07090d;
  --card-bg: #0e1219;
  --card-border: #181f2c;
  --card-hover-border: #38bdf8;
  --primary: #38bdf8;
  --primary-glow: rgba(56, 189, 248, 0.2);
  --cyan: #38bdf8;
  --cyan-glow: rgba(56, 189, 248, 0.2);
  --accent-green: #10b981;
  --accent-yellow: #f59e0b;
  --danger: #f43f5e;
  --text: #e2e8f0;
  --text-muted: #64748b;
  --term-bg: #04060a;
  --term-border: #181f2c;
}}

* {{ margin:0; padding:0; box-sizing:border-box; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-tap-highlight-color: transparent; }}
body {{ background:var(--bg); color:var(--text); min-height:100vh; padding:12px; padding-bottom:70px; position:relative; overflow-x:hidden; -webkit-font-smoothing: antialiased; }}

#matrixCanvas {{ position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:0; opacity:0.08; display:none; }}
.container {{ max-width:820px; margin:0 auto; position:relative; z-index:1; }}

/* Навбар */
.navbar {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--card-border); padding:10px 0 14px; margin-bottom:14px; background:rgba(7,9,13,0.92); backdrop-filter:blur(16px); }}
.brand {{ font-size:12px; font-weight:800; color:#fff; display:flex; align-items:center; gap:8px; text-transform:uppercase; letter-spacing:0.5px; cursor:pointer; }}
.brand i {{ color:var(--primary); }}
.nav-actions {{ display:flex; align-items:center; gap:6px; flex-wrap:wrap; }}

.user-badge {{ display:inline-flex; align-items:center; gap:5px; padding:4px 9px; background:#0e1219; border-radius:6px; font-size:11px; font-weight:700; color:#fff; border:1px solid var(--card-border); cursor:pointer; }}
.quota-badge {{ display:inline-flex; align-items:center; gap:5px; padding:4px 9px; background:#0e1219; border-radius:6px; font-size:11px; font-weight:800; color:var(--accent-yellow); border:1px solid var(--card-border); cursor:pointer; transition:all .2s; }}
.quota-badge:hover {{ border-color:var(--accent-yellow); }}

.view-page {{ display:none; }}
.view-page.active {{ display:block; animation:fadeIn 0.15s ease-out; }}
@keyframes fadeIn {{ from {{ opacity:0; }} to {{ opacity:1; }} }}

/* Сетка быстрого доступа (Essential Launchpad) */
.essential-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(115px, 1fr)); gap:6px; margin-bottom:12px; }}
.essential-btn {{ background:var(--card-bg); border:1px solid var(--card-border); border-radius:8px; padding:9px 10px; cursor:pointer; transition:all .15s; }}
.essential-btn:hover {{ border-color:var(--primary); background:#121722; transform:translateY(-1px); }}
.essential-btn-title {{ font-size:11px; font-weight:800; color:#fff; display:flex; align-items:center; gap:5px; margin-bottom:2px; }}
.essential-btn-sub {{ font-size:9px; color:var(--text-muted); }}

/* Поиск по каталогу */
.search-box-row {{ display:flex; gap:6px; align-items:center; margin-bottom:10px; }}
.search-box {{ position:relative; flex:1; }}
.search-box i {{ position:absolute; left:12px; top:50%; transform:translateY(-50%); color:var(--text-muted); font-size:12px; }}
.search-box input {{ width:100%; padding:9px 12px 9px 34px; background:var(--card-bg); border:1px solid var(--card-border); border-radius:6px; color:#fff; font-size:12px; outline:none; transition:all .15s; }}
.search-box input:focus {{ border-color:var(--primary); }}
.search-counter {{ font-size:10px; font-weight:700; color:#94a3b8; white-space:nowrap; background:var(--card-bg); padding:8px 10px; border-radius:6px; border:1px solid var(--card-border); }}

/* Категории (Chips) */
.filter-chips {{ display:flex; gap:5px; overflow-x:auto; padding-bottom:6px; margin-bottom:12px; scrollbar-width:none; -webkit-overflow-scrolling:touch; }}
.filter-chips::-webkit-scrollbar {{ display:none; }}
.chip {{ padding:5px 11px; background:var(--card-bg); border:1px solid var(--card-border); border-radius:6px; font-size:10px; font-weight:700; color:#94a3b8; white-space:nowrap; cursor:pointer; display:inline-flex; align-items:center; gap:5px; transition:all .15s; }}
.chip:hover, .chip.active {{ background:#161c28; border-color:var(--primary); color:#fff; }}

/* Сетка карточек каталога */
.group-title {{ font-size:11px; font-weight:800; color:#94a3b8; margin:14px 0 6px; display:flex; align-items:center; gap:6px; text-transform:uppercase; letter-spacing:0.5px; }}
.group-desc {{ font-size:10px; color:var(--text-muted); margin-bottom:8px; }}

.cards-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(240px, 1fr)); gap:8px; }}
.card {{ background:var(--card-bg); border:1px solid var(--card-border); border-radius:8px; padding:12px; cursor:pointer; transition:all .15s; display:flex; flex-direction:column; justify-content:space-between; }}
.card:hover {{ border-color:var(--primary); background:#121722; transform:translateY(-1px); }}
.card-header {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px; gap:6px; }}
.card-title {{ font-size:12px; font-weight:800; color:#fff; display:flex; align-items:center; gap:6px; line-height:1.2; }}
.card-icon {{ color:var(--primary); font-size:12px; }}
.badge {{ font-size:9px; font-weight:800; padding:2px 6px; border-radius:4px; text-transform:uppercase; white-space:nowrap; }}
.badge-api {{ background:#111928; color:var(--primary); border:1px solid #1c2b42; }}
.badge-web {{ background:#111928; color:#94a3b8; border:1px solid var(--card-border); }}
.badge-doc {{ background:#111928; color:var(--text-muted); border:1px solid var(--card-border); }}

.card-purpose {{ font-size:10px; color:#94a3b8; line-height:1.4; margin-bottom:8px; flex:1; }}
.card-target-tag {{ font-size:9px; color:var(--primary); font-family:monospace; margin-bottom:8px; }}

/* Кнопки */
.btn-group {{ display:flex; flex-wrap:wrap; gap:5px; }}
.btn {{ padding:6px 12px; font-size:11px; font-weight:700; border-radius:6px; border:none; cursor:pointer; display:inline-flex; align-items:center; gap:5px; text-decoration:none; transition:all .15s; }}
.btn-primary {{ background:#fff; color:#000; font-weight:800; }}
.btn-primary:hover {{ background:#e2e8f0; }}
.btn-secondary {{ background:var(--card-bg); color:var(--text); border:1px solid var(--card-border); }}
.btn-secondary:hover {{ border-color:#fff; color:#fff; }}
.btn-purple {{ background:#2563eb; color:#fff; }}
.btn-purple:hover {{ background:#1d4ed8; }}
.btn-cyan {{ background:var(--primary); color:#000; font-weight:800; }}
.btn-yellow {{ background:#f59e0b; color:#000; font-weight:800; }}
.btn-danger {{ background:#1a0d11; color:var(--danger); border:1px solid #3b141d; }}

/* Страница инструмента (toolView) */
.tool-view-header {{ background:var(--card-bg); border:1px solid var(--card-border); border-radius:8px; padding:14px; margin-bottom:10px; }}
.back-btn {{ display:inline-flex; align-items:center; gap:5px; color:var(--primary); font-size:11px; font-weight:700; cursor:pointer; margin-bottom:8px; }}
.back-btn:hover {{ color:#fff; }}
.tool-view-title {{ font-size:15px; font-weight:800; color:#fff; margin-bottom:3px; }}
.tool-view-desc {{ font-size:11px; color:var(--text-muted); margin-bottom:10px; line-height:1.4; }}

.workspace-box {{ background:var(--card-bg); border:1px solid var(--card-border); border-radius:8px; padding:14px; margin-bottom:10px; }}
.workspace-title {{ font-size:11px; font-weight:800; color:#fff; margin-bottom:10px; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:5px; }}

.input-row {{ display:flex; gap:6px; margin-bottom:10px; }}
.tool-input {{ flex:1; padding:9px 12px; background:#05070a; border:1px solid var(--card-border); border-radius:6px; color:#fff; font-size:12px; outline:none; }}
.tool-input:focus {{ border-color:var(--primary); }}

/* Характеристики модуля */
.spec-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(160px, 1fr)); gap:6px; }}
.spec-card {{ background:#07090e; border:1px solid var(--card-border); border-radius:6px; padding:8px 10px; }}
.spec-label {{ font-size:9px; color:var(--text-muted); margin-bottom:2px; }}
.spec-val {{ font-size:11px; font-weight:700; color:#fff; }}

/* Кастомные карточки результатов */
.custom-card {{ background:var(--card-bg); border:1px solid var(--card-border); border-radius:8px; padding:12px; margin-bottom:8px; }}
.custom-card-title {{ font-size:12px; font-weight:800; color:#fff; margin-bottom:8px; display:flex; align-items:center; gap:6px; }}
.custom-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:11px; }}
.custom-item {{ background:#07090e; padding:6px 8px; border-radius:6px; border:1px solid var(--card-border); }}
.custom-label {{ color:var(--text-muted); font-size:9px; margin-bottom:2px; }}
.custom-val {{ color:#fff; font-weight:700; font-size:11px; word-break:break-all; }}

/* Профили */
.profiles-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(180px, 1fr)); gap:5px; margin-top:6px; }}
.profile-card {{ background:#07090e; border:1px solid var(--card-border); border-radius:6px; padding:6px 8px; display:flex; align-items:center; justify-content:space-between; gap:5px; }}
.profile-name {{ font-size:10px; font-weight:700; color:#fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}

/* Терминал */
.cli-console-box {{ background:var(--term-bg); border:1px solid var(--term-border); border-radius:8px; padding:12px; margin-bottom:10px; }}
.cli-output {{ color:#e2e8f0; font-family:'Courier New', monospace; font-size:11px; line-height:1.5; white-space:pre-wrap; max-height:360px; overflow-y:auto; margin-bottom:10px; }}
.cli-prompt-row {{ display:flex; align-items:center; gap:6px; font-family:'Courier New', monospace; font-size:12px; }}
.cli-prompt-label {{ color:var(--primary); font-weight:800; }}
.cli-input {{ flex:1; background:transparent; border:none; outline:none; color:#fff; font-family:'Courier New', monospace; font-size:12px; }}

/* Дропзона */
.upload-dropzone {{ border:1px dashed var(--card-border); border-radius:8px; padding:18px 12px; text-align:center; background:#07090e; cursor:pointer; transition:all .15s; margin-bottom:8px; }}
.upload-dropzone:hover {{ border-color:var(--primary); }}
.upload-preview {{ max-width:100%; max-height:200px; border-radius:6px; margin-top:8px; display:none; border:1px solid var(--card-border); }}

/* Спиннер */
.loader {{ display:none; text-align:center; padding:12px; }}
.spinner {{ width:20px; height:20px; border:2px solid #1e293b; border-top-color:#fff; border-radius:50%; animation:spin .8s linear infinite; margin:0 auto 6px; }}
@keyframes spin {{ to {{ transform:rotate(360deg); }} }}

/* Авторизация */
.auth-container {{ display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:60vh; padding:16px; }}
.auth-card {{ background:var(--card-bg); border:1px solid var(--card-border); border-radius:10px; padding:20px; max-width:380px; width:100%; text-align:center; }}
.auth-icon {{ font-size:32px; color:var(--primary); margin-bottom:10px; }}
.auth-title {{ font-size:13px; font-weight:800; color:#fff; margin-bottom:4px; }}
.auth-subtitle {{ font-size:10px; color:var(--text-muted); margin-bottom:14px; line-height:1.4; }}
.auth-input {{ width:100%; padding:9px 12px; background:#05070a; border:1px solid var(--card-border); border-radius:6px; color:#fff; font-size:12px; outline:none; margin-bottom:10px; text-align:center; }}
.auth-input:focus {{ border-color:var(--primary); }}

.footer-info {{ text-align:center; font-size:9px; color:#475569; margin-top:16px; padding:8px; }}

</style>
</head>
<body>

<canvas id="matrixCanvas"></canvas>

<div class="container">
  
  <!-- НАВБАР -->
  <div class="navbar">
    <div class="brand" onclick="showView('catalogView')">
      <i class="fa-solid fa-shield-halved" style="color:var(--primary); font-size:14px;"></i>
      <span style="font-weight:900; letter-spacing:0.5px; font-size:12px;">peace of the island of sor/ber peoples</span>
      <span style="font-size:8px; background:rgba(0,255,102,0.15); color:var(--primary); padding:1px 5px; border-radius:4px; font-weight:800; border:1px solid rgba(0,255,102,0.3);">LIVE</span>
    </div>
    <div class="nav-actions">
      <div class="quota-badge" id="quotaBadge" onclick="openStarsModal()" title="Баланс запросов и Stars">
        <i class="fa-solid fa-star"></i> <span id="quotaSpan">5/5 Запросов</span>
      </div>
      <button class="btn btn-yellow" id="navAdminBtn" onclick="openAdminPanel()" style="display:none; padding:4px 8px; font-size:10px;"><i class="fa-solid fa-shield-halved"></i> 👑 Админ</button>
      <div class="user-badge" id="currentUserBadge" onclick="handleUserBadgeClick()" title="Профиль агента / Вход для админа">
        <i id="userBadgeIcon" class="fa-solid fa-user-check"></i> <span id="currentUsernameSpan">Агент</span>
      </div>
      <button class="btn btn-cyan" onclick="showView('graphView')" style="padding:4px 8px; font-size:10px;"><i class="fa-solid fa-project-diagram"></i> Граф</button>
      <button class="btn btn-primary" onclick="showView('terminalView')" style="padding:4px 8px; font-size:10px;"><i class="fa-solid fa-terminal"></i> CLI</button>
      <button class="btn btn-secondary" onclick="showView('decoderView')" style="padding:4px 8px; font-size:10px;"><i class="fa-solid fa-wrench"></i> Лаб</button>
    </div>
  </div>

  <!-- MODAL: ПОКУПКА ЗВЕЗД (STARS) -->
  <div id="starsModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:9999; backdrop-filter:blur(8px); align-items:center; justify-content:center; padding:16px;">
    <div style="background:#090f1d; border:2px solid #eab308; border-radius:16px; padding:20px; max-width:440px; width:100%; box-shadow:0 0 40px rgba(234,179,8,0.25);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <div style="font-size:15px; font-weight:800; color:#facc15; display:flex; align-items:center; gap:8px;">
          <i class="fa-solid fa-star"></i> Пополнение баланса (Telegram Stars)
        </div>
        <button onclick="closeStarsModal()" style="background:none; border:none; color:#94a3b8; font-size:20px; cursor:pointer;">&times;</button>
      </div>
      <div style="font-size:11px; color:#cbd5e1; margin-bottom:14px; line-height:1.5;">
        Каждому новому агенту начисляется <b>5 бесплатных запросов</b>.<br>
        Для продолжения расследований выберите тариф пополнения:
      </div>
      <div style="display:flex; flex-direction:column; gap:8px; margin-bottom:14px;">
        <div onclick="buyStarsPkg('pkg_20')" style="background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:12px; display:flex; justify-content:space-between; align-items:center; cursor:pointer; transition:all .2s;" onmouseover="this.style.borderColor='#eab308'" onmouseout="this.style.borderColor='#1e293b'">
          <div>
            <div style="font-weight:800; font-size:13px; color:#fff;">🌟 20 OSINT Запросов</div>
            <div style="font-size:10px; color:#94a3b8;">Тариф «Разведчик»</div>
          </div>
          <button class="btn btn-yellow" style="padding:6px 12px; font-size:11px;">35 ⭐️</button>
        </div>
        <div onclick="buyStarsPkg('pkg_50')" style="background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:12px; display:flex; justify-content:space-between; align-items:center; cursor:pointer; transition:all .2s;" onmouseover="this.style.borderColor='#eab308'" onmouseout="this.style.borderColor='#1e293b'">
          <div>
            <div style="font-weight:800; font-size:13px; color:#fff;">🌟 50 OSINT Запросов</div>
            <div style="font-size:10px; color:#94a3b8;">Тариф «Оперативник» (Популярно)</div>
          </div>
          <button class="btn btn-yellow" style="padding:6px 12px; font-size:11px;">88 ⭐️</button>
        </div>
        <div onclick="buyStarsPkg('pkg_100')" style="background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:12px; display:flex; justify-content:space-between; align-items:center; cursor:pointer; transition:all .2s;" onmouseover="this.style.borderColor='#eab308'" onmouseout="this.style.borderColor='#1e293b'">
          <div>
            <div style="font-weight:800; font-size:13px; color:#fff;">🌟 100 OSINT Запросов</div>
            <div style="font-size:10px; color:#94a3b8;">Тариф «Архимаг OSINT»</div>
          </div>
          <button class="btn btn-yellow" style="padding:6px 12px; font-size:11px;">235 ⭐️</button>
        </div>
      </div>
      <div style="font-size:10px; color:#64748b; text-align:center;">
        Оплата происходит мгновенно через официальные Telegram Stars. Также доступна команда <code>/buy</code> в боте.
      </div>
    </div>
  </div>

  <!-- ВЬЮ 0: СТРАНИЦА РЕГИСТРАЦИИ -->
  <div class="view-page" id="registerView">
    <div class="auth-container">
      <div class="auth-card">
        <i class="fa-solid fa-shield-halved auth-icon"></i>
        <div class="auth-title">peace of the island of sor/ber peoples</div>
        <div class="auth-subtitle">
          Для доступа к системе расследований, базам Sherlock, поиску по Instagram, VK, GitHub и блокчейн-разведке зарегистрируйте рабочий позывной:
        </div>
        <input type="text" id="regNicknameInput" class="auth-input" placeholder="Введите ваш позывной (например: Ghost_OSINT)" onkeydown="if(event.key==='Enter') doRegister()">
        <button class="btn btn-primary" style="width:100%; justify-content:center; padding:13px; font-size:13px;" onclick="doRegister()">
          <i class="fa-solid fa-check"></i> Зарегистрироваться и получить 5 запросов
        </button>
        <div id="regStatusMsg" style="margin-top:12px; font-size:12px; color:var(--danger); display:none;"></div>
      </div>
    </div>
  </div>

  <!-- ВЬЮ 1: ГЛАВНЫЙ КАТАЛОГ & БЫСТРЫЙ ПОИСК -->
  <div class="view-page active" id="catalogView">
    
    <!-- ЕДИНЫЙ УМНЫЙ OMNIBAR ПОИСКА -->
    <div style="background:var(--card-bg); border:1px solid var(--card-border); border-radius:8px; padding:12px; margin-bottom:10px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <div style="font-size:11px; font-weight:800; color:#fff; display:flex; align-items:center; gap:5px;">
          <i class="fa-solid fa-crosshairs" style="color:var(--cyan);"></i> Универсальный OSINT Поиск & AI Досье
        </div>
        <div class="search-counter" id="searchCounterBadge" style="font-size:9px; padding:3px 7px;">52 утилиты</div>
      </div>
      <div style="display:flex; gap:6px;">
        <input type="text" id="searchInput" class="tool-input" style="flex:1;" placeholder="Никнейм (@user), кошелек (0x/BTC), домен, телефон или инструмент..." oninput="renderCatalog()" onkeydown="if(event.key==='Enter') runMainOmniSearch()">
        <button class="btn btn-purple" style="padding:9px 12px; font-size:11px;" onclick="runMainOmniSearch()"><i class="fa-solid fa-brain"></i> AI Досье</button>
      </div>
      <div style="display:flex; gap:8px; margin-top:6px; font-size:9px; color:#94a3b8; align-items:center;">
        <span>Быстрый тест:</span>
        <span style="color:var(--cyan); cursor:pointer; text-decoration:underline;" onclick="setOmniTarget('durov')">@durov</span>
        <span style="color:var(--cyan); cursor:pointer; text-decoration:underline;" onclick="setOmniTarget('vitalik.eth')">vitalik.eth</span>
        <span style="color:var(--cyan); cursor:pointer; text-decoration:underline;" onclick="setOmniTarget('sherlock')">sherlock</span>
        <span style="color:var(--cyan); cursor:pointer; text-decoration:underline;" onclick="setOmniTarget('instagram')">instagram</span>
      </div>
    </div>

    <!-- ⚡ БЫСТРЫЙ ДОСТУП К КЛЮЧЕВЫМ МОДУЛЯМ (6 КАРТОЧЕК) -->
    <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(115px, 1fr)); gap:5px; margin-bottom:12px;">
      <div onclick="openToolPage('ai_detective_profiler')" class="essential-btn" style="border-color:rgba(168,85,247,0.35);">
        <div class="essential-btn-title" style="color:#fff;"><i class="fa-solid fa-brain" style="color:#a855f7;"></i> AI Досье</div>
        <div class="essential-btn-sub">Scam Score & Профиль</div>
      </div>
      <div onclick="openToolPage('tg_activity_tracker')" class="essential-btn">
        <div class="essential-btn-title"><i class="fa-solid fa-user-secret" style="color:var(--cyan);"></i> Spy Tracker</div>
        <div class="essential-btn-sub">Сон & Mutual Spy</div>
      </div>
      <div onclick="openToolPage('crypto_aml_auditor')" class="essential-btn" style="border-color:rgba(250,204,21,0.3);">
        <div class="essential-btn-title" style="color:#fef08a;"><i class="fa-solid fa-shield-halved" style="color:#facc15;"></i> Crypto AML</div>
        <div class="essential-btn-sub">OFAC & Миксеры</div>
      </div>
      <div onclick="openToolPage('sherlock')" class="essential-btn">
        <div class="essential-btn-title"><i class="fa-solid fa-magnifying-glass" style="color:var(--primary);"></i> Sherlock</div>
        <div class="essential-btn-sub">480+ Баз никнеймов</div>
      </div>
      <div onclick="openToolPage('instaloader')" class="essential-btn">
        <div class="essential-btn-title"><i class="fa-brands fa-instagram" style="color:#f472b6;"></i> Instagram</div>
        <div class="essential-btn-sub">Посты & Профили</div>
      </div>
      <div onclick="openToolPage('digital_hygiene_audit')" class="essential-btn" style="border-color:rgba(255,51,102,0.3);">
        <div class="essential-btn-title" style="color:#fecdd3;"><i class="fa-solid fa-shield-virus" style="color:var(--danger);"></i> Аудит утечек</div>
        <div class="essential-btn-sub">Проверка почты/тел.</div>
      </div>
    </div>

    <!-- ФИЛЬТР КАТЕГОРИЙ -->
    <div class="filter-chips">
      <div class="chip active" onclick="setFilter('all', this)"><i class="fa-solid fa-layer-group"></i> Все (52)</div>
      <div class="chip" onclick="setFilter('killer_monetization', this)"><i class="fa-solid fa-gem" style="color:var(--yellow);"></i> 💎 AI & AML (Premium)</div>
      <div class="chip" onclick="setFilter('social_google_instagram', this)"><i class="fa-brands fa-instagram"></i> Instagram, VK & TikTok</div>
      <div class="chip" onclick="setFilter('deep_archive_recon', this)"><i class="fa-solid fa-clock-rotate-left"></i> Архивы & Auto-Recon</div>
      <div class="chip" onclick="setFilter('cyber_tools_lab', this)"><i class="fa-solid fa-coins"></i> Блокчейн & Dorks</div>
      <div class="chip" onclick="setFilter('telegram_osint', this)"><i class="fa-brands fa-telegram"></i> Telegram & Вирты</div>
      <div class="chip" onclick="setFilter('username_osint', this)"><i class="fa-solid fa-magnifying-glass"></i> Sherlock Никнеймы</div>
      <div class="chip" onclick="setFilter('email_checks', this)"><i class="fa-solid fa-phone"></i> Телефон & Email</div>
      <div class="chip" onclick="setFilter('hacker_crypto_git', this)"><i class="fa-brands fa-github"></i> GitHub Recon</div>
      <div class="chip" onclick="setFilter('web_infra_secrets', this)"><i class="fa-solid fa-network-wired"></i> Домены & Серверы</div>
      <div class="chip" onclick="setFilter('amazing_osint', this)"><i class="fa-solid fa-camera"></i> Фото & GeoINT</div>
    </div>

    <!-- СПИСОК КАРТОЧЕК КАТАЛОГА -->
    <div id="catalogContainer"></div>
  </div>

  <!-- ВЬЮ 2: СТРАНИЦА ИНСТРУМЕНТА -->
  <div class="view-page" id="toolView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог
    </div>

    <div class="tool-view-header">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px;">
        <div class="tool-view-title" id="tvTitle">Название утилиты</div>
        <div id="tvHeaderButtons" class="btn-group"></div>
      </div>
      <div class="tool-view-desc" id="tvPurpose">Описание</div>
    </div>

    <div class="workspace-box">
      <div class="workspace-title"><i class="fa-solid fa-bolt"></i> Запуск сканера</div>
      
      <div id="tvPhotoUploaderBox" style="display:none;">
        <div class="upload-dropzone" onclick="document.getElementById('tvFileInput').click()" ondragover="event.preventDefault()" ondrop="handlePhotoDrop(event, 'tvFileInput')">
          <i class="fa-solid fa-cloud-arrow-up" style="font-size:26px; color:var(--cyan); margin-bottom:4px;"></i>
          <div style="font-weight:700; color:#fff; font-size:12px;">Загрузите фото для анализа</div>
          <div style="font-size:10px; color:var(--text-muted);">EXIF-теги, GPS, дата, модель камеры и биометрия лица</div>
          <input type="file" id="tvFileInput" accept="image/*" style="display:none;" onchange="handlePhotoUpload(this)">
        </div>
        <img id="tvPhotoPreview" class="upload-preview">
      </div>

      <div class="input-row" id="tvTextInputRow">
        <input class="tool-input" id="tvTargetInput" placeholder="Введите цель..." onkeydown="if(event.key==='Enter') runCurrentToolScan()">
        <button class="btn btn-primary" onclick="runCurrentToolScan()"><i class="fa-solid fa-play"></i> Старт</button>
      </div>

      <div class="loader" id="tvLoader">
        <div class="spinner"></div>
        <span style="font-size:11px; color:var(--cyan);" id="tvLoaderText">Выполняется сканирование...</span>
      </div>

      <div id="tvOutputBox" style="display:none; margin-top:10px;"></div>
    </div>

    <!-- ХАРАКТЕРИСТИКИ И ВОЗМОЖНОСТИ МОДУЛЯ (ВМЕСТО GIT CLONE) -->
    <div class="workspace-box">
      <div class="workspace-title"><i class="fa-solid fa-circle-info"></i> Спецификация и возможности модуля</div>
      <div class="spec-grid" id="tvSpecGrid">
        <div class="spec-card">
          <div class="spec-label">⚡ Движок</div>
          <div class="spec-val" style="color:var(--primary);">Cloud API (Zero-Log)</div>
        </div>
        <div class="spec-card">
          <div class="spec-label">🎯 Формат цели</div>
          <div class="spec-val" id="tvTargetFormat">username / handle</div>
        </div>
        <div class="spec-card">
          <div class="spec-label">⏱️ Время ответа</div>
          <div class="spec-val">~1.2 - 2.5 сек</div>
        </div>
        <div class="spec-card">
          <div class="spec-label">🔒 Приватность</div>
          <div class="spec-val" style="color:var(--cyan);">Анонимный запрос</div>
        </div>
      </div>
    </div>
  </div>

  <!-- ВЬЮ 3: ИНТЕРАКТИВНЫЙ ХАКЕРСКИЙ CLI ТЕРМИНАЛ -->
  <div class="view-page" id="terminalView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог
    </div>

    <div class="cli-console-box">
      <div class="term-topbar">
        <div class="term-dots">
          <span class="term-dot term-dot-red"></span>
          <span class="term-dot term-dot-yellow"></span>
          <span class="term-dot term-dot-green"></span>
        </div>
        <span>CYBER-TERMINAL v2.5 [ROOT SESSION]</span>
        <span style="color:var(--primary); font-size:10px;">● ONLINE</span>
      </div>
      
      <div class="cli-output" id="cliOutputContent">peace of the island of sor/ber peoples · Terminal Console
Type 'help' to see available commands, or execute any tool directly.
Examples: 'autorecon torvalds', 'crypto 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'dorks target', 'wayback github.com/user'
----------------------------------------------------------------------
</div>

      <div class="cli-prompt-row">
        <span class="cli-prompt-label">root@cyberhub:~#</span>
        <input type="text" id="cliInputField" class="cli-input" placeholder="Введите команду (help, autorecon, crypto, dorks, sherlock, wayback, crtsh, clear)..." autofocus onkeydown="handleCliKeyDown(event)">
        <button class="btn btn-primary" style="padding:5px 12px; font-size:11px;" onclick="executeCliCommand()">RUN</button>
      </div>
    </div>
  </div>

  <!-- ВЬЮ 4: ИНТЕРАКТИВНЫЙ ГРАФ СВЯЗЕЙ (VIS.JS) -->
  <div class="view-page" id="graphView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог
    </div>

    <div class="workspace-box">
      <div class="workspace-title" style="color:var(--cyan); display:flex; justify-content:space-between; align-items:center;">
        <span><i class="fa-solid fa-project-diagram"></i> Интерактивный Граф Связей Расследования</span>
        <button class="btn btn-secondary" style="padding:3px 8px; font-size:10px;" onclick="exportCurrentGraph()"><i class="fa-solid fa-camera"></i> Сохранить PNG</button>
      </div>
      <div style="font-size:11px; color:var(--text-muted); margin-bottom:12px;">
        Визуализация цифровых связей между профилями, коммит-email, блокчейн-кошельками и инфраструктурой.
      </div>

      <div class="input-row">
        <input class="tool-input" id="graphTargetInput" placeholder="Введите никнейм, логин GitHub, домен или кошелек..." onkeydown="if(event.key==='Enter') runGraphDirectScan()">
        <button class="btn btn-cyan" onclick="runGraphDirectScan()"><i class="fa-solid fa-bolt"></i> Построить граф</button>
      </div>

      <div class="loader" id="graphLoader">
        <div class="spinner" style="border-top-color:var(--cyan);"></div>
        <span style="font-size:11px; color:var(--cyan);">Сквозной сбор узлов и построение графа связей...</span>
      </div>

      <div id="graphContainerBox" style="display:none;">
        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:8px; font-size:10px; color:#cbd5e1;">
          <span>🟢 Цель</span> · <span>🔵 Профиль</span> · <span>🔴 Commit Email</span> · <span>🟣 ФИО</span> · <span>🪙 Крипто</span> · <span>🌐 Сервер/IP</span>
        </div>
        <div id="visNetworkCanvas" style="width:100%; height:400px; background:#020509; border:1px solid #162a44; border-radius:12px; margin-bottom:12px;"></div>
        
        <div class="custom-card" id="graphDossierBox" style="border-color:var(--primary);">
          <div class="custom-card-title" style="color:var(--primary); display:flex; justify-content:space-between;">
            <span><i class="fa-solid fa-file-shield"></i> Тактическое Досье по Графу</span>
            <button class="btn btn-primary" style="padding:3px 8px; font-size:10px;" onclick="printDossierReport()"><i class="fa-solid fa-print"></i> Печать / PDF</button>
          </div>
          <div id="graphDossierContent" class="ai-dossier-text" style="color:#cbd5e1; font-size:12px; line-height:1.55; white-space:pre-wrap;"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- ВЬЮ 5: АТРИБУЦИЯ ВИРТОВ -->
  <div class="view-page" id="attributionView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог
    </div>

    <div class="workspace-box">
      <div class="workspace-title" style="color:var(--purple);"><i class="fa-solid fa-user-secret"></i> Детектор виртов & Атрибуция основы</div>
      <div style="font-size:11px; color:var(--text-muted); margin-bottom:12px;">
        Сопоставление цифровых следов виртов, купленных аккаунтов Telegram и поиск истинного владельца через мутации и метаданные ID.
      </div>

      <div class="input-row">
        <input class="tool-input" id="attrTargetInput" placeholder="Введите юзернейм или ID вирта (например: @sock_puppet)" onkeydown="if(event.key==='Enter') runAttributionScanDirect()">
        <button class="btn btn-purple" onclick="runAttributionScanDirect()"><i class="fa-solid fa-bolt"></i> Найти основу</button>
      </div>

      <div style="margin-bottom:10px;">
        <input class="tool-input" id="attrTextSample" placeholder="Образец сообщений жертвы (опционально, для стилометрического анализа)...">
      </div>

      <div class="loader" id="attrLoader">
        <div class="spinner" style="border-top-color:var(--purple);"></div>
        <span style="font-size:11px; color:var(--purple);">Анализ мутаций никнеймов и цифровых следов...</span>
      </div>

      <div id="attrResultBox"></div>
    </div>
  </div>

  <!-- ВЬЮ 6: ФОТО & EXIF GEOLOCATION -->
  <div class="view-page" id="photoView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог
    </div>

    <div class="workspace-box">
      <div class="workspace-title" style="color:var(--cyan);"><i class="fa-solid fa-camera"></i> Разведка по Фото & Извлечение EXIF/GPS</div>
      <div class="upload-dropzone" onclick="document.getElementById('directPhotoInput').click()" ondragover="event.preventDefault()" ondrop="handlePhotoDrop(event, 'directPhotoInput')">
        <i class="fa-solid fa-cloud-arrow-up" style="font-size:36px; color:var(--cyan); margin-bottom:8px;"></i>
        <div style="font-weight:700; color:#fff; font-size:14px;">Нажмите или перетащите фото для анализа</div>
        <div style="font-size:11px; color:var(--text-muted); margin-top:3px;">Извлечение GPS координат, камеры, даты съемки и поиск дубликатов в Сети</div>
        <input type="file" id="directPhotoInput" accept="image/*" style="display:none;" onchange="processDirectPhoto(this)">
      </div>
      <img id="directPhotoPreview" class="upload-preview">

      <div class="loader" id="photoLoader">
        <div class="spinner" style="border-top-color:var(--cyan);"></div>
        <span style="font-size:11px; color:var(--cyan);">Анализ структуры снимка и поиск совпадений...</span>
      </div>

      <div id="photoResultBox" style="margin-top:12px;"></div>
    </div>
  </div>

  <!-- ВЬЮ 7: ДЕКОДЕРЫ & DORK BUILDER -->
  <div class="view-page" id="decoderView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог
    </div>

    <div class="workspace-box">
      <div class="workspace-title"><i class="fa-solid fa-wrench"></i> Лаборатория Кибер-Декодеров</div>
      <textarea class="tool-input" id="decoderInputData" placeholder="Вставьте зашифрованную строку, хеш (MD5/SHA256) или JWT токен..." style="width:100%; height:80px; resize:vertical; margin-bottom:8px;"></textarea>

      <div class="btn-group" style="margin-bottom:12px;">
        <button class="btn btn-primary" onclick="runDecoderAction('hash_id')"><i class="fa-solid fa-fingerprint"></i> Хеш-Идентификатор</button>
        <button class="btn btn-cyan" onclick="runDecoderAction('jwt_decode')"><i class="fa-solid fa-shield-halved"></i> JWT Token</button>
        <button class="btn btn-secondary" onclick="runDecoderAction('base64_decode')">Base64 Decode</button>
        <button class="btn btn-secondary" onclick="runDecoderAction('base64_encode')">Base64 Encode</button>
        <button class="btn btn-secondary" onclick="runDecoderAction('hex_decode')">Hex Decode</button>
        <button class="btn btn-secondary" onclick="runDecoderAction('rot13')">ROT13</button>
      </div>

      <div id="decoderResultBox" style="display:none;" class="custom-card">
        <div class="custom-card-title"><i class="fa-solid fa-terminal"></i> Результат обработки</div>
        <pre id="decoderOutputPre" style="font-family:monospace; color:var(--primary); font-size:12px; white-space:pre-wrap; word-break:break-all; max-height:250px; overflow-y:auto;"></pre>
      </div>
    </div>
  </div>

  <!-- ВЬЮ 8: АДМИН-ПАНЕЛЬ -->
  <div class="view-page" id="usersAdminView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог
    </div>

    <div class="workspace-box">
      <div class="workspace-title" style="display:flex; justify-content:space-between; align-items:center;">
        <span><i class="fa-solid fa-users-gear"></i> Управление Пользователями & Квотами Stars</span>
        <button class="btn btn-purple" onclick="toggleAddUserModal()"><i class="fa-solid fa-plus"></i> Добавить</button>
      </div>

      <div id="addUserFormBox" style="display:none; background:#0d1524; padding:12px; border-radius:8px; margin-bottom:10px; border:1px solid #1e293b;">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:6px;">
          <input class="tool-input" id="newUsername" placeholder="Позывной / Никнейм">
          <input class="tool-input" id="newNotes" placeholder="Telegram ID / Примечание">
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:6px;">
          <select class="tool-input" id="newRole">
            <option value="user">User (Обычный)</option>
            <option value="vip">VIP (Бесконечный)</option>
            <option value="admin">Admin (Владелец)</option>
          </select>
          <input class="tool-input" id="newPassword" type="password" placeholder="Пароль (опционально)">
        </div>
        <div class="btn-group">
          <button class="btn btn-primary" onclick="submitCreateUser()"><i class="fa-solid fa-check"></i> Создать</button>
          <button class="btn btn-secondary" onclick="toggleAddUserModal()">Отмена</button>
        </div>
      </div>

      <div style="overflow-x:auto;">
        <table class="admin-table">
          <thead>
            <tr><th>Позывной / Ник</th><th>Telegram</th><th>Квота (Stars)</th><th>Статус</th><th>Антифрод</th><th>Управление квотой</th><th>Действия</th></tr>
          </thead>
          <tbody id="usersTableBody">
            <tr><td colspan="7" style="text-align:center; padding:10px;">Загрузка пользователей...</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="workspace-box">
      <div class="workspace-title" style="display:flex; justify-content:space-between; align-items:center;">
        <span><i class="fa-solid fa-network-wired"></i> Журнал IP-визитов и подключений</span>
        <button class="btn btn-secondary" onclick="loadAdminVisitors()"><i class="fa-solid fa-rotate"></i> Обновить</button>
      </div>
      <div style="overflow-x:auto;">
        <table class="admin-table">
          <thead>
            <tr><th>Время</th><th>Пользователь / Ник</th><th>IP адрес</th><th>Геолокация</th><th>Клиент</th></tr>
          </thead>
          <tbody id="visitorsTableBody">
            <tr><td colspan="5" style="text-align:center; padding:10px;">Загрузка IP-журнала...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ВЬЮ 9: ЭКРАН БЛОКИРОВКИ -->
  <div class="view-page" id="blockedView">
    <div class="auth-container">
      <div style="background:#13090e; border:2px solid var(--danger); border-radius:16px; padding:28px 22px; max-width:400px; width:100%; box-shadow:0 0 40px rgba(255,51,102,0.35); text-align:center;">
        <i class="fa-solid fa-ban" style="font-size:52px; color:var(--danger); margin-bottom:14px;"></i>
        <div style="font-size:18px; font-weight:800; color:#fff; margin-bottom:8px;">ДОСТУП ЗАБЛОКИРОВАН</div>
        <div style="font-size:12px; color:#cbd5e1; line-height:1.55;">
          Ваш аккаунт деактивирован администратором.<br>Доступ к платформе закрыт.
        </div>
      </div>
    </div>
  </div>

  <div class="footer-info">
    peace of the island of sor/ber peoples · OSINT Intelligence & Recon
  </div>
</div>

<script>
let FULL_CATALOG = {catalog_json};
let currentCategory = 'all';
let activeTool = null;
let currentSessionUser = '';
let tgUserId = '';

let isUserAdmin = false;
let currentSessionUser = 'Agent';
let tgUserId = '';

function openAdminPanel() {{
  showView('usersAdminView');
  loadAdminUsers();
  loadAdminVisitors();
}}

function unlockAdmin() {{
  const pass = prompt('Введите пароль администратора (ADMIN_TOKEN):');
  if (pass) {{
    localStorage.setItem('osint_admin_token', pass);
    initUserProfile();
  }}
}}

function handleUserBadgeClick() {{
  if (isUserAdmin) {{
    openAdminPanel();
  }} else {{
    const ask = confirm('Открыть панель администратора? Нажмите ОК для ввода пароля.');
    if (ask) unlockAdmin();
  }}
}}

async function loadAdminUsers() {{
  const tbody = document.getElementById('usersTableBody');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:10px; color:#94a3b8;">Загрузка пользователей...</td></tr>';

  const token = localStorage.getItem('osint_admin_token') || 'admin123';
  try {{
    const res = await fetch(`/api/admin/users?token=${{encodeURIComponent(token)}}`, {{
      headers: {{
        'X-Telegram-User-Id': tgUserId || '5233450569',
        'X-Admin-Token': token
      }}
    }});
    const data = await res.json();
    if (!data.ok) {{
      tbody.innerHTML = `<tr><td colspan="7" style="color:var(--danger); text-align:center; padding:10px;">Ошибка: ${{data.error}}</td></tr>`;
      return;
    }}
    const users = data.users || [];
    tbody.innerHTML = '';
    users.forEach(u => {{
      const tr = document.createElement('tr');
      const statusTxt = u.status === 'active' ? '<span style="color:var(--accent-green); font-weight:700;">🟢 АКТИВЕН</span>' : '<span style="color:var(--danger); font-weight:700;">🔴 БЛОК</span>';
      const tgInfo = u.tg_username ? `@${{u.tg_username}}` : (u.tg_id ? `ID:${{u.tg_id}}` : '—');
      const twinkTxt = u.is_twink ? '<span style="color:var(--danger); font-weight:800;">⚠️ Твинк</span>' : '<span style="color:var(--text-muted);">Чисто</span>';
      const quotaDisplay = u.is_unlimited ? '<span style="color:var(--accent-yellow); font-weight:800;">👑 VIP (∞)</span>' : `<b>${{u.scan_balance}}</b> ост.`;

      tr.innerHTML = `
        <td><b>${{u.nickname || u.username}}</b></td>
        <td style="font-size:10px; color:var(--primary);">${{tgInfo}}</td>
        <td>${{quotaDisplay}}</td>
        <td>${{statusTxt}}</td>
        <td>${{twinkTxt}}</td>
        <td>
          <div class="btn-group">
            <button class="btn btn-secondary" style="padding:2px 5px; font-size:9px;" onclick="adminSetQuota('${{u.id_key || u.tg_id || u.username}}', 20, 'add')">+20</button>
            <button class="btn btn-secondary" style="padding:2px 5px; font-size:9px;" onclick="adminSetQuota('${{u.id_key || u.tg_id || u.username}}', 50, 'add')">+50</button>
            <button class="btn btn-yellow" style="padding:2px 5px; font-size:9px;" onclick="adminSetQuota('${{u.id_key || u.tg_id || u.username}}', 0, 'unlimited')">VIP</button>
            <button class="btn btn-secondary" style="padding:2px 5px; font-size:9px;" onclick="adminSetQuota('${{u.id_key || u.tg_id || u.username}}', 5, 'reset')">Сброс</button>
          </div>
        </td>
        <td>
          <div class="btn-group">
            <button class="btn btn-secondary" style="padding:3px 6px; font-size:9px;" onclick="toggleUserStatus('${{u.id_key || u.tg_id || u.username}}')">${{u.status === 'active' ? 'Блок' : 'Разблок'}}</button>
            ${{u.role !== 'admin' ? `<button class="btn btn-danger" style="padding:3px 6px; font-size:9px;" onclick="deleteUser('${{u.id_key || u.tg_id || u.username}}')"><i class="fa-solid fa-trash"></i></button>` : ''}}
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    }});
  }} catch (err) {{
    tbody.innerHTML = `<tr><td colspan="7" style="color:var(--danger); text-align:center;">Ошибка соединения: ${{err.message}}</td></tr>`;
  }}
}}

async function loadAdminVisitors() {{
  const tbody = document.getElementById('visitorsTableBody');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:10px; color:#94a3b8;">Загрузка журнала визитов...</td></tr>';

  const token = localStorage.getItem('osint_admin_token') || 'admin123';
  try {{
    const res = await fetch(`/api/admin/visitors?limit=50&token=${{encodeURIComponent(token)}}`, {{
      headers: {{
        'X-Telegram-User-Id': tgUserId || '5233450569',
        'X-Admin-Token': token
      }}
    }});
    const data = await res.json();
    if (!data.ok) {{
      tbody.innerHTML = `<tr><td colspan="5" style="color:var(--danger); text-align:center; padding:10px;">Ошибка: ${{data.error}}</td></tr>`;
      return;
    }}
    const rows = data.visitors || [];
    tbody.innerHTML = '';
    rows.forEach(r => {{
      const tr = document.createElement('tr');
      const timeStr = (r.ts || '').substr(11, 8) || (r.ts || '—');
      const userDisplay = r.user || (r.tg_username ? `@${{r.tg_username}}` : (r.tg_id ? `TG:${{r.tg_id}}` : 'Гость'));
      const geoDisplay = r.country ? `${{r.country}} ${{r.city ? `(${{r.city}})` : ''}}` : 'GLOBAL';

      tr.innerHTML = `
        <td style="color:#64748b; font-size:10px;">${{timeStr}}</td>
        <td style="font-size:11px; font-weight:700; color:#fff;">${{userDisplay}}</td>
        <td style="font-family:monospace; color:var(--primary); font-weight:700;">${{r.ip || '—'}}</td>
        <td><span class="badge badge-api">${{geoDisplay}}</span></td>
        <td style="font-size:10px; color:#64748b; max-width:140px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${{r.ua || 'Web/TG'}}</td>
      `;
      tbody.appendChild(tr);
    }});
  }} catch (err) {{
    tbody.innerHTML = '<tr><td colspan="5" style="color:var(--danger); text-align:center;">Ошибка загрузки журнала</td></tr>';
  }}
}}

async function adminSetQuota(username, amount, mode) {{
  const token = localStorage.getItem('osint_admin_token') || 'admin123';
  try {{
    const res = await fetch('/api/admin/user/set-quota', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
        'X-Telegram-User-Id': tgUserId || '5233450569',
        'X-Admin-Token': token
      }},
      body: JSON.stringify({{ username, amount, mode }})
    }});
    const data = await res.json();
    if (data.ok) {{
      loadAdminUsers();
    }} else {{
      alert('Ошибка: ' + data.error);
    }}
  }} catch (e) {{
    alert('Ошибка: ' + e.message);
  }}
}}

async function toggleUserStatus(username) {{
  const token = localStorage.getItem('osint_admin_token') || 'admin123';
  try {{
    await fetch('/api/admin/users/toggle_status', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
        'X-Telegram-User-Id': tgUserId || '5233450569',
        'X-Admin-Token': token
      }},
      body: JSON.stringify({{ username }})
    }});
    loadAdminUsers();
  }} catch (e) {{}}
}}

async function deleteUser(username) {{
  if (!confirm(`Удалить пользователя ${{username}}?`)) return;
  const token = localStorage.getItem('osint_admin_token') || 'admin123';
  try {{
    await fetch('/api/admin/users/delete', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
        'X-Telegram-User-Id': tgUserId || '5233450569',
        'X-Admin-Token': token
      }},
      body: JSON.stringify({{ username }})
    }});
    loadAdminUsers();
  }} catch (e) {{}}
}}

async function submitCreateUser() {{
  const username = document.getElementById('newUsername').value.trim();
  const password = document.getElementById('newPassword').value.trim();
  const role = document.getElementById('newRole').value;
  const notes = document.getElementById('newNotes').value.trim();

  if (!username) {{ alert('Укажите позывной'); return; }}
  const token = localStorage.getItem('osint_admin_token') || 'admin123';

  try {{
    const res = await fetch('/api/admin/users/create', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
        'X-Telegram-User-Id': tgUserId || '5233450569',
        'X-Admin-Token': token
      }},
      body: JSON.stringify({{ username, password, role, notes }})
    }});
    const data = await res.json();
    if (data.ok) {{
      toggleAddUserModal();
      document.getElementById('newUsername').value = '';
      loadAdminUsers();
    }} else {{ alert('Ошибка: ' + data.error); }}
  }} catch (e) {{ alert('Ошибка: ' + e.message); }}
}}

async function initUserProfile() {{
  const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
  let tgId = '';
  let tgUser = '';
  let tgName = '';

  if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) {{
    tgId = String(tg.initDataUnsafe.user.id);
    tgUser = tg.initDataUnsafe.user.username || '';
    tgName = `${{tg.initDataUnsafe.user.first_name || ''}} ${{tg.initDataUnsafe.user.last_name || ''}}`.trim();
  }}

  const urlParams = new URLSearchParams(window.location.search);
  const paramId = urlParams.get('tg_id') || urlParams.get('id');
  const paramToken = urlParams.get('token') || urlParams.get('admin');
  if (paramToken) localStorage.setItem('osint_admin_token', paramToken);

  if (!tgId && paramId) tgId = String(paramId);
  
  if (!tgId) {{
    let localStoredId = localStorage.getItem('osint_local_uid');
    if (!localStoredId) {{
      localStoredId = 'browser_' + Math.floor(100000 + Math.random() * 900000);
      localStorage.setItem('osint_local_uid', localStoredId);
    }}
    tgId = localStoredId;
  }}
  tgUserId = tgId;

  const adminToken = localStorage.getItem('osint_admin_token') || '';

  // Auto-detect admin
  if (tgId === '5233450569' || adminToken === 'admin123' || urlParams.get('admin') === '1') {{
    isUserAdmin = true;
  }}

  currentSessionUser = tgUser || tgName || (isUserAdmin ? 'Admin' : `Agent_${{tgId.slice(-4)}}`);
  
  const spanEl = document.getElementById('currentUsernameSpan');
  if (spanEl) spanEl.innerText = isUserAdmin ? `${{currentSessionUser}} 👑` : currentSessionUser;
  
  const adminBtn = document.getElementById('navAdminBtn');
  if (adminBtn) adminBtn.style.display = isUserAdmin ? 'inline-flex' : 'none';

  const icon = document.getElementById('userBadgeIcon');
  if (icon && isUserAdmin) {{
    icon.className = 'fa-solid fa-crown';
    icon.style.color = 'var(--accent-yellow)';
  }}

  try {{
    const res = await fetch('/api/user/profile', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
        'X-Telegram-User-Id': tgId,
        'X-Admin-Token': adminToken
      }},
      body: JSON.stringify({{ tg_id: tgId, tg_username: tgUser, tg_name: tgName, admin_token: adminToken }})
    }});
    const data = await res.json();

    if (data.blocked) {{
      showView('blockedView');
      return;
    }}

    if (data.is_admin || tgId === '5233450569' || adminToken === 'admin123') {{
      isUserAdmin = true;
      if (adminBtn) adminBtn.style.display = 'inline-flex';
      if (spanEl) spanEl.innerText = (data.nickname || 'Admin') + ' 👑';
      if (icon) {{
        icon.className = 'fa-solid fa-crown';
        icon.style.color = 'var(--accent-yellow)';
      }}
    }}

    const qSpan = document.getElementById('quotaSpan');
    if (qSpan) {{
      qSpan.innerText = (data.is_unlimited || isUserAdmin) ? '👑 VIP (∞)' : `${{data.scan_balance !== undefined ? data.scan_balance : 5}} Запросов`;
    }}
  }} catch (err) {{
    console.warn('Profile init:', err);
  }}
}}

renderCatalog();
initUserProfile();
</script>
</body>
</html>
"""