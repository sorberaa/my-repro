import json
from pathlib import Path
from src.catalog import CATALOG

html_path = Path("index.html")

catalog_json = json.dumps(CATALOG, ensure_ascii=False, indent=2)

full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>OSINT Cyber Hub · Sherlock, Sockpuppet & Hacker Lab</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
<style>
:root {{
  --bg: #05070a;
  --card-bg: #0b0f17;
  --card-border: #182234;
  --primary: #00ff66;
  --primary-glow: rgba(0, 255, 102, 0.28);
  --cyan: #00e5ff;
  --cyan-glow: rgba(0, 229, 255, 0.22);
  --purple: #a855f7;
  --purple-glow: rgba(168, 85, 247, 0.25);
  --danger: #ff3366;
  --text: #e2e8f0;
  --text-muted: #8492a6;
  --term-bg: #020408;
  --term-border: #00ff6633;
}}

* {{ margin:0; padding:0; box-sizing:border-box; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-tap-highlight-color: transparent; }}
body {{ background:var(--bg); color:var(--text); min-height:100vh; padding:10px; padding-bottom:70px; position:relative; overflow-x:hidden; }}

/* Canvas для эффекта матрицы */
#matrixCanvas {{ position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:0; opacity:0.18; display:none; }}

.container {{ max-width:760px; margin:0 auto; position:relative; z-index:1; }}

/* Навбар */
.navbar {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--card-border); padding:8px 0 12px; margin-bottom:12px; background:rgba(5,7,10,0.85); backdrop-filter:blur(10px); }}
.brand {{ font-size:16px; font-weight:800; color:#fff; display:flex; align-items:center; gap:8px; text-transform:uppercase; letter-spacing:0.5px; cursor:pointer; }}
.brand i {{ color:var(--primary); text-shadow:0 0 10px var(--primary-glow); }}
.nav-actions {{ display:flex; align-items:center; gap:6px; flex-wrap:wrap; }}

.user-badge {{ display:inline-flex; align-items:center; gap:6px; padding:5px 10px; background:#101726; border-radius:8px; font-size:11px; font-weight:700; color:var(--cyan); border:1px solid #1e293b; cursor:pointer; }}
.user-badge:hover {{ border-color:var(--primary); }}

.view-page {{ display:none; }}
.view-page.active {{ display:block; }}

/* Страница Регистрации */
.auth-container {{ display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:80vh; padding:16px; text-align:center; }}
.auth-card {{ background:linear-gradient(135deg, #091322, #0d1e34); border:2px solid var(--cyan); border-radius:16px; padding:28px 22px; max-width:420px; width:100%; box-shadow:0 0 40px rgba(0,229,255,0.25); }}
.auth-icon {{ font-size:48px; color:var(--cyan); margin-bottom:14px; text-shadow:0 0 20px var(--cyan-glow); }}
.auth-title {{ font-size:18px; font-weight:800; color:#fff; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.5px; }}
.auth-subtitle {{ font-size:12px; color:#94a3b8; margin-bottom:20px; line-height:1.5; }}
.auth-input {{ width:100%; padding:13px; background:#04070c; border:1px solid var(--cyan); border-radius:10px; color:#fff; font-size:14px; font-weight:700; text-align:center; outline:none; margin-bottom:14px; }}
.auth-input:focus {{ border-color:var(--primary); box-shadow:0 0 15px var(--primary-glow); }}

/* Главный быстрый поиск на первой странице */
.quick-recon-box {{ background:linear-gradient(135deg, #09121f, #0d1a2d); border:1px solid #1e3557; border-radius:12px; padding:14px; margin-bottom:14px; box-shadow:0 4px 20px rgba(0,0,0,0.5); }}
.quick-title {{ font-size:13px; font-weight:800; color:#fff; display:flex; align-items:center; gap:6px; margin-bottom:10px; text-transform:uppercase; }}
.quick-input-group {{ display:flex; gap:6px; }}
.quick-input {{ flex:1; padding:11px 13px; background:#04070c; border:1px solid #1e293b; border-radius:8px; color:#fff; font-size:13px; outline:none; transition:border .2s; }}
.quick-input:focus {{ border-color:var(--primary); box-shadow:0 0 10px var(--primary-glow); }}

/* Поиск по каталогу */
.search-box {{ position:relative; margin-bottom:10px; }}
.search-box i {{ position:absolute; left:14px; top:50%; transform:translateY(-50%); color:var(--text-muted); font-size:13px; }}
.search-box input {{ width:100%; padding:11px 14px 11px 38px; background:#080c14; border:1px solid var(--card-border); border-radius:10px; color:#fff; font-size:13px; outline:none; transition:all .2s; }}
.search-box input:focus {{ border-color:var(--primary); box-shadow:0 0 10px var(--primary-glow); }}

/* Категории (Chips) */
.filter-chips {{ display:flex; gap:6px; overflow-x:auto; padding-bottom:6px; margin-bottom:12px; scrollbar-width:none; -webkit-overflow-scrolling:touch; }}
.filter-chips::-webkit-scrollbar {{ display:none; }}
.chip {{ padding:6px 11px; background:var(--card-bg); border:1px solid var(--card-border); border-radius:16px; font-size:11px; font-weight:600; color:var(--text-muted); white-space:nowrap; cursor:pointer; }}
.chip.active, .chip:hover {{ background:rgba(0,255,102,0.12); border-color:var(--primary); color:var(--primary); }}

/* Каталог */
.group-title {{ font-size:13px; font-weight:800; color:var(--cyan); margin:14px 0 6px; display:flex; align-items:center; gap:6px; text-transform:uppercase; }}
.group-desc {{ font-size:11px; color:var(--text-muted); margin-bottom:8px; }}

.cards-grid {{ display:grid; gap:8px; }}
.card {{ background:var(--card-bg); border:1px solid var(--card-border); border-radius:10px; padding:12px; cursor:pointer; transition:all .15s; }}
.card:hover {{ border-color:var(--cyan); transform:translateY(-1px); }}
.card-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:4px; gap:6px; }}
.card-title {{ font-size:14px; font-weight:700; color:#fff; display:flex; align-items:center; gap:6px; }}
.badge {{ font-size:9px; font-weight:700; padding:2px 7px; border-radius:10px; text-transform:uppercase; }}
.badge-api {{ background:rgba(0,255,102,0.15); color:var(--primary); border:1px solid var(--primary); }}
.badge-web {{ background:rgba(0,229,255,0.15); color:var(--cyan); border:1px solid var(--cyan); }}
.badge-doc {{ background:rgba(148,163,184,0.12); color:var(--text-muted); border:1px solid var(--text-muted); }}

.card-purpose {{ font-size:11px; color:var(--text-muted); line-height:1.4; margin-bottom:8px; }}

/* Кнопки */
.btn-group {{ display:flex; flex-wrap:wrap; gap:6px; }}
.btn {{ padding:8px 14px; font-size:11px; font-weight:700; border-radius:8px; border:none; cursor:pointer; display:inline-flex; align-items:center; gap:6px; text-decoration:none; }}
.btn-primary {{ background:var(--primary); color:#000; font-weight:800; }}
.btn-primary:hover {{ filter:brightness(1.1); box-shadow:0 0 10px var(--primary-glow); }}
.btn-secondary {{ background:#111927; color:var(--text); border:1px solid #1e293b; }}
.btn-purple {{ background:linear-gradient(135deg, #7c3aed, #9333ea); color:#fff; }}
.btn-cyan {{ background:linear-gradient(135deg, #00e5ff, #0099ff); color:#000; font-weight:800; }}
.btn-danger {{ background:rgba(255,51,102,0.15); color:var(--danger); border:1px solid var(--danger); }}

/* Страница инструмента */
.tool-view-header {{ background:#090d16; border:1px solid var(--card-border); border-radius:12px; padding:14px; margin-bottom:12px; }}
.back-btn {{ display:inline-flex; align-items:center; gap:6px; color:var(--cyan); font-size:12px; font-weight:600; cursor:pointer; margin-bottom:8px; }}
.tool-view-title {{ font-size:17px; font-weight:800; color:#fff; margin-bottom:4px; }}
.tool-view-desc {{ font-size:12px; color:var(--text-muted); margin-bottom:10px; }}

.workspace-box {{ background:#080c14; border:1px solid var(--card-border); border-radius:12px; padding:14px; margin-bottom:12px; }}
.workspace-title {{ font-size:13px; font-weight:800; color:var(--primary); margin-bottom:10px; display:flex; align-items:center; gap:6px; text-transform:uppercase; }}
.input-row {{ display:flex; gap:6px; margin-bottom:10px; }}
.tool-input {{ flex:1; padding:10px 12px; background:#04070c; border:1px solid var(--card-border); border-radius:8px; color:#fff; font-size:13px; outline:none; }}
.tool-input:focus {{ border-color:var(--primary); }}

/* Загрузка фото */
.upload-dropzone {{ border:2px dashed #1e293b; border-radius:10px; padding:18px; text-align:center; cursor:pointer; background:#04070c; margin-bottom:10px; }}
.upload-dropzone:hover {{ border-color:var(--cyan); }}
.upload-preview {{ max-width:100%; max-height:220px; border-radius:8px; margin:8px auto; display:none; object-fit:contain; }}

/* ХАКЕРСКАЯ КОНСОЛЬ В СТИЛЕ КИБЕРПАНК */
.hacker-terminal {{ background:var(--term-bg); border:1px solid var(--term-border); border-radius:10px; padding:12px; margin-bottom:12px; box-shadow:0 0 20px rgba(0,255,102,0.08); position:relative; overflow:hidden; }}
.term-topbar {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #14281c; padding-bottom:6px; margin-bottom:8px; font-size:11px; font-family:'Courier New', monospace; font-weight:700; color:var(--primary); }}
.term-dots {{ display:flex; gap:4px; }}
.term-dot {{ width:8px; height:8px; border-radius:50%; display:inline-block; }}
.term-dot-red {{ background:#ff3366; }}
.term-dot-yellow {{ background:#ffaa00; }}
.term-dot-green {{ background:#00ff66; box-shadow:0 0 6px #00ff66; }}
.term-log-content {{ font-family:'Courier New', Consolas, monospace; font-size:11px; line-height:1.45; color:#38ef7d; word-break:break-all; white-space:pre-wrap; max-height:260px; overflow-y:auto; scrollbar-width:thin; }}

/* ИНТЕРАКТИВНЫЙ CLI ТЕРМИНАЛ */
.cli-console-box {{ background:#020407; border:2px solid #00ff6644; border-radius:12px; padding:14px; box-shadow:0 0 30px rgba(0,255,102,0.12); font-family:'Courier New', Consolas, monospace; }}
.cli-output {{ min-height:220px; max-height:380px; overflow-y:auto; color:#00ff66; font-size:12px; line-height:1.5; white-space:pre-wrap; margin-bottom:10px; scrollbar-width:thin; }}
.cli-prompt-row {{ display:flex; align-items:center; gap:8px; border-top:1px solid #0d2818; padding-top:8px; }}
.cli-prompt-label {{ color:var(--cyan); font-weight:700; font-size:12px; }}
.cli-input {{ flex:1; background:transparent; border:none; color:#00ff66; font-family:'Courier New', monospace; font-size:13px; font-weight:700; outline:none; }}

/* БЛОК ДАННЫХ */
.custom-card {{ background:linear-gradient(135deg, #091322, #0d1e34); border:1px solid #1e3a5f; border-radius:10px; padding:12px; margin-bottom:12px; }}
.custom-card-title {{ font-size:13px; font-weight:800; color:#fff; display:flex; align-items:center; gap:6px; margin-bottom:10px; text-transform:uppercase; }}
.custom-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }}
.custom-item {{ background:rgba(0,0,0,0.35); padding:8px 10px; border-radius:7px; border:1px solid rgba(0,229,255,0.15); }}
.custom-label {{ font-size:10px; font-weight:700; color:var(--cyan); text-transform:uppercase; margin-bottom:2px; }}
.custom-val {{ font-size:12px; font-weight:700; color:#fff; word-break:break-all; }}

/* Информационная плашка */
.info-banner {{ background:#0a1322; border:1px solid #1a2f4c; border-radius:8px; padding:10px 12px; font-size:11px; color:#cbd5e1; line-height:1.5; margin-bottom:10px; }}

/* AI Досье Блок */
.ai-dossier-card {{ background:#090e18; border:1px solid #1a2942; border-radius:10px; padding:12px; margin-bottom:12px; }}
.ai-dossier-title {{ font-size:13px; font-weight:800; color:var(--purple); display:flex; align-items:center; gap:6px; margin-bottom:8px; }}
.ai-dossier-text {{ font-size:12px; color:#cbd5e1; line-height:1.55; white-space:pre-wrap; }}

/* Таблицы */
.admin-table {{ width:100%; border-collapse:collapse; font-size:11px; margin-top:8px; }}
.admin-table th {{ text-align:left; padding:8px 6px; background:#0e1624; color:var(--text-muted); border-bottom:1px solid #1a273b; }}
.admin-table td {{ padding:8px 6px; border-bottom:1px solid #0f1828; color:#cbd5e1; }}

/* Сетка профилей */
.profiles-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(180px, 1fr)); gap:6px; margin-top:8px; }}
.profile-card {{ background:#080c14; border:1px solid #162235; border-radius:8px; padding:9px; display:flex; align-items:center; justify-content:space-between; }}
.profile-left {{ display:flex; align-items:center; gap:8px; }}
.profile-icon {{ font-size:15px; color:var(--cyan); width:18px; text-align:center; }}
.profile-name {{ font-size:12px; font-weight:700; color:#fff; }}
.profile-tag {{ font-size:9px; color:var(--primary); }}

.loader {{ display:none; text-align:center; padding:14px 0; }}
.spinner {{ border:2px solid rgba(255,255,255,0.1); border-top:2px solid var(--primary); border-radius:50%; width:22px; height:22px; animation:spin 0.8s linear infinite; margin:0 auto 8px; }}
@keyframes spin {{ 0% {{ transform:rotate(0deg); }} 100% {{ transform:rotate(360deg); }} }}

.code-wrap {{ position:relative; background:#04060a; border:1px solid #162235; border-radius:7px; padding:8px 10px; font-family:'Courier New', monospace; font-size:11px; color:var(--primary); word-break:break-all; white-space:pre-wrap; }}
.cmd-box {{ margin-bottom:8px; }}
.cmd-label {{ font-size:10px; font-weight:700; color:var(--cyan); text-transform:uppercase; margin-bottom:3px; display:flex; justify-content:space-between; align-items:center; }}
.copy-btn {{ position:absolute; right:6px; top:6px; background:#101726; color:var(--text-muted); border:none; border-radius:5px; padding:3px 6px; font-size:10px; cursor:pointer; }}
.copy-btn:hover {{ background:var(--primary); color:#000; }}

.footer-info {{ text-align:center; font-size:10px; color:#475569; margin-top:20px; }}
</style>
</head>
<body>

<canvas id="matrixCanvas"></canvas>

<div class="container">
  <!-- Навбар -->
  <div class="navbar" id="mainNavbar">
    <div class="brand" onclick="showView('catalogView')">
      <i class="fa-solid fa-terminal"></i> OSINT Cyber Hub
    </div>
    <div class="nav-actions">
      <div class="user-badge" id="currentUserBadge" style="display:none;" onclick="handleUserBadgeClick()">
        <i id="userBadgeIcon" class="fa-solid fa-user-check"></i> <span id="currentUsernameSpan">Позывной</span>
      </div>
      <button class="btn btn-primary" onclick="showView('terminalView')" style="padding:5px 9px; font-size:11px;"><i class="fa-solid fa-terminal"></i> CLI</button>
      <button class="btn btn-purple" id="navAttrBtn" onclick="showView('attributionView')" style="padding:5px 9px; font-size:11px;"><i class="fa-solid fa-user-secret"></i> Вирты</button>
      <button class="btn btn-secondary" id="navPhotoBtn" onclick="showView('photoView')" style="padding:5px 9px; font-size:11px;"><i class="fa-solid fa-camera"></i> Фото</button>
      <button class="btn btn-secondary" onclick="toggleMatrix()" style="padding:5px 8px; font-size:11px;" title="Матрица"><i class="fa-solid fa-code"></i></button>
    </div>
  </div>

  <!-- ВЬЮ 0: ОТДЕЛЬНАЯ СТРАНИЦА РЕГИСТРАЦИИ (ОБЯЗАТЕЛЬНЫЙ ЭКРАН) -->
  <div class="view-page" id="registerView">
    <div class="auth-container">
      <div class="auth-card">
        <i class="fa-solid fa-shield-halved auth-icon"></i>
        <div class="auth-title">OSINT CYBER HUB</div>
        <div class="auth-subtitle">
          Для доступа к системе расследований, базам Sherlock, поиску по GitHub и телефонной разведке зарегистрируйте ваш рабочий позывной:
        </div>
        <input type="text" id="regNicknameInput" class="auth-input" placeholder="Введите ваш позывной (например: Ghost_OSINT)" onkeydown="if(event.key==='Enter') doRegister()">
        <button class="btn btn-primary" style="width:100%; justify-content:center; padding:13px; font-size:13px;" onclick="doRegister()">
          <i class="fa-solid fa-check"></i> Зарегистрироваться и войти
        </button>
        <div id="regStatusMsg" style="margin-top:12px; font-size:12px; color:var(--danger); display:none;"></div>
      </div>
    </div>
  </div>

  <!-- ВЬЮ 1: ГЛАВНЫЙ КАТАЛОГ & БЫСТРЫЙ ПОИСК -->
  <div class="view-page" id="catalogView">
    
    <!-- БЫСТРЫЙ СКАНЕР ПРЯМО НА ГЛАВНОЙ -->
    <div class="quick-recon-box">
      <div class="quick-title">
        <i class="fa-solid fa-crosshairs" style="color:var(--primary);"></i> Экспресс-поиск: Sherlock · GitHub Email · Phone · Crypto
      </div>
      <div class="quick-input-group">
        <input type="text" id="mainQuickTargetInput" class="quick-input" placeholder="Введите никнейм, GitHub логин, телефон или криптокошелек..." onkeydown="if(event.key==='Enter') runMainQuickScan()">
        <button class="btn btn-primary" onclick="runMainQuickScan()"><i class="fa-solid fa-bolt"></i> Найти</button>
      </div>
    </div>

    <div class="search-box">
      <i class="fa-solid fa-magnifying-glass"></i>
      <input type="text" id="searchInput" placeholder="Фильтр программ: GitHub, Crypto, Sherlock, Telegram, Subfinder, EXIF, GeoIP..." oninput="renderCatalog()">
    </div>

    <div class="filter-chips">
      <div class="chip active" onclick="setFilter('all', this)">Все утилиты</div>
      <div class="chip" onclick="setFilter('hacker_crypto_git', this)">💻 GitHub & Crypto OSINT</div>
      <div class="chip" onclick="setFilter('telegram_osint', this)">✈️ Детектор виртов & TG</div>
      <div class="chip" onclick="setFilter('username_osint', this)">🔍 Sherlock Engine</div>
      <div class="chip" onclick="setFilter('social_google_instagram', this)">📱 Google & Instagram</div>
      <div class="chip" onclick="setFilter('web_infra_secrets', this)">🔑 Краулеры & Ключи</div>
      <div class="chip" onclick="setFilter('amazing_osint', this)">🌟 GeoINT & Спутники</div>
      <div class="chip" onclick="setFilter('email_checks', this)">📧 Почта & Телефон</div>
    </div>

    <div id="catalogContainer"></div>
  </div>

  <!-- ВЬЮ 2: СТРАНИЦА ИНСТРУМЕНТА -->
  <div class="view-page" id="toolView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог
    </div>

    <div class="tool-view-header">
      <div class="tool-view-title" id="tvTitle">Название утилиты</div>
      <div class="tool-view-desc" id="tvPurpose">Описание</div>
      <div class="btn-group" id="tvHeaderButtons"></div>
    </div>

    <div class="workspace-box">
      <div class="workspace-title"><i class="fa-solid fa-bolt"></i> Терминал запуска утилиты</div>
      
      <div id="tvPhotoUploaderBox" style="display:none;">
        <div class="upload-dropzone" onclick="document.getElementById('tvFileInput').click()">
          <i class="fa-solid fa-cloud-arrow-up" style="font-size:28px; color:var(--cyan); margin-bottom:6px;"></i>
          <div style="font-weight:700; color:#fff; font-size:12px;">Выбрать фото для экспертизы</div>
          <div style="font-size:11px; color:var(--text-muted);">EXIF, GPS, камера и поиск по картинкам</div>
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

    <div class="workspace-box">
      <div class="workspace-title"><i class="fa-solid fa-book-open"></i> Инструкция по установке (CLI)</div>
      <div id="tvInstallCommands"></div>
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
        <span style="color:var(--primary); font-size:10px;">● CONNECTED</span>
      </div>
      
      <div class="cli-output" id="cliOutputContent">OSINT CYBER HUB · Interactive Command Terminal
Type 'help' to see all available commands, or run scans directly.
Example: 'sherlock wertag20', 'github torvalds', 'phone +79991234567', 'crypto 0x...'
----------------------------------------------------------------------
</div>

      <div class="cli-prompt-row">
        <span class="cli-prompt-label">root@cyberhub:~#</span>
        <input type="text" id="cliInputField" class="cli-input" placeholder="Введите команду (help, scan, github, crypto, clear)..." autofocus onkeydown="handleCliKeyDown(event)">
        <button class="btn btn-primary" style="padding:4px 10px; font-size:11px;" onclick="executeCliCommand()">RUN</button>
      </div>
    </div>
  </div>

  <!-- ВЬЮ 4: СПЕЦИАЛИЗИРОВАННЫЙ МОДУЛЬ АТРИБУЦИИ ВИРТОВ -->
  <div class="view-page" id="attributionView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог
    </div>

    <div class="workspace-box">
      <div class="workspace-title" style="color:var(--purple);">
        <i class="fa-solid fa-user-secret"></i> Детектор виртов & Поиск основы (Sockpuppet Attribution)
      </div>
      <div style="font-size:11px; color:var(--text-muted); margin-bottom:10px; line-height:1.4;">
        Выявление реального владельца и основы, когда вам пишут с купленного или виртуального аккаунта.
      </div>

      <div style="margin-bottom:8px;">
        <input class="tool-input" id="attrTargetInput" placeholder="Юзернейм или ID вирта (например: @alex_temp или 6834920194)">
      </div>
      <div style="margin-bottom:8px;">
        <textarea class="tool-input" id="attrTextSample" style="height:65px; resize:none;" placeholder="Текст сообщений вирта (для стилометрии и выявления сленга/опечаток)..."></textarea>
      </div>

      <button class="btn btn-purple" style="width:100%; justify-content:center; padding:10px;" onclick="runAttributionScanDirect()">
        <i class="fa-solid fa-crosshairs"></i> Рассчитать атрибуцию и найти основу
      </button>

      <div class="loader" id="attrLoader">
        <div class="spinner" style="border-top-color:var(--purple);"></div>
        <span style="font-size:11px; color:var(--purple);">Корреляция мутаций никнеймов, ID и баз данных...</span>
      </div>

      <div id="attrResultBox" style="margin-top:12px;"></div>
    </div>
  </div>

  <!-- ВЬЮ 5: ФОТО & ЭКСПЕРТИЗА МЕТАДАННЫХ -->
  <div class="view-page" id="photoView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог
    </div>

    <div class="workspace-box">
      <div class="workspace-title" style="color:var(--cyan);"><i class="fa-solid fa-camera"></i> Экспертиза снимка (EXIF, GPS, Камера)</div>
      <div class="upload-dropzone" onclick="document.getElementById('directPhotoInput').click()">
        <i class="fa-solid fa-image" style="font-size:32px; color:var(--cyan); margin-bottom:6px;"></i>
        <div style="font-weight:700; color:#fff; font-size:12px;">Загрузить фото для анализа метаданных</div>
        <div style="font-size:11px; color:var(--text-muted); margin-top:4px;">JPG, PNG, WEBP, HEIC (без сжатия)</div>
        <input type="file" id="directPhotoInput" accept="image/*" style="display:none;" onchange="processDirectPhoto(this)">
      </div>

      <img id="directPhotoPreview" class="upload-preview">

      <div class="loader" id="photoLoader">
        <div class="spinner" style="border-top-color:var(--cyan);"></div>
        <span style="font-size:11px; color:var(--cyan);">Чтение тегов EXIF и геолокации...</span>
      </div>

      <div id="photoResultBox"></div>
    </div>
  </div>

  <!-- ВЬЮ 6: УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ (АДМИН) -->
  <div class="view-page" id="usersAdminView">
    <div class="back-btn" onclick="showView('catalogView')">
      <i class="fa-solid fa-arrow-left"></i> Назад в каталог
    </div>

    <div class="workspace-box">
      <div class="workspace-title" style="color:var(--purple); display:flex; justify-content:space-between; align-items:center;">
        <span><i class="fa-solid fa-users-gear"></i> Управление пользователями</span>
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
            <option value="vip">VIP (Расширенный)</option>
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
            <tr><th>Позывной / Ник</th><th>Telegram</th><th>IP адрес</th><th>Статус</th><th>Поисков</th><th>Действия</th></tr>
          </thead>
          <tbody id="usersTableBody">
            <tr><td colspan="6" style="text-align:center; padding:10px;">Загрузка пользователей...</td></tr>
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

  <!-- ВЬЮ 7: ЭКРАН БЛОКИРОВКИ -->
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
    OSINT Cyber Hub · Sherlock Engine · GitHub Recon · Crypto Intel · Matrix FX
  </div>
</div>

<script>
let FULL_CATALOG = {catalog_json};
let currentCategory = 'all';
let activeTool = null;
let currentSessionUser = '';
let tgUserId = '';
let isUserAdmin = false;
let cliHistory = [];
let cliHistoryIndex = -1;
let matrixActive = false;

const tg = window.Telegram?.WebApp;
if (tg) {{
  tg.expand();
  tg.ready();
}}

// MATRIX DIGITAL RAIN FX
function toggleMatrix() {{
  const canvas = document.getElementById('matrixCanvas');
  matrixActive = !matrixActive;
  canvas.style.display = matrixActive ? 'block' : 'none';
  if (matrixActive) startMatrixRain();
}}

function startMatrixRain() {{
  const canvas = document.getElementById('matrixCanvas');
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  const katakana = '0123456789ABCDEFｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜ';
  const fontSize = 14;
  const columns = canvas.width / fontSize;
  const drops = Array(Math.floor(columns)).fill(1);

  function draw() {{
    if (!matrixActive) return;
    ctx.fillStyle = 'rgba(5, 7, 10, 0.08)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#00ff66';
    ctx.font = fontSize + 'px monospace';

    for (let i = 0; i < drops.length; i++) {{
      const text = katakana.charAt(Math.floor(Math.random() * katakana.length));
      ctx.fillText(text, i * fontSize, drops[i] * fontSize);
      if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {{
        drops[i] = 0;
      }}
      drops[i]++;
    }}
    requestAnimationFrame(draw);
  }}
  draw();
}}

function showView(viewId) {{
  if (viewId === 'usersAdminView' && !isUserAdmin) return;
  document.querySelectorAll('.view-page').forEach(el => el.classList.remove('active'));
  const targetEl = document.getElementById(viewId);
  if (targetEl) targetEl.classList.add('active');
  window.scrollTo({{ top: 0, behavior: 'smooth' }});

  if (viewId === 'usersAdminView') {{
    loadAdminUsers();
    loadAdminVisitors();
  }} else if (viewId === 'terminalView') {{
    document.getElementById('cliInputField')?.focus();
  }}
}}

function handleUserBadgeClick() {{
  if (isUserAdmin) {{
    showView('usersAdminView');
  }} else {{
    showView('registerView');
  }}
}}

// ИНИЦИАЛИЗАЦИЯ ПОЛЬЗОВАТЕЛЯ
async function initUserProfile() {{
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

  try {{
    const res = await fetch('/api/user/profile', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgId }},
      body: JSON.stringify({{ tg_id: tgId, tg_username: tgUser, tg_name: tgName }})
    }});
    const data = await res.json();

    if (data.blocked) {{
      showView('blockedView');
      return;
    }}

    if (data.is_admin) {{
      isUserAdmin = true;
      currentSessionUser = data.nickname || 'Admin';
      document.getElementById('currentUserBadge').style.display = 'inline-flex';
      document.getElementById('userBadgeIcon').className = 'fa-solid fa-user-shield';
      document.getElementById('currentUsernameSpan').innerText = currentSessionUser;
      showView('catalogView');
    }} else if (data.registered) {{
      isUserAdmin = false;
      currentSessionUser = data.nickname;
      document.getElementById('currentUserBadge').style.display = 'inline-flex';
      document.getElementById('userBadgeIcon').className = 'fa-solid fa-user-check';
      document.getElementById('currentUsernameSpan').innerText = currentSessionUser;
      showView('catalogView');
    }} else {{
      isUserAdmin = false;
      document.getElementById('currentUserBadge').style.display = 'none';
      document.getElementById('regNicknameInput').value = data.suggested_nickname || '';
      showView('registerView');
    }}
  }} catch (e) {{
    showView('registerView');
  }}
}}

// РЕГИСТРАЦИЯ
async function doRegister() {{
  const nick = document.getElementById('regNicknameInput').value.trim();
  const statusMsg = document.getElementById('regStatusMsg');

  if (!nick || nick.length < 2) {{
    statusMsg.innerText = 'Пожалуйста, введите ваш позывной (минимум 2 символа)';
    statusMsg.style.display = 'block';
    return;
  }}

  let tgUser = '';
  let tgName = '';
  if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) {{
    tgUser = tg.initDataUnsafe.user.username || '';
    tgName = `${{tg.initDataUnsafe.user.first_name || ''}} ${{tg.initDataUnsafe.user.last_name || ''}}`.trim();
  }}

  try {{
    const res = await fetch('/api/user/profile', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
      body: JSON.stringify({{ tg_id: tgUserId, tg_username: tgUser, tg_name: tgName, nickname: nick }})
    }});
    const data = await res.json();
    if (data.ok) {{
      currentSessionUser = data.nickname || nick;
      document.getElementById('currentUserBadge').style.display = 'inline-flex';
      if (data.is_admin) {{
        isUserAdmin = true;
        document.getElementById('userBadgeIcon').className = 'fa-solid fa-user-shield';
        document.getElementById('currentUsernameSpan').innerText = currentSessionUser;
      }} else {{
        isUserAdmin = false;
        document.getElementById('userBadgeIcon').className = 'fa-solid fa-user-check';
        document.getElementById('currentUsernameSpan').innerText = currentSessionUser;
      }}
      showView('catalogView');
    }} else {{
      statusMsg.innerText = 'Ошибка: ' + (data.error || 'Попробуйте другой позывной');
      statusMsg.style.display = 'block';
    }}
  }} catch (e) {{
    statusMsg.innerText = 'Ошибка соединения: ' + e.message;
    statusMsg.style.display = 'block';
  }}
}}

function setFilter(cat, elem) {{
  currentCategory = cat;
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  if (elem) elem.classList.add('active');
  renderCatalog();
}}

function renderCatalog() {{
  const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();
  const container = document.getElementById('catalogContainer');
  if (!container) return;
  container.innerHTML = '';

  let totalShown = 0;

  FULL_CATALOG.forEach(group => {{
    if (currentCategory !== 'all' && group.id !== currentCategory) return;

    const filteredTools = group.tools.filter(t => {{
      if (!query) return true;
      const gStr = JSON.stringify(t.install_guide || {{}}).toLowerCase();
      const blob = (group.title + ' ' + t.name + ' ' + t.purpose + ' ' + (t.input||'') + ' ' + gStr).toLowerCase();
      return blob.includes(query);
    }});

    if (filteredTools.length === 0) return;
    totalShown += filteredTools.length;

    const groupWrap = document.createElement('div');
    groupWrap.innerHTML = `
      <div class="group-title">${{group.title}}</div>
      <div class="group-desc">${{group.desc}}</div>
    `;

    const grid = document.createElement('div');
    grid.className = 'cards-grid';

    filteredTools.forEach(tool => {{
      const card = document.createElement('div');
      card.className = 'card';
      card.onclick = () => openToolPage(tool.id);

      let badge = '<span class="badge badge-doc">CLI</span>';
      if (tool.web_runnable && tool.launch?.type === 'api') {{
        badge = '<span class="badge badge-api">⚡ SCANNER</span>';
      }} else if (tool.web_url && tool.launch?.type === 'url') {{
        badge = '<span class="badge badge-web">🌐 WEB</span>';
      }}

      card.innerHTML = `
        <div class="card-header">
          <div class="card-title">${{tool.name}}</div>
          ${{badge}}
        </div>
        <div class="card-purpose">${{tool.purpose}}</div>
        <div class="btn-group" onclick="event.stopPropagation()">
          <button class="btn btn-primary" onclick="openToolPage('${{tool.id}}')"><i class="fa-solid fa-crosshairs"></i> Запуск</button>
        </div>
      `;
      grid.appendChild(card);
    }});

    groupWrap.appendChild(grid);
    container.appendChild(groupWrap);
  }});

  if (totalShown === 0) {{
    container.innerHTML = '<div style="text-align:center; padding:24px; color:var(--text-muted); font-size:12px;">Ничего не найдено.</div>';
  }}
}}

// БЫСТРЫЙ ЗАПУСК С ГЛАВНОЙ СТРАНИЦЫ
function runMainQuickScan() {{
  const target = document.getElementById('mainQuickTargetInput').value.trim();
  if (!target) {{
    alert('Введите никнейм, GitHub логин, телефон или адрес кошелька');
    return;
  }}

  // Умный авто-роутинг по формату ввода
  if (target.startsWith('0x') || target.startsWith('T') && target.length === 34 || target.startsWith('bc1') || target.startsWith('1') && target.length >= 26) {{
    openToolPage('crypto_tracker');
    document.getElementById('tvTargetInput').value = target;
  }} else if (target.includes('github.com') || target.startsWith('gh:')) {{
    openToolPage('github_recon');
    document.getElementById('tvTargetInput').value = target.replace('gh:', '').replace('https://github.com/', '');
  }} else if (target.startsWith('+') || /^\\d{{10,15}}$/.test(target.replace(/[\\s\\-\\(\\)]/g, ''))) {{
    openToolPage('phoneinfoga_recon');
    document.getElementById('tvTargetInput').value = target;
  }} else if (target.includes('@') && target.includes('.')) {{
    openToolPage('holehe_osint');
    document.getElementById('tvTargetInput').value = target;
  }} else if (target.startsWith('@') || target.includes('_temp') || target.includes('_alt') || target.includes('_work')) {{
    openToolPage('sockpuppet_attribution');
    document.getElementById('tvTargetInput').value = target;
  }} else if (target.includes('.') && !target.includes(' ') && (target.endsWith('.com') || target.endsWith('.ru') || target.endsWith('.org') || target.endsWith('.io') || target.startsWith('http'))) {{
    openToolPage('subfinder');
    document.getElementById('tvTargetInput').value = target;
  }} else {{
    openToolPage('sherlock');
    document.getElementById('tvTargetInput').value = target;
  }}

  runCurrentToolScan();
}}

function openToolPage(toolId) {{
  let selected = null;
  for (let g of FULL_CATALOG) {{
    for (let t of g.tools) {{
      if (t.id === toolId) {{ selected = t; break; }}
    }}
  }}
  if (!selected) {{
    selected = {{
      id: 'sherlock',
      name: 'Sherlock Project Engine',
      purpose: 'Поиск открытых аккаунтов по 480+ официальным базам данных.',
      scan_type: 'username',
      input: 'username'
    }};
  }}

  activeTool = selected;
  document.getElementById('tvTitle').innerHTML = `<i class="fa-solid fa-cube" style="color:var(--primary);"></i> ${{selected.name}}`;
  document.getElementById('tvPurpose').innerText = selected.purpose;

  const btnGroup = document.getElementById('tvHeaderButtons');
  btnGroup.innerHTML = '';

  if (selected.web_url) {{
    btnGroup.innerHTML += `<button onclick="openExternalUrl('${{selected.web_url}}')" class="btn btn-primary"><i class="fa-solid fa-arrow-up-right-from-square"></i> Web</button>`;
  }}
  if (selected.repo) {{
    btnGroup.innerHTML += `<button onclick="openExternalUrl('${{selected.repo}}')" class="btn btn-secondary"><i class="fa-brands fa-github"></i> GitHub</button>`;
  }}

  const isPhotoTool = selected.id.includes('suncalc') || selected.id.includes('meta') || (selected.input||'').includes('photo');
  
  if (isPhotoTool) {{
    document.getElementById('tvPhotoUploaderBox').style.display = 'block';
    document.getElementById('tvTextInputRow').style.display = 'none';
  }} else {{
    document.getElementById('tvPhotoUploaderBox').style.display = 'none';
    document.getElementById('tvTextInputRow').style.display = 'flex';
  }}

  const input = document.getElementById('tvTargetInput');
  input.value = '';
  if (selected.scan_type === 'github' || selected.id === 'github_recon') {{
    input.placeholder = `GitHub логин (например: torvalds или sorberaa)`;
  }} else if (selected.scan_type === 'crypto' || selected.id === 'crypto_tracker') {{
    input.placeholder = `Адрес кошелька (BTC, ETH, USDT TRC20, SOL)`;
  }} else if (selected.scan_type === 'attribution' || selected.id === 'sockpuppet_attribution') {{
    input.placeholder = `Telegram юзернейм или ID вирта (например: @alex_temp)`;
  }} else if (selected.scan_type === 'telegram' || selected.id === 'tg_inspector') {{
    input.placeholder = `Telegram username или ID (например: durov)`;
  }} else if (selected.input === 'username' || selected.scan_type === 'username') {{
    input.placeholder = `Никнейм для Sherlock (например: wertag20)`;
  }} else if (selected.input === 'domain' || selected.scan_type === 'domain') {{
    input.placeholder = `Домен (например: google.com)`;
  }} else if (selected.input === 'email' || selected.scan_type === 'email') {{
    input.placeholder = `Email (например: user@mail.ru)`;
  }} else if (selected.input === 'ip' || selected.scan_type === 'ip') {{
    input.placeholder = `IP-адрес (например: 8.8.8.8)`;
  }} else if (selected.input === 'phone' || selected.scan_type === 'phone') {{
    input.placeholder = `Номер телефона (например: +79991234567)`;
  }} else {{
    input.placeholder = `Цель для анализа`;
  }}

  document.getElementById('tvOutputBox').style.display = 'none';
  document.getElementById('tvOutputBox').innerHTML = '';

  const cmdsDiv = document.getElementById('tvInstallCommands');
  cmdsDiv.innerHTML = '';
  const guide = selected.install_guide || {{}};

  if (guide.git) cmdsDiv.appendChild(createCmdBox('1. Клонирование Git', guide.git));
  if (guide.pip_or_pkg) cmdsDiv.appendChild(createCmdBox('2. Установка зависимостей', guide.pip_or_pkg));
  if (guide.docker) cmdsDiv.appendChild(createCmdBox('3. Docker запуск', guide.docker));
  if (guide.usage) cmdsDiv.appendChild(createCmdBox('4. Пример запуска', guide.usage));

  showView('toolView');
}}

// ЗАПУСК СКАНИРОВАНИЯ В ТЕРМИНАЛЕ
async function runCurrentToolScan() {{
  if (!activeTool) return;
  const rawTarget = document.getElementById('tvTargetInput').value.trim();
  const loader = document.getElementById('tvLoader');
  const loaderText = document.getElementById('tvLoaderText');
  const outBox = document.getElementById('tvOutputBox');

  if (!rawTarget) {{
    alert('Введите цель для анализа');
    return;
  }}

  loader.style.display = 'block';
  outBox.style.display = 'none';

  let endpoint = '/api/scan/username';
  let cleanTarget = rawTarget;

  if (activeTool.scan_type === 'github' || activeTool.id === 'github_recon') {{
    endpoint = '/api/scan/github';
    cleanTarget = rawTarget.replace(/^@+/, '').replace('https://github.com/', '');
    loaderText.innerText = 'Поиск скрытых email в коммитах и анализ профиля GitHub...';
  }} else if (activeTool.scan_type === 'crypto' || activeTool.id === 'crypto_tracker') {{
    endpoint = '/api/scan/crypto';
    cleanTarget = rawTarget;
    loaderText.innerText = 'Определение блокчейна, эксплореров и AML статуса...';
  }} else if (activeTool.scan_type === 'attribution' || activeTool.id === 'sockpuppet_attribution') {{
    endpoint = '/api/scan/attribution';
    cleanTarget = rawTarget.replace(/^@+/, '');
    loaderText.innerText = 'Корреляция мутаций псевдонимов и поиск основы...';
  }} else if (activeTool.scan_type === 'telegram' || activeTool.id === 'tg_inspector') {{
    endpoint = '/api/scan/telegram';
    cleanTarget = rawTarget.replace(/^@+/, '');
    loaderText.innerText = 'Опрос Telegram Gateway и извлечение профиля...';
  }} else if (activeTool.scan_type === 'domain' || activeTool.input === 'domain' || activeTool.id === 'subfinder' || activeTool.id === 'webcheck' || activeTool.id === 'finalrecon') {{
    endpoint = '/api/scan/domain';
    cleanTarget = rawTarget.replace(/^https?:\\/\\//, '').split('/')[0];
    loaderText.innerText = 'Разведка DNS, SSL, заголовков и поддоменов...';
  }} else if (activeTool.scan_type === 'email' || activeTool.input === 'email' || activeTool.id === 'ghunt' || activeTool.id === 'holehe_osint') {{
    endpoint = '/api/scan/email';
    loaderText.innerText = 'Проверка MX серверов, Gravatar и сервисов...';
  }} else if (activeTool.scan_type === 'phone' || activeTool.id === 'phoneinfoga_recon' || (rawTarget.startsWith('+') && rawTarget.length > 7)) {{
    endpoint = '/api/scan/phone';
    cleanTarget = rawTarget;
    loaderText.innerText = 'Определение оператора, региона и генерация дорков...';
  }} else if (activeTool.scan_type === 'ip' || activeTool.input === 'ip') {{
    endpoint = '/api/scan/ip';
    loaderText.innerText = 'Определение геопозиции IP и провайдера...';
  }} else {{
    endpoint = '/api/scan/username';
    cleanTarget = rawTarget.replace(/^@+/, '');
    loaderText.innerText = 'Опрос официальных баз Sherlock Project...';
  }}

  try {{
    const res = await fetch(endpoint, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
      body: JSON.stringify({{ target: cleanTarget, caller: currentSessionUser || 'user' }})
    }});
    const data = await res.json();
    loader.style.display = 'none';
    outBox.style.display = 'block';

    if (data.type === 'attribution') {{
      renderAttributionOutput(data, outBox);
    }} else {{
      renderToolSpecificOutput(data, cleanTarget);
    }}
  }} catch (err) {{
    loader.style.display = 'none';
    outBox.style.display = 'block';
    outBox.innerHTML = `<div style="color:var(--danger); font-size:12px;">❌ Ошибка: ${{err.message}}</div>`;
  }}
}}

// ВЫВОД РЕЗУЛЬТАТОВ РАЗВЕДКИ (GITHUB, CRYPTO, SHERLOCK, PHONE, DOMAIN, IP)
function renderToolSpecificOutput(data, target) {{
  const outBox = document.getElementById('tvOutputBox');
  const nowStr = new Date().toISOString().replace('T', ' ').substr(11, 8);
  let html = '';

  // 1. GITHUB DEEP RECON
  if (data.type === 'github') {{
    const emails = data.emails_discovered || [];
    const repos = data.recent_repos || [];
    let logLines = `[${{nowStr}}] [GH-PROBE] RESOLVING USER: ${{data.username}}
[${{nowStr}}] [+] REAL NAME: "${{data.name}}"
[${{nowStr}}] [+] REPOSITORIES: ${{data.public_repos_count}} | FOLLOWERS: ${{data.followers}}
[${{nowStr}}] [COMMITS] EXTRACTING UNMASKED EMAILS: ${{emails.length > 0 ? emails.join(', ') : 'NO PUBLIC EMAILS'}}
[${{nowStr}}] [✓] GITHUB RECON COMPLETED.`;

    html += `
      <div class="hacker-terminal">
        <div class="term-topbar">
          <div class="term-dots"><span class="term-dot term-dot-green"></span></div>
          <span>GITHUB-INTEL@STATION:~# ./gh-dork ${{data.username}}</span>
        </div>
        <div class="term-log-content">${{logLines}}</div>
      </div>

      <div class="custom-card" style="border-color:var(--cyan);">
        <div class="custom-card-title" style="color:var(--cyan); display:flex; justify-content:space-between;">
          <span><i class="fa-brands fa-github"></i> Профиль GitHub: ${{data.username}}</span>
          <button onclick="openExternalUrl('${{data.profile_url}}')" class="btn btn-primary" style="padding:2px 8px; font-size:10px;">Открыть GitHub</button>
        </div>
        <div style="display:flex; gap:12px; align-items:center; margin-bottom:12px;">
          <img src="${{data.avatar_url}}" style="width:54px; height:54px; border-radius:50%; border:2px solid var(--cyan);" alt="Avatar">
          <div>
            <div style="font-weight:800; font-size:15px; color:#fff;">${{data.name}}</div>
            <div style="font-size:11px; color:var(--text-muted);">${{data.bio}}</div>
            <div style="font-size:10px; color:var(--cyan); margin-top:2px;">📍 ${{data.location}} · 🏢 ${{data.company}}</div>
          </div>
        </div>

        <div class="custom-grid">
          <div class="custom-item" style="grid-column: span 2;">
            <div class="custom-label">📧 Извлеченные Email (из коммитов)</div>
            <div class="custom-val" style="color:var(--primary); font-family:monospace; font-size:13px;">
              ${{emails.length > 0 ? emails.map(e => `<div>✉️ <b>${{e}}</b></div>`).join('') : '<span style="color:var(--text-muted);">Публичные email скрыты в последних коммитах</span>'}}
            </div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🔑 Публичные SSH Ключи</div>
            <div class="custom-val"><button onclick="openExternalUrl('${{data.keys_url}}')" class="btn btn-secondary" style="padding:2px 6px; font-size:9px;">Посмотреть .keys</button></div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🛡️ GPG Подписи</div>
            <div class="custom-val"><button onclick="openExternalUrl('${{data.gpg_url}}')" class="btn btn-secondary" style="padding:2px 6px; font-size:9px;">Посмотреть .gpg</button></div>
          </div>
        </div>
      </div>
    `;

    if (repos.length > 0) {{
      html += `
        <div style="font-size:12px; font-weight:800; color:#fff; margin-top:10px; margin-bottom:6px;">
          Активные репозитории (${{repos.length}}):
        </div>
        <div class="profiles-grid">
      `;
      repos.forEach(r => {{
        html += `
          <div class="profile-card">
            <div>
              <div class="profile-name" style="font-size:11px;">${{r.name}}</div>
              <div style="font-size:9px; color:var(--cyan);">⭐ ${{r.stars}} · ${{r.language}}</div>
            </div>
            <button onclick="openExternalUrl('${{r.url}}')" class="btn btn-secondary" style="padding:3px 7px; font-size:10px;">Код</button>
          </div>
        `;
      }});
      html += '</div>';
    }}

  // 2. CRYPTO & BLOCKCHAIN WALLET
  }} else if (data.type === 'crypto') {{
    let logLines = `[${{nowStr}}] [CRYPTO-PROBE] RESOLVING ADDRESS: ${{data.address}}
[${{nowStr}}] [+] DETECTED NETWORK: ${{data.network}} (${{data.symbol}})
[${{nowStr}}] [EXPLORERS] GENERATING REALTIME LEDGER LINKS...
[${{nowStr}}] [✓] BLOCKCHAIN INTEL READY.`;

    html += `
      <div class="hacker-terminal">
        <div class="term-topbar">
          <div class="term-dots"><span class="term-dot term-dot-green"></span></div>
          <span>CRYPTO-INTEL@STATION:~# ./trace ${{data.address.substr(0, 10)}}...</span>
        </div>
        <div class="term-log-content">${{logLines}}</div>
      </div>

      <div class="custom-card" style="border-color:var(--primary);">
        <div class="custom-card-title"><i class="fa-solid fa-wallet" style="color:var(--primary);"></i> Анализ блокчейн-кошелька</div>
        <div class="custom-grid">
          <div class="custom-item" style="grid-column: span 2;">
            <div class="custom-label">🪙 Адрес кошелька</div>
            <div class="custom-val" style="color:var(--primary); font-family:monospace; font-size:12px;">${{data.address}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🌐 Сеть блокчейна</div>
            <div class="custom-val">${{data.network}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🛡️ AML / Чистота</div>
            <div class="custom-val"><button onclick="openExternalUrl('${{data.aml_check_url}}')" class="btn btn-secondary" style="padding:2px 6px; font-size:9px;">AML Check</button></div>
          </div>
        </div>
      </div>

      <div class="custom-card">
        <div class="custom-card-title"><i class="fa-solid fa-magnifying-glass" style="color:var(--cyan);"></i> Блокчейн-эксплореры (Баланс и транзакции)</div>
        <div class="btn-group">
          ${{data.explorers.map(ex => `<button onclick="openExternalUrl('${{ex.url}}')" class="btn btn-primary" style="font-size:10px;"><i class="fa-solid fa-arrow-up-right-from-square"></i> ${{ex.name}}</button>`).join('')}}
        </div>
      </div>
    `;

  // 3. SHERLOCK USERNAME
  }} else if (data.type === 'username') {{
    const pdata = data.probable_data || {{}};
    const profiles = data.profiles || [];
    
    let checkedLines = profiles.map(p => `[${{nowStr}}] [+] [MATCH] ${{p.platform.padEnd(14)}} (${{p.category}}) -> ${{p.url}}`).join('\\n');
    let cliLog = `[${{nowStr}}] [CORE] INITIATING SHERLOCK PROJECT ENGINE
[${{nowStr}}] [TARGET] RESOLVING IDENTIFIER: "${{data.username}}"
[${{nowStr}}] [PROBE] CROSS-SEARCHING ALL OFFICIAL PLATFORMS...
${{checkedLines || `[${{nowStr}}] [-] NO DIRECT MATCHES FOUND`}}
[${{nowStr}}] [✓] COMPLETED: ${{data.found_count}} OF ${{data.total_checked}} NODES VERIFIED.`;

    html += `
      <div class="hacker-terminal">
        <div class="term-topbar">
          <div class="term-dots"><span class="term-dot term-dot-green"></span></div>
          <span>SHERLOCK@STATION:~# ./sherlock ${{data.username}}</span>
          <span style="font-size:10px; color:var(--cyan);"><i class="fa-solid fa-circle" style="font-size:7px; color:var(--primary);"></i> LIVE</span>
        </div>
        <div class="term-log-content">${{cliLog}}</div>
      </div>

      <div class="custom-card">
        <div class="custom-card-title">
          <i class="fa-solid fa-crosshairs" style="color:var(--primary);"></i> Сводная дедукция по цели "${{target}}"
        </div>
        <div class="custom-grid">
          <div class="custom-item">
            <div class="custom-label">👤 Вероятное имя</div>
            <div class="custom-val">${{pdata.name || target}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🏙️ Локация</div>
            <div class="custom-val">${{pdata.location || 'По часовому поясу'}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🎂 Возраст</div>
            <div class="custom-val">${{pdata.age_estimate || '20–30 лет'}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🔗 Подтвержденных баз</div>
            <div class="custom-val" style="color:var(--primary); font-weight:800;">${{data.found_count}} из ${{data.total_checked}}</div>
          </div>
        </div>
      </div>
    `;

    if (profiles.length > 0) {{
      window._lastProfiles = profiles;
      const categories = ['Все', ...new Set(profiles.map(p => p.category))];
      let catButtons = categories.map((c, i) => `
        <button class="chip ${{i === 0 ? 'active' : ''}}" style="padding:4px 9px; font-size:10px;" onclick="filterResultProfiles('${{c}}', this)">${{c}} (${{c === 'Все' ? profiles.length : profiles.filter(p => p.category === c).length}})</button>
      `).join('');

      html += `
        <div style="font-size:12px; font-weight:800; color:#fff; margin-top:10px; margin-bottom:6px;">
          Подтвержденные профили (${{data.found_count}}):
        </div>
        <div class="filter-chips" style="margin-bottom:8px;">${{catButtons}}</div>
        <div class="profiles-grid" id="scanProfilesGrid">
      `;
      profiles.forEach(p => {{
        html += `
          <div class="profile-card" data-cat="${{p.category}}">
            <div class="profile-left">
              <i class="fa-solid fa-arrow-up-right-from-square profile-icon"></i>
              <div>
                <div class="profile-name">${{p.platform}}</div>
                <span class="profile-tag">✅ ${{p.category}}</span>
              </div>
            </div>
            <button onclick="openExternalUrl('${{p.url}}')" class="btn btn-secondary" style="padding:4px 8px; font-size:10px;">🔗 Открыть</button>
          </div>
        `;
      }});
      html += '</div>';
    }} else {{
      html += `
        <div class="info-banner" style="text-align:center; padding:14px;">
          ❌ Прямых открытых совпадений по никнейму <b>${{target}}</b> не найдено.
        </div>
      `;
    }}

  // 4. PHONE RECON
  }} else if (data.type === 'phone') {{
    const tz = (data.timezones || []).join(', ') || 'UTC';
    const m = data.messengers || {{}};
    const d = data.dorks || {{}};

    let cliLog = `[${{nowStr}}] [PHONE] PARSING E.164: ${{data.e164}} (${{data.national}})
[${{nowStr}}] [GEO] REGION: ${{data.country}} | CARRIER: ${{data.carrier}}
[${{nowStr}}] [LINE] TYPE: ${{data.line_type}} | TZ: ${{tz}}
[${{nowStr}}] [MESSENGERS] CHECKING WA / TG / VIBER / SKYPE...
[${{nowStr}}] [✓] PHONE RECON COMPLETED.`;

    html += `
      <div class="hacker-terminal">
        <div class="term-topbar">
          <div class="term-dots"><span class="term-dot term-dot-green"></span></div>
          <span>PHONE-RECON@STATION:~# ./phoneinfoga scan -n ${{data.e164}}</span>
        </div>
        <div class="term-log-content">${{cliLog}}</div>
      </div>

      <div class="custom-card">
        <div class="custom-card-title"><i class="fa-solid fa-phone" style="color:var(--primary);"></i> Данные оператора и региона</div>
        <div class="custom-grid">
          <div class="custom-item">
            <div class="custom-label">📞 Номер телефона</div>
            <div class="custom-val" style="color:var(--primary); font-size:14px;">${{data.e164}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🏢 Оператор связи</div>
            <div class="custom-val">${{data.carrier}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🌍 Страна и Регион</div>
            <div class="custom-val">${{data.country}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🏷️ Тип линии</div>
            <div class="custom-val" style="color:${{data.is_voip_suspect ? 'var(--danger)' : '#fff'}};">
              ${{data.is_voip_suspect ? '⚠️ VoIP / Виртуальный номер' : '📱 Мобильный / Физический'}}
            </div>
          </div>
        </div>
      </div>

      <div class="custom-card">
        <div class="custom-card-title"><i class="fa-solid fa-comments" style="color:var(--cyan);"></i> Проверка в мессенджерах</div>
        <div class="btn-group">
          ${{m.whatsapp ? `<button onclick="openExternalUrl('${{m.whatsapp}}')" class="btn btn-primary" style="background:#25D366; color:#000;"><i class="fa-brands fa-whatsapp"></i> WhatsApp</button>` : ''}}
          ${{m.telegram ? `<button onclick="openExternalUrl('${{m.telegram}}')" class="btn btn-primary" style="background:#229ED9; color:#fff;"><i class="fa-brands fa-telegram"></i> Telegram</button>` : ''}}
          ${{m.viber ? `<button onclick="openExternalUrl('${{m.viber}}')" class="btn btn-purple"><i class="fa-brands fa-viber"></i> Viber</button>` : ''}}
        </div>
      </div>
    `;

  // 5. DOMAIN & SUBFINDER
  }} else if (data.type === 'domain') {{
    const d = data.data || {{}};
    const ssl = d.ssl || {{}};
    const hdrs = d.headers || {{}};
    const subs = d.subdomains_found || [];

    html += `
      <div class="custom-card">
        <div class="custom-card-title"><i class="fa-solid fa-network-wired" style="color:var(--cyan);"></i> Инфраструктура домена</div>
        <div class="custom-grid">
          <div class="custom-item">
            <div class="custom-label">🌐 IP Адрес(а)</div>
            <div class="custom-val">${{d.ip_addresses?.join(', ') || 'Не определен'}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🔒 SSL Сертификат</div>
            <div class="custom-val">${{ssl.valid ? '✅ ' + (ssl.issuer || 'Действителен') : '❌ Отсутствует'}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🖥️ Серверное ПО</div>
            <div class="custom-val">${{hdrs.Server || 'Скрыто'}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🛡️ HSTS Защита</div>
            <div class="custom-val">${{hdrs.HSTS !== 'Отсутствует' ? 'Включена' : 'Отключена'}}</div>
          </div>
        </div>
      </div>
    `;

    if (subs.length > 0) {{
      html += `
        <div style="font-size:12px; font-weight:800; color:#fff; margin-top:10px; margin-bottom:6px;">
          Найденные субдомены (${{subs.length}}):
        </div>
        <div class="profiles-grid">
      `;
      subs.forEach(s => {{
        html += `
          <div class="profile-card">
            <div>
              <div class="profile-name" style="font-size:11px;">${{s.subdomain}}</div>
              <div style="font-size:9px; color:var(--cyan); font-family:monospace;">${{s.ip}}</div>
            </div>
            <button onclick="openExternalUrl('https://${{s.subdomain}}')" class="btn btn-secondary" style="padding:3px 7px; font-size:10px;">🔗 Открыть</button>
          </div>
        `;
      }});
      html += '</div>';
    }}

  // 6. IP GEOINT
  }} else if (data.type === 'ip') {{
    const d = data.data || {{}};
    html += `
      <div class="custom-card">
        <div class="custom-card-title"><i class="fa-solid fa-earth-americas" style="color:var(--cyan);"></i> Геолокация и Провайдер IP</div>
        <div class="custom-grid">
          <div class="custom-item">
            <div class="custom-label">🌍 Страна и Город</div>
            <div class="custom-val">${{d.country || '—'}}, ${{d.city || '—'}} (${{d.regionName || ''}})</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🏢 Провайдер (ISP)</div>
            <div class="custom-val">${{d.isp || '—'}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🔢 Автономная система (AS)</div>
            <div class="custom-val">${{d.as || '—'}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🕒 Часовой пояс</div>
            <div class="custom-val">${{d.timezone || '—'}}</div>
          </div>
        </div>
      </div>
    `;
  }}

  outBox.innerHTML = html;
}}

// ИНТЕРАКТИВНЫЙ CLI ТЕРМИНАЛ ОБРАБОТЧИК
function handleCliKeyDown(event) {{
  if (event.key === 'Enter') {{
    executeCliCommand();
  }} else if (event.key === 'ArrowUp') {{
    if (cliHistory.length > 0 && cliHistoryIndex > 0) {{
      cliHistoryIndex--;
      document.getElementById('cliInputField').value = cliHistory[cliHistoryIndex];
    }}
  }} else if (event.key === 'ArrowDown') {{
    if (cliHistoryIndex < cliHistory.length - 1) {{
      cliHistoryIndex++;
      document.getElementById('cliInputField').value = cliHistory[cliHistoryIndex];
    }} else {{
      cliHistoryIndex = cliHistory.length;
      document.getElementById('cliInputField').value = '';
    }}
  }}
}}

async function executeCliCommand() {{
  const inputEl = document.getElementById('cliInputField');
  const outputEl = document.getElementById('cliOutputContent');
  const cmdRaw = inputEl.value.trim();
  if (!cmdRaw) return;

  cliHistory.push(cmdRaw);
  cliHistoryIndex = cliHistory.length;
  inputEl.value = '';

  outputEl.innerText += `\\nroot@cyberhub:~# ${{cmdRaw}}\\n`;

  const parts = cmdRaw.split(/\\s+/);
  const cmd = parts[0].toLowerCase();
  const arg = parts.slice(1).join(' ');

  if (cmd === 'help') {{
    outputEl.innerText += `AVAILABLE COMMANDS:
  help                     - Show this command reference
  sherlock <username>      - Search 480+ databases for username
  github <username>        - Extract commit emails & repos for GitHub user
  crypto <wallet_address>  - Identify network, balance & ledger links for wallet
  phone <phone_number>     - Lookup carrier, region and VoIP status
  ip <ip_address>          - Lookup GeoIP, ISP and ASN
  attr <tg_username>       - Sockpuppet attribution & root handle correlation
  matrix                   - Toggle Matrix Digital Rain background FX
  whoami / id              - Display current user callsign & Telegram ID
  clear                    - Clear terminal screen
  catalog                  - Return to Web Catalog view
`;
  }} else if (cmd === 'clear') {{
    outputEl.innerText = 'OSINT CYBER HUB · Terminal Cleared\\n';
  }} else if (cmd === 'matrix') {{
    toggleMatrix();
    outputEl.innerText += `[+] Matrix Rain FX toggled: ${{matrixActive ? 'ENABLED' : 'DISABLED'}}\\n`;
  }} else if (cmd === 'whoami' || cmd === 'id') {{
    outputEl.innerText += `[+] Callsign: ${{currentSessionUser || 'Guest'}} | TG ID: ${{tgUserId || 'Browser'}} | Admin: ${{isUserAdmin ? 'YES' : 'NO'}}\\n`;
  }} else if (cmd === 'catalog' || cmd === 'exit') {{
    showView('catalogView');
  }} else if (cmd === 'github' && arg) {{
    outputEl.innerText += `[*] Probing GitHub user: ${{arg}}...\\n`;
    try {{
      const res = await fetch('/api/scan/github', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
        body: JSON.stringify({{ target: arg, caller: currentSessionUser }})
      }});
      const data = await res.json();
      outputEl.innerText += `[+] Name: ${{data.name}} | Location: ${{data.location}} | Repos: ${{data.public_repos_count}}\\n`;
      if (data.emails_discovered && data.emails_discovered.length > 0) {{
        outputEl.innerText += `[!] DISCOVERED EMAILS (FROM COMMITS): ${{data.emails_discovered.join(', ')}}\\n`;
      }} else {{
        outputEl.innerText += `[-] No public commit emails discovered.\\n`;
      }}
    }} catch (e) {{
      outputEl.innerText += `[-] Error: ${{e.message}}\\n`;
    }}
  }} else if (cmd === 'crypto' && arg) {{
    outputEl.innerText += `[*] Analyzing crypto wallet: ${{arg}}...\\n`;
    try {{
      const res = await fetch('/api/scan/crypto', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
        body: JSON.stringify({{ target: arg, caller: currentSessionUser }})
      }});
      const data = await res.json();
      outputEl.innerText += `[+] Network: ${{data.network}} (${{data.symbol}})\\n[+] Explorers: ${{data.explorers.map(e => e.name).join(', ')}}\\n`;
    }} catch (e) {{
      outputEl.innerText += `[-] Error: ${{e.message}}\\n`;
    }}
  }} else if ((cmd === 'sherlock' || cmd === 'scan' || cmd === 'user') && arg) {{
    outputEl.innerText += `[*] Querying Sherlock Project database for: ${{arg}}...\\n`;
    try {{
      const res = await fetch('/api/scan/username', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
        body: JSON.stringify({{ target: arg, caller: currentSessionUser }})
      }});
      const data = await res.json();
      outputEl.innerText += `[+] Matches found: ${{data.found_count}} of ${{data.total_checked}} platforms.\\n`;
      (data.profiles || []).slice(0, 10).forEach(p => {{
        outputEl.innerText += `  • [${{p.platform}}] -> ${{p.url}}\\n`;
      }});
      if ((data.profiles || []).length > 10) outputEl.innerText += `  ... and ${{data.profiles.length - 10}} more.\\n`;
    }} catch (e) {{
      outputEl.innerText += `[-] Error: ${{e.message}}\\n`;
    }}
  }} else if (cmd === 'phone' && arg) {{
    outputEl.innerText += `[*] Probing phone: ${{arg}}...\\n`;
    try {{
      const res = await fetch('/api/scan/phone', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
        body: JSON.stringify({{ target: arg, caller: currentSessionUser }})
      }});
      const data = await res.json();
      outputEl.innerText += `[+] Number: ${{data.e164}} | Region: ${{data.country}} | Carrier: ${{data.carrier}} | Line: ${{data.line_type}}\\n`;
    }} catch (e) {{
      outputEl.innerText += `[-] Error: ${{e.message}}\\n`;
    }}
  }} else if (cmd === 'ip' && arg) {{
    outputEl.innerText += `[*] Geolocation lookup for: ${{arg}}...\\n`;
    try {{
      const res = await fetch('/api/scan/ip', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
        body: JSON.stringify({{ target: arg, caller: currentSessionUser }})
      }});
      const data = await res.json();
      const d = data.data || {{}};
      outputEl.innerText += `[+] Country: ${{d.country}}, City: ${{d.city}} | ISP: ${{d.isp}} | AS: ${{d.as}}\\n`;
    }} catch (e) {{
      outputEl.innerText += `[-] Error: ${{e.message}}\\n`;
    }}
  }} else {{
    outputEl.innerText += `[-] Unknown command: '${{cmd}}'. Type 'help' for command list.\\n`;
  }}

  outputEl.scrollTop = outputEl.scrollHeight;
}}

// ОБРАБОТКА ФОТО
async function processDirectPhoto(input) {{
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];
  const preview = document.getElementById('directPhotoPreview');
  const reader = new FileReader();
  reader.onload = async function(e) {{
    preview.src = e.target.result;
    preview.style.display = 'block';

    const loader = document.getElementById('photoLoader');
    const outBox = document.getElementById('photoResultBox');
    loader.style.display = 'block';
    outBox.innerHTML = '';

    try {{
      const res = await fetch('/api/scan/photo', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
        body: JSON.stringify({{ image_base64: e.target.result }})
      }});
      const data = await res.json();
      loader.style.display = 'none';
      renderPhotoSpecificCard(data, outBox);
    }} catch (err) {{
      loader.style.display = 'none';
      outBox.innerHTML = `<div style="color:var(--danger); font-size:12px;">❌ Ошибка: ${{err.message}}</div>`;
    }}
  }};
  reader.readAsDataURL(file);
}}

function renderPhotoSpecificCard(data, container) {{
  const exif = data.exif || {{}};
  let hasGps = !!exif.gps;
  let hasCamera = !!(exif.camera_make || exif.camera_model);
  let hasDate = !!exif.date_time;

  let html = '';
  if (hasCamera || hasDate || hasGps) {{
    html += `
      <div class="custom-card">
        <div class="custom-card-title"><i class="fa-solid fa-camera" style="color:var(--cyan);"></i> Метаданные снимка (EXIF)</div>
        <div class="custom-grid">
          <div class="custom-item">
            <div class="custom-label">📷 Камера</div>
            <div class="custom-val">${{exif.camera_make || ''}} ${{exif.camera_model || '—'}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🕒 Дата съемки</div>
            <div class="custom-val">${{exif.date_time || 'Скрыта'}}</div>
          </div>
          <div class="custom-item" style="grid-column: span 2;">
            <div class="custom-label">📍 Координаты GPS</div>
            <div class="custom-val">
              ${{hasGps ? `
                <span style="color:var(--primary);">📍 ${{exif.gps.latitude}}, ${{exif.gps.longitude}}</span>
                <button onclick="openExternalUrl('${{exif.google_maps_url}}')" class="btn btn-primary" style="padding:2px 7px; font-size:9px; margin-left:6px;">Google Maps</button>
              ` : '<span style="color:var(--text-muted);">Метки GPS отсутствуют</span>'}}
            </div>
          </div>
        </div>
      </div>
    `;
  }} else {{
    html += `
      <div class="info-banner">
        <b>ℹ️ Метаданные (EXIF) очищены:</b> В этом снимке отсутствуют теги камеры. Соцсети удаляют EXIF при сжатии.
      </div>
    `;
  }}

  html += `
    <div style="margin-bottom:12px;">
      <div style="font-size:11px; font-weight:700; color:var(--cyan); margin-bottom:6px; text-transform:uppercase;">
        🔍 Обратный поиск оригинала в поисковиках:
      </div>
      <div class="btn-group">
        <button onclick="openExternalUrl('https://yandex.ru/images/search?rpt=imageview')" class="btn btn-secondary"><i class="fa-solid fa-arrow-up-right-from-square"></i> Яндекс</button>
        <button onclick="openExternalUrl('https://lens.google.com/')" class="btn btn-secondary"><i class="fa-solid fa-arrow-up-right-from-square"></i> Google Lens</button>
      </div>
    </div>
  `;
  container.innerHTML = html;
}}

// АТРИБУЦИЯ ВИРТОВ
async function runAttributionScanDirect() {{
  const target = document.getElementById('attrTargetInput').value.trim();
  const text_sample = document.getElementById('attrTextSample').value.trim();
  const loader = document.getElementById('attrLoader');
  const outBox = document.getElementById('attrResultBox');

  if (!target) {{
    alert('Введите юзернейм или ID вирта');
    return;
  }}

  loader.style.display = 'block';
  outBox.innerHTML = '';

  try {{
    const res = await fetch('/api/scan/attribution', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
      body: JSON.stringify({{ target: target.replace(/^@+/, ''), text_sample, caller: currentSessionUser }})
    }});
    const data = await res.json();
    loader.style.display = 'none';
    renderAttributionOutput(data, outBox);
  }} catch (err) {{
    loader.style.display = 'none';
    outBox.innerHTML = `<div style="color:var(--danger); font-size:12px;">❌ Ошибка: ${{err.message}}</div>`;
  }}
}}

function renderAttributionOutput(data, container) {{
  const target = data.target || '';
  const root = data.root_handle || '';
  const nowStr = new Date().toISOString().replace('T', ' ').substr(11, 8);
  const mutations = data.candidate_mutations || [];
  const idAge = data.id_age_estimate || {{}};

  let logLines = `[${{nowStr}}] [ATTR] ANALYZING TARGET ACCOUNT: @${{target}}
[${{nowStr}}] [ID-PROBE] ESTIMATED CREATION: ${{idAge.year || '2023–2024'}} (${{idAge.note || 'Вирт/Купленный'}})
[${{nowStr}}] [MUTATION] GENERATED ROOT CANDIDATES: ${{mutations.join(', ')}}
[${{nowStr}}] [SYNTHESIS] CORRELATING DIGITAL FOOTPRINTS...`;

  let html = `
    <div class="hacker-terminal">
      <div class="term-topbar">
        <div class="term-dots"><span class="term-dot term-dot-green"></span></div>
        <span>ATTRIBUTION@ENGINE:~# ./attr @${{target}}</span>
      </div>
      <div class="term-log-content">${{logLines}}</div>
    </div>

    <div class="custom-card" style="border-color:var(--purple);">
      <div class="custom-card-title" style="color:var(--purple);">
        <i class="fa-solid fa-user-secret"></i> Результаты детектора виртов
      </div>
      <div class="custom-grid">
        <div class="custom-item">
          <div class="custom-label">🎯 Исходный аккаунт</div>
          <div class="custom-val">@${{target}}</div>
        </div>
        <div class="custom-item">
          <div class="custom-label">🔍 Вероятная основа (Корень)</div>
          <div class="custom-val" style="color:var(--primary); font-size:13px;">${{root ? '@' + root : 'Прямой корень скрыт'}}</div>
        </div>
        <div class="custom-item">
          <div class="custom-label">📅 Возраст Telegram ID</div>
          <div class="custom-val">${{idAge.year || 'Не определен'}}</div>
        </div>
        <div class="custom-item">
          <div class="custom-label">🏷️ Вердикт профиля</div>
          <div class="custom-val" style="color:${{data.is_sockpuppet_suspect ? 'var(--danger)' : 'var(--primary)'}};">
            ${{data.is_sockpuppet_suspect ? '⚠️ Подозрение на вирт' : '✅ Обычный аккаунт'}}
          </div>
        </div>
      </div>
    </div>
  `;

  if (mutations.length > 0) {{
    html += `
      <div style="font-size:12px; font-weight:800; color:#fff; margin-top:10px; margin-bottom:6px;">
        🔗 Связанные профили вероятного владельца в соцсетях:
      </div>
      <div class="profiles-grid">
    `;
    mutations.forEach(m => {{
      html += `
        <div class="profile-card">
          <div class="profile-left">
            <i class="fa-solid fa-link profile-icon" style="color:var(--purple);"></i>
            <div>
              <div class="profile-name">@${{m}}</div>
              <span class="profile-tag">Кандидат в основу</span>
            </div>
          </div>
          <button onclick="openExternalUrl('https://t.me/${{m}}')" class="btn btn-secondary" style="padding:3px 7px; font-size:10px;">Проверить TG</button>
        </div>
      `;
    }});
    html += '</div>';
  }}

  container.innerHTML = html;
}}

// АДМИН-ФУНКЦИИ
function toggleAddUserModal() {{
  const box = document.getElementById('addUserFormBox');
  box.style.display = box.style.display === 'none' ? 'block' : 'none';
}}

async function loadAdminUsers() {{
  if (!isUserAdmin) return;
  const tbody = document.getElementById('usersTableBody');
  tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:8px;">Загрузка...</td></tr>';

  try {{
    const res = await fetch('/api/admin/users', {{ headers: {{ 'X-Telegram-User-Id': tgUserId }} }});
    const data = await res.json();
    const users = data.users || [];

    tbody.innerHTML = '';
    users.forEach(u => {{
      const tr = document.createElement('tr');
      const roleBadge = u.role === 'admin' ? '<span class="badge badge-api">ADMIN</span>' : '<span class="badge badge-doc">USER</span>';
      const statusTxt = u.status === 'active' ? '<span style="color:var(--primary); font-weight:700;">🟢 АКТИВЕН</span>' : '<span style="color:var(--danger); font-weight:700;">🔴 БЛОК</span>';
      const tgInfo = u.tg_username ? `@${{u.tg_username}}` : (u.tg_id ? `ID:${{u.tg_id}}` : '—');
      
      tr.innerHTML = `
        <td><b>${{u.nickname || u.username}}</b></td>
        <td style="font-size:10px; color:var(--cyan);">${{tgInfo}}</td>
        <td style="font-family:monospace; font-size:10px; color:#38ef7d;">${{u.last_ip || '—'}}</td>
        <td>${{statusTxt}}</td>
        <td><code>${{u.total_scans}}</code></td>
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
    tbody.innerHTML = '<tr><td colspan="6" style="color:var(--danger); text-align:center;">Ошибка загрузки</td></tr>';
  }}
}}

async function submitCreateUser() {{
  if (!isUserAdmin) return;
  const username = document.getElementById('newUsername').value.trim();
  const password = document.getElementById('newPassword').value.trim();
  const role = document.getElementById('newRole').value;
  const notes = document.getElementById('newNotes').value.trim();

  if (!username) {{
    alert('Укажите позывной');
    return;
  }}

  try {{
    const res = await fetch('/api/admin/users/create', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
      body: JSON.stringify({{ username, password, role, notes }})
    }});
    const data = await res.json();
    if (data.ok) {{
      toggleAddUserModal();
      document.getElementById('newUsername').value = '';
      loadAdminUsers();
    }} else {{
      alert('Ошибка: ' + data.error);
    }}
  }} catch (e) {{
    alert('Ошибка: ' + e.message);
  }}
}}

async function toggleUserStatus(username) {{
  if (!isUserAdmin) return;
  try {{
    await fetch('/api/admin/users/toggle_status', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
      body: JSON.stringify({{ username }})
    }});
    loadAdminUsers();
  }} catch (e) {{}}
}}

async function deleteUser(username) {{
  if (!isUserAdmin) return;
  if (!confirm(`Удалить пользователя ${{username}}?`)) return;
  try {{
    await fetch('/api/admin/users/delete', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
      body: JSON.stringify({{ username }})
    }});
    loadAdminUsers();
  }} catch (e) {{}}
}}

async function loadAdminVisitors() {{
  if (!isUserAdmin) return;
  const tbody = document.getElementById('visitorsTableBody');
  tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:8px;">Загрузка...</td></tr>';

  try {{
    const res = await fetch('/api/admin/visitors?limit=50', {{ headers: {{ 'X-Telegram-User-Id': tgUserId }} }});
    const data = await res.json();
    const rows = data.visitors || [];

    tbody.innerHTML = '';
    rows.forEach(r => {{
      const tr = document.createElement('tr');
      const timeStr = (r.ts || '').substr(11, 8);
      const userDisplay = r.user || (r.tg_username ? `@${{r.tg_username}}` : (r.tg_id ? `TG:${{r.tg_id}}` : 'Гость'));
      const geoDisplay = r.country ? `${{r.country}} ${{r.city ? `(${{r.city}})` : ''}}` : 'GLOBAL';

      tr.innerHTML = `
        <td style="color:#94a3b8; font-size:10px;">${{timeStr}}</td>
        <td style="font-size:11px; font-weight:700; color:#fff;">${{userDisplay}}</td>
        <td style="font-family:monospace; color:var(--primary); font-weight:700;">${{r.ip || '—'}}</td>
        <td><span class="badge badge-api">${{geoDisplay}}</span></td>
        <td style="font-size:10px; color:#94a3b8; max-width:140px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${{r.ua || 'Telegram'}}</td>
      `;
      tbody.appendChild(tr);
    }});
  }} catch (err) {{
    tbody.innerHTML = '<tr><td colspan="5" style="color:var(--danger); text-align:center;">Ошибка</td></tr>';
  }}
}}

function openExternalUrl(url) {{
  if (!url) return;
  try {{
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.openLink) {{
      window.Telegram.WebApp.openLink(url);
      return;
    }}
  }} catch (e) {{}}
  window.open(url, '_blank', 'noopener,noreferrer');
}}

function createCmdBox(label, cmd) {{
  const box = document.createElement('div');
  box.className = 'cmd-box';
  box.innerHTML = `
    <div class="cmd-label">
      <span>${{label}}</span>
      <button class="copy-btn" onclick="copyText(this, \\`${{cmd.replace(/`/g, '\\\\`')}}\\`)">Копировать</button>
    </div>
    <div class="code-wrap">${{cmd}}</div>
  `;
  return box;
}}

function copyText(btn, text) {{
  navigator.clipboard.writeText(text).then(() => {{
    const orig = btn.innerText;
    btn.innerText = 'Скопировано!';
    setTimeout(() => {{ btn.innerText = orig; }}, 1500);
  }});
}}

function filterResultProfiles(cat, btn) {{
  if (btn && btn.parentElement) {{
    btn.parentElement.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
  }}
  const cards = document.querySelectorAll('#scanProfilesGrid .profile-card');
  cards.forEach(c => {{
    if (cat === 'Все' || c.getAttribute('data-cat') === cat) {{
      c.style.display = 'flex';
    }} else {{
      c.style.display = 'none';
    }}
  }});
}}

// СТАРТ ПРИЛОЖЕНИЯ
renderCatalog();
initUserProfile();
</script>
</body>
</html>
"""

html_path.write_text(full_html, encoding="utf-8")
print("Enhanced index.html successfully created!")
