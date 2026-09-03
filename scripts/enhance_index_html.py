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
  --bg: #05080e;
  --card-bg: rgba(12, 18, 28, 0.75);
  --card-border: rgba(255, 255, 255, 0.07);
  --card-hover-border: rgba(0, 229, 255, 0.5);
  --primary: #00ff66;
  --primary-glow: rgba(0, 255, 102, 0.25);
  --cyan: #00e5ff;
  --cyan-glow: rgba(0, 229, 255, 0.25);
  --purple: #a855f7;
  --purple-glow: rgba(168, 85, 247, 0.25);
  --yellow: #facc15;
  --yellow-glow: rgba(250, 204, 21, 0.25);
  --danger: #ff3366;
  --text: #f1f5f9;
  --text-muted: #94a3b8;
  --term-bg: #03060a;
  --term-border: rgba(0, 255, 102, 0.2);
}}

* {{ margin:0; padding:0; box-sizing:border-box; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-tap-highlight-color: transparent; }}
body {{ background:var(--bg); color:var(--text); min-height:100vh; padding:12px; padding-bottom:70px; position:relative; overflow-x:hidden; -webkit-font-smoothing: antialiased; }}

#matrixCanvas {{ position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:0; opacity:0.12; display:none; }}
.container {{ max-width:820px; margin:0 auto; position:relative; z-index:1; }}

/* Навбар */
.navbar {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--card-border); padding:8px 0 12px; margin-bottom:14px; background:rgba(5,8,14,0.85); backdrop-filter:blur(16px); }}
.brand {{ font-size:12px; font-weight:800; color:#fff; display:flex; align-items:center; gap:8px; text-transform:uppercase; letter-spacing:0.6px; cursor:pointer; }}
.brand i {{ color:var(--primary); text-shadow:0 0 10px var(--primary-glow); }}
.nav-actions {{ display:flex; align-items:center; gap:6px; flex-wrap:wrap; }}

.user-badge {{ display:inline-flex; align-items:center; gap:5px; padding:4px 9px; background:#0b1322; border-radius:8px; font-size:11px; font-weight:700; color:var(--cyan); border:1px solid rgba(0,229,255,0.2); cursor:pointer; }}
.quota-badge {{ display:inline-flex; align-items:center; gap:5px; padding:4px 9px; background:#181504; border-radius:8px; font-size:11px; font-weight:800; color:var(--yellow); border:1px solid rgba(250,204,21,0.3); cursor:pointer; transition:all .2s; }}
.quota-badge:hover {{ box-shadow:0 0 10px var(--yellow-glow); transform:translateY(-1px); }}

.view-page {{ display:none; }}
.view-page.active {{ display:block; animation:fadeIn 0.2s ease-out; }}
@keyframes fadeIn {{ from {{ opacity:0; transform:translateY(4px); }} to {{ opacity:1; transform:translateY(0); }} }}

/* Hero баннер */
.hero-stats-banner {{ display:flex; justify-content:space-between; align-items:center; background:rgba(10,16,26,0.6); border:1px solid var(--card-border); border-radius:10px; padding:8px 12px; margin-bottom:12px; backdrop-filter:blur(10px); flex-wrap:wrap; gap:6px; }}
.stat-pill {{ display:flex; align-items:center; gap:5px; font-size:10px; font-weight:700; color:#94a3b8; }}
.stat-pill i {{ color:var(--primary); }}
.stat-pill.cyan i {{ color:var(--cyan); }}
.stat-pill.purple i {{ color:var(--purple); }}
.stat-pill.yellow i {{ color:var(--yellow); }}

/* Флагманский блок AI Profiler */
.ai-profiler-compact {{ background:linear-gradient(135deg, rgba(16,11,32,0.8), rgba(24,14,48,0.7)); border:1px solid rgba(168,85,247,0.35); border-radius:12px; padding:12px 14px; margin-bottom:12px; backdrop-filter:blur(12px); box-shadow:0 4px 20px rgba(124,58,237,0.12); }}
.ai-profiler-title {{ font-size:12px; font-weight:800; color:#e9d5ff; display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }}
.ai-input-group {{ display:flex; gap:6px; }}
.ai-input {{ flex:1; padding:9px 12px; background:rgba(4,6,12,0.8); border:1px solid rgba(168,85,247,0.3); border-radius:8px; color:#fff; font-size:12px; outline:none; transition:all .2s; }}
.ai-input:focus {{ border-color:var(--purple); box-shadow:0 0 10px var(--purple-glow); }}

/* Сетка быстрого доступа (Essential Launchpad) */
.essential-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(115px, 1fr)); gap:6px; margin-bottom:14px; }}
.essential-btn {{ background:var(--card-bg); border:1px solid var(--card-border); border-radius:8px; padding:8px; cursor:pointer; transition:all .2s; backdrop-filter:blur(8px); }}
.essential-btn:hover {{ border-color:var(--cyan); transform:translateY(-1px); box-shadow:0 3px 12px rgba(0,229,255,0.1); }}
.essential-btn-title {{ font-size:11px; font-weight:800; color:#fff; display:flex; align-items:center; gap:5px; margin-bottom:2px; }}
.essential-btn-sub {{ font-size:9px; color:var(--text-muted); }}

/* Поиск по каталогу */
.search-box-row {{ display:flex; gap:6px; align-items:center; margin-bottom:10px; }}
.search-box {{ position:relative; flex:1; }}
.search-box i {{ position:absolute; left:12px; top:50%; transform:translateY(-50%); color:var(--text-muted); font-size:12px; }}
.search-box input {{ width:100%; padding:9px 12px 9px 34px; background:rgba(7,11,18,0.8); border:1px solid var(--card-border); border-radius:8px; color:#fff; font-size:12px; outline:none; transition:all .2s; }}
.search-box input:focus {{ border-color:var(--cyan); box-shadow:0 0 10px var(--cyan-glow); }}
.search-counter {{ font-size:10px; font-weight:700; color:var(--cyan); white-space:nowrap; background:rgba(11,20,36,0.6); padding:8px 10px; border-radius:8px; border:1px solid rgba(0,229,255,0.15); }}

/* Категории (Chips) */
.filter-chips {{ display:flex; gap:5px; overflow-x:auto; padding-bottom:6px; margin-bottom:12px; scrollbar-width:none; -webkit-overflow-scrolling:touch; }}
.filter-chips::-webkit-scrollbar {{ display:none; }}
.chip {{ padding:5px 10px; background:rgba(8,14,24,0.6); border:1px solid var(--card-border); border-radius:16px; font-size:10px; font-weight:700; color:#94a3b8; white-space:nowrap; cursor:pointer; display:inline-flex; align-items:center; gap:4px; transition:all .15s; }}
.chip:hover, .chip.active {{ background:rgba(0,255,102,0.1); border-color:var(--primary); color:var(--primary); }}

/* Сетка карточек каталога */
.group-title {{ font-size:12px; font-weight:800; color:var(--cyan); margin:14px 0 4px; display:flex; align-items:center; gap:5px; text-transform:uppercase; letter-spacing:0.5px; }}
.group-desc {{ font-size:10px; color:var(--text-muted); margin-bottom:8px; }}

.cards-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(240px, 1fr)); gap:8px; }}
.card {{ background:var(--card-bg); border:1px solid var(--card-border); border-radius:10px; padding:12px; cursor:pointer; transition:all .2s; display:flex; flex-direction:column; justify-content:space-between; backdrop-filter:blur(8px); }}
.card:hover {{ border-color:var(--cyan); transform:translateY(-1px); box-shadow:0 3px 15px rgba(0,229,255,0.08); }}
.card-header {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px; gap:6px; }}
.card-title {{ font-size:12px; font-weight:800; color:#fff; display:flex; align-items:center; gap:6px; line-height:1.2; }}
.card-icon {{ color:var(--primary); font-size:12px; }}
.badge {{ font-size:9px; font-weight:800; padding:2px 6px; border-radius:6px; text-transform:uppercase; white-space:nowrap; }}
.badge-api {{ background:rgba(0,255,102,0.1); color:var(--primary); border:1px solid rgba(0,255,102,0.3); }}
.badge-web {{ background:rgba(0,229,255,0.1); color:var(--cyan); border:1px solid rgba(0,229,255,0.3); }}
.badge-doc {{ background:rgba(148,163,184,0.08); color:var(--text-muted); border:1px solid rgba(148,163,184,0.2); }}

.card-purpose {{ font-size:10px; color:#cbd5e1; line-height:1.4; margin-bottom:8px; flex:1; }}
.card-target-tag {{ font-size:9px; color:var(--cyan); font-family:monospace; margin-bottom:8px; }}

/* Кнопки */
.btn-group {{ display:flex; flex-wrap:wrap; gap:5px; }}
.btn {{ padding:6px 12px; font-size:11px; font-weight:700; border-radius:6px; border:none; cursor:pointer; display:inline-flex; align-items:center; gap:5px; text-decoration:none; transition:all .15s; }}
.btn-primary {{ background:var(--primary); color:#000; font-weight:800; }}
.btn-primary:hover {{ filter:brightness(1.1); box-shadow:0 0 10px var(--primary-glow); }}
.btn-secondary {{ background:rgba(12,20,34,0.8); color:var(--text); border:1px solid var(--card-border); }}
.btn-secondary:hover {{ border-color:var(--cyan); color:#fff; }}
.btn-purple {{ background:linear-gradient(135deg, #7c3aed, #9333ea); color:#fff; }}
.btn-cyan {{ background:linear-gradient(135deg, #00e5ff, #0099ff); color:#000; font-weight:800; }}
.btn-yellow {{ background:linear-gradient(135deg, #facc15, #eab308); color:#000; font-weight:800; }}
.btn-danger {{ background:rgba(255,51,102,0.12); color:var(--danger); border:1px solid rgba(255,51,102,0.3); }}

/* Страница инструмента (toolView) */
.tool-view-header {{ background:var(--card-bg); border:1px solid var(--card-border); border-radius:12px; padding:14px; margin-bottom:10px; backdrop-filter:blur(8px); }}
.back-btn {{ display:inline-flex; align-items:center; gap:5px; color:var(--cyan); font-size:11px; font-weight:700; cursor:pointer; margin-bottom:8px; }}
.back-btn:hover {{ color:var(--primary); }}
.tool-view-title {{ font-size:15px; font-weight:800; color:#fff; margin-bottom:3px; }}
.tool-view-desc {{ font-size:11px; color:var(--text-muted); margin-bottom:10px; line-height:1.4; }}

.workspace-box {{ background:var(--card-bg); border:1px solid var(--card-border); border-radius:12px; padding:14px; margin-bottom:10px; backdrop-filter:blur(8px); }}
.workspace-title {{ font-size:11px; font-weight:800; color:var(--primary); margin-bottom:10px; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:5px; }}

.input-row {{ display:flex; gap:6px; margin-bottom:10px; }}
.tool-input {{ flex:1; padding:9px 12px; background:rgba(3,6,10,0.8); border:1px solid var(--card-border); border-radius:6px; color:#fff; font-size:12px; outline:none; }}
.tool-input:focus {{ border-color:var(--primary); box-shadow:0 0 8px var(--primary-glow); }}

/* Характеристики модуля (вместо инструкций github) */
.spec-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(160px, 1fr)); gap:6px; }}
.spec-card {{ background:rgba(5,9,16,0.6); border:1px solid var(--card-border); border-radius:6px; padding:8px 10px; }}
.spec-label {{ font-size:9px; color:var(--text-muted); margin-bottom:2px; }}
.spec-val {{ font-size:11px; font-weight:700; color:#fff; }}

/* Кастомные карточки результатов */
.custom-card {{ background:rgba(8,14,24,0.8); border:1px solid var(--card-border); border-radius:10px; padding:12px; margin-bottom:8px; }}
.custom-card-title {{ font-size:12px; font-weight:800; color:#fff; margin-bottom:8px; display:flex; align-items:center; gap:6px; }}
.custom-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:11px; }}
.custom-item {{ background:rgba(4,8,14,0.7); padding:6px 8px; border-radius:6px; border:1px solid var(--card-border); }}
.custom-label {{ color:var(--text-muted); font-size:9px; margin-bottom:2px; }}
.custom-val {{ color:#fff; font-weight:700; font-size:11px; word-break:break-all; }}

/* Профили */
.profiles-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(180px, 1fr)); gap:5px; margin-top:6px; }}
.profile-card {{ background:rgba(5,10,18,0.7); border:1px solid var(--card-border); border-radius:6px; padding:6px 8px; display:flex; align-items:center; justify-content:space-between; gap:5px; }}
.profile-name {{ font-size:10px; font-weight:700; color:#fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}

/* Терминал */
.cli-console-box {{ background:var(--term-bg); border:1px solid var(--term-border); border-radius:10px; padding:12px; margin-bottom:10px; }}
.cli-output {{ color:#38ef7d; font-family:'Courier New', monospace; font-size:11px; line-height:1.5; white-space:pre-wrap; max-height:360px; overflow-y:auto; margin-bottom:10px; }}
.cli-prompt-row {{ display:flex; align-items:center; gap:6px; font-family:'Courier New', monospace; font-size:12px; }}
.cli-prompt-label {{ color:var(--primary); font-weight:800; }}
.cli-input {{ flex:1; background:transparent; border:none; outline:none; color:#fff; font-family:'Courier New', monospace; font-size:12px; }}

/* Дропзона */
.upload-dropzone {{ border:1px dashed rgba(0,229,255,0.3); border-radius:10px; padding:18px 12px; text-align:center; background:rgba(6,13,26,0.5); cursor:pointer; transition:all .2s; margin-bottom:8px; }}
.upload-dropzone:hover {{ border-color:var(--cyan); background:rgba(9,20,38,0.7); }}
.upload-preview {{ max-width:100%; max-height:200px; border-radius:6px; margin-top:8px; display:none; border:1px solid var(--card-border); }}

/* Спиннер */
.loader {{ display:none; text-align:center; padding:12px; }}
.spinner {{ width:20px; height:20px; border:2px solid rgba(0,255,102,0.2); border-top-color:var(--primary); border-radius:50%; animation:spin .8s linear infinite; margin:0 auto 6px; }}
@keyframes spin {{ to {{ transform:rotate(360deg); }} }}

/* Авторизация */
.auth-container {{ display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:60vh; padding:16px; }}
.auth-card {{ background:var(--card-bg); border:1px solid var(--card-border); border-radius:14px; padding:20px; max-width:380px; width:100%; text-align:center; backdrop-filter:blur(12px); }}
.auth-icon {{ font-size:36px; color:var(--primary); margin-bottom:10px; }}
.auth-title {{ font-size:14px; font-weight:800; color:#fff; margin-bottom:4px; }}
.auth-subtitle {{ font-size:10px; color:var(--text-muted); margin-bottom:14px; line-height:1.4; }}
.auth-input {{ width:100%; padding:10px 12px; background:rgba(3,6,10,0.8); border:1px solid var(--card-border); border-radius:8px; color:#fff; font-size:12px; outline:none; margin-bottom:10px; text-align:center; }}
.auth-input:focus {{ border-color:var(--primary); box-shadow:0 0 10px var(--primary-glow); }}

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
      <span style="font-weight:900; letter-spacing:0.5px; font-size:12px;">OSINT TERMINAL</span>
      <span style="font-size:8px; background:rgba(0,255,102,0.15); color:var(--primary); padding:1px 5px; border-radius:4px; font-weight:800; border:1px solid rgba(0,255,102,0.3);">LIVE</span>
    </div>
    <div class="nav-actions">
      <div class="quota-badge" id="quotaBadge" onclick="openStarsModal()" title="Баланс запросов и Stars">
        <i class="fa-solid fa-star"></i> <span id="quotaSpan">5/5 Запросов</span>
      </div>
      <button class="btn btn-yellow" id="navAdminBtn" onclick="openAdminPanel()" style="display:none; padding:4px 8px; font-size:10px;"><i class="fa-solid fa-crown"></i> Админ</button>
      <div class="user-badge" id="currentUserBadge" style="display:none;" onclick="handleUserBadgeClick()">
        <i id="userBadgeIcon" class="fa-solid fa-user-check"></i> <span id="currentUsernameSpan">Позывной</span>
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
    <div style="background:rgba(12,18,28,0.85); border:1px solid rgba(0,229,255,0.25); border-radius:12px; padding:12px; margin-bottom:12px; box-shadow:0 4px 20px rgba(0,0,0,0.4); backdrop-filter:blur(12px);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <div style="font-size:11px; font-weight:800; color:#fff; display:flex; align-items:center; gap:5px;">
          <i class="fa-solid fa-crosshairs" style="color:var(--cyan);"></i> Универсальный OSINT Поиск & AI Досье
        </div>
        <div class="search-counter" id="searchCounterBadge" style="font-size:9px; padding:3px 7px;">52 утилиты</div>
      </div>
      <div style="display:flex; gap:6px;">
        <input type="text" id="searchInput" class="quick-input" style="flex:1; padding:9px 12px; font-size:12px;" placeholder="Никнейм (@user), кошелек (0x/BTC), домен, телефон или инструмент..." oninput="renderCatalog()" onkeydown="if(event.key==='Enter') runMainOmniSearch()">
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
        <div class="essential-btn-title" style="color:#e9d5ff;"><i class="fa-solid fa-brain" style="color:#a855f7;"></i> AI Досье</div>
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
let userScanBalance = 5;
let isUserUnlimited = false;
let cliHistory = [];
let cliHistoryIndex = -1;
let matrixActive = false;
let visNetworkInstance = null;
let lastAutoReconData = null;

const tg = window.Telegram?.WebApp;
if (tg) {{
  tg.expand();
  tg.ready();
}}

// FINGERPRINTING FUNCTION FOR MULTI-ACCOUNT DETECTION
async function getDeviceFingerprint() {{
  try {{
    let canvasData = '';
    try {{
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillStyle = '#f60';
      ctx.fillRect(125,1,62,20);
      ctx.fillStyle = '#069';
      ctx.fillText('sorber_recon_fp_1.0', 2, 15);
      canvasData = canvas.toDataURL();
    }} catch(e){{}}

    let glInfo = '';
    try {{
      const gl = document.createElement('canvas').getContext('webgl');
      if (gl) {{
        const dbg = gl.getExtension('WEBGL_debug_renderer_info');
        glInfo = dbg ? (gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL) + '~' + gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL)) : '';
      }}
    }} catch(e){{}}

    const nav = window.navigator;
    const screen = window.screen;
    const raw = [
      canvasData.slice(0, 100),
      glInfo,
      nav.userAgent,
      nav.language,
      nav.hardwareConcurrency || 4,
      screen.width + 'x' + screen.height,
      screen.colorDepth,
      Intl.DateTimeFormat().resolvedOptions().timeZone
    ].join('###');

    let hash = 0;
    for (let i = 0; i < raw.length; i++) {{
      const char = raw.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash |= 0;
    }}
    return 'df_' + Math.abs(hash).toString(16);
  }} catch(e) {{
    return 'df_fallback_' + (localStorage.getItem('osint_local_uid') || '0');
  }}
}}

// STARS MODAL
function openStarsModal() {{
  document.getElementById('starsModal').style.display = 'flex';
}}

function closeStarsModal() {{
  document.getElementById('starsModal').style.display = 'none';
}}

function buyStarsPkg(pkgKey) {{
  closeStarsModal();
  if (tg && tg.sendData) {{
    tg.sendData('/buy');
  }}
  alert('⭐️ Для покупки пакета через Telegram Stars отправьте команду /buy в чате нашего бота!');
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
    ctx.fillStyle = 'rgba(4, 6, 10, 0.08)';
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
    openStarsModal();
  }}
}}

function updateQuotaDisplay(balance, unlimited) {{
  userScanBalance = balance;
  isUserUnlimited = unlimited;
  const qBadge = document.getElementById('quotaSpan');
  if (unlimited) {{
    qBadge.innerText = '👑 VIP Безлимит';
  }} else {{
    qBadge.innerText = `⭐️ ${{balance}} запросов`;
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

  // Immediate UI activation
  currentSessionUser = tgUser || tgName || `Agent_${{tgId.slice(-4)}}`;
  const badgeEl = document.getElementById('currentUserBadge');
  const spanEl = document.getElementById('currentUsernameSpan');
  if (badgeEl && spanEl) {{
    spanEl.innerText = currentSessionUser;
    badgeEl.style.display = 'inline-flex';
  }}
  renderCatalog();
  showView('catalogView');

  let fp = 'df_default';
  try {{
    fp = await getDeviceFingerprint();
  }} catch(e) {{}}

  try {{
    const res = await fetch('/api/user/profile', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgId }},
      body: JSON.stringify({{ tg_id: tgId, tg_username: tgUser, tg_name: tgName, fingerprint: fp }})
    }});
    const data = await res.json();

    if (data.blocked) {{
      showView('blockedView');
      return;
    }}

    updateQuotaDisplay(data.scan_balance ?? 5, data.is_unlimited ?? false);

    if (data.is_admin) {{
      isUserAdmin = true;
      currentSessionUser = data.nickname || 'Admin';
      document.getElementById('userBadgeIcon').className = 'fa-solid fa-user-shield';
      document.getElementById('currentUsernameSpan').innerText = currentSessionUser;
    }} else if (data.registered) {{
      isUserAdmin = false;
      currentSessionUser = data.nickname;
      document.getElementById('userBadgeIcon').className = 'fa-solid fa-user-check';
      document.getElementById('currentUsernameSpan').innerText = currentSessionUser;
    }}
  }} catch (e) {{
    console.warn('Profile init:', e);
  }}
}}

async function doRegister() {{
  const nickname = document.getElementById('regNicknameInput').value.trim();
  const statusMsg = document.getElementById('regStatusMsg');
  if (!nickname || nickname.length < 2) {{
    statusMsg.innerText = 'Позывной должен содержать минимум 2 символа';
    statusMsg.style.display = 'block';
    return;
  }}

  const fp = await getDeviceFingerprint();

  try {{
    const res = await fetch('/api/user/profile', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
      body: JSON.stringify({{ tg_id: tgUserId, nickname, fingerprint: fp }})
    }});
    const data = await res.json();

    if (data.ok && data.registered) {{
      currentSessionUser = data.nickname;
      isUserAdmin = data.is_admin;
      updateQuotaDisplay(data.scan_balance ?? 5, data.is_unlimited ?? false);

      document.getElementById('currentUserBadge').style.display = 'inline-flex';
      document.getElementById('userBadgeIcon').className = isUserAdmin ? 'fa-solid fa-user-shield' : 'fa-solid fa-user-check';
      document.getElementById('currentUsernameSpan').innerText = currentSessionUser;
      showView('catalogView');
    }} else {{
      statusMsg.innerText = data.error || 'Ошибка регистрации';
      statusMsg.style.display = 'block';
    }}
  }} catch (e) {{
    statusMsg.innerText = 'Сетевая ошибка: ' + e.message;
    statusMsg.style.display = 'block';
  }}
}}

// РЕНДЕР КАТАЛОГА
function setFilter(cat, element) {{
  currentCategory = cat;
  document.querySelectorAll('.filter-chips .chip').forEach(c => c.classList.remove('active'));
  if (element) element.classList.add('active');
  renderCatalog();
}}

function renderCatalog() {{
  const search = (document.getElementById('searchInput')?.value || '').toLowerCase().trim();
  const container = document.getElementById('catalogContainer');
  if (!container) return;

  container.innerHTML = '';
  let totalToolsCount = 0;

  FULL_CATALOG.forEach(group => {{
    if (currentCategory !== 'all' && group.id !== currentCategory) return;

    const filteredTools = group.tools.filter(t => {{
      if (!search) return true;
      return t.name.toLowerCase().includes(search) ||
             t.purpose.toLowerCase().includes(search) ||
             t.id.toLowerCase().includes(search) ||
             (t.input || '').toLowerCase().includes(search);
    }});

    if (filteredTools.length === 0) return;
    totalToolsCount += filteredTools.length;

    const groupTitle = document.createElement('div');
    groupTitle.className = 'group-title';
    groupTitle.innerHTML = group.title;
    container.appendChild(groupTitle);

    const groupDesc = document.createElement('div');
    groupDesc.className = 'group-desc';
    groupDesc.innerText = group.desc;
    container.appendChild(groupDesc);

    const grid = document.createElement('div');
    grid.className = 'cards-grid';

    filteredTools.forEach(tool => {{
      const card = document.createElement('div');
      card.className = 'card';
      card.onclick = () => openToolPage(tool.id);

      let badgeHtml = '<span class="badge badge-api">API Engine</span>';
      if (tool.scan_type === 'decoder') badgeHtml = '<span class="badge badge-api">Cyber Lab</span>';
      else if (tool.scan_type === 'crypto') badgeHtml = '<span class="badge badge-api" style="border-color:#facc15; color:#facc15;">Crypto</span>';
      else if (tool.scan_type === 'dorks') badgeHtml = '<span class="badge badge-api" style="border-color:#a855f7; color:#a855f7;">Dork Matrix</span>';
      else if (!tool.web_runnable) badgeHtml = '<span class="badge badge-doc">CLI Tool</span>';

      card.innerHTML = `
        <div>
          <div class="card-header">
            <div class="card-title">
              <i class="fa-solid fa-cube card-icon"></i>
              <span>${{tool.name}}</span>
            </div>
            ${{badgeHtml}}
          </div>
          <div class="card-purpose">${{tool.purpose}}</div>
        </div>
        <div>
          <div class="card-target-tag">Target: ${{tool.input || 'string'}}</div>
          <div class="btn-group">
            <button class="btn btn-primary" style="padding:5px 10px; font-size:10px;" onclick="event.stopPropagation(); openToolPage('${{tool.id}}')">
              <i class="fa-solid fa-play"></i> Открыть
            </button>
            ${{tool.repo ? `<button class="btn btn-secondary" style="padding:5px 10px; font-size:10px;" onclick="event.stopPropagation(); openExternalUrl('${{tool.repo}}')"><i class="fa-brands fa-github"></i></button>` : ''}}
          </div>
        </div>
      `;
      grid.appendChild(card);
    }});

    container.appendChild(grid);
  }});

  const counterBadge = document.getElementById('searchCounterBadge');
  if (counterBadge) counterBadge.innerText = `${{totalToolsCount}} утилит`;
}}

function openToolPage(toolId) {{
  let found = null;
  FULL_CATALOG.forEach(g => {{
    g.tools.forEach(t => {{ if (t.id === toolId) found = t; }});
  }});
  if (!found) return;

  activeTool = found;
  document.getElementById('tvTitle').innerText = found.name;
  document.getElementById('tvPurpose').innerText = found.purpose;
  document.getElementById('tvTargetFormat').innerText = found.input || 'string / handle';

  const headerBtns = document.getElementById('tvHeaderButtons');
  headerBtns.innerHTML = '';
  if (found.web_url) {{
    headerBtns.innerHTML += `<button onclick="openExternalUrl('${{found.web_url}}')" class="btn btn-cyan" style="padding:4px 8px; font-size:10px;"><i class="fa-solid fa-arrow-up-right-from-square"></i> Сервис</button>`;
  }}
  if (found.repo) {{
    headerBtns.innerHTML += `<button onclick="openExternalUrl('${{found.repo}}')" class="btn btn-secondary" style="padding:4px 8px; font-size:10px;"><i class="fa-brands fa-github"></i></button>`;
  }}

  const photoBox = document.getElementById('tvPhotoUploaderBox');
  const textRow = document.getElementById('tvTextInputRow');
  const targetInput = document.getElementById('tvTargetInput');
  const outBox = document.getElementById('tvOutputBox');
  outBox.style.display = 'none';

  if (found.scan_type === 'photo' || found.id === 'photo_exif_gps' || found.scan_type === 'face_search') {{
    photoBox.style.display = 'block';
    textRow.style.display = 'none';
  }} else {{
    photoBox.style.display = 'none';
    textRow.style.display = 'flex';
    targetInput.placeholder = `Введите цель (${{found.input || 'username / url'}})...`;
  }}

  showView('toolView');
}}

// ЗАПУСК СКАНЕРА
async function runCurrentToolScan() {{
  if (!activeTool) return;
  const target = document.getElementById('tvTargetInput').value.trim();
  if (!target) {{
    alert('Введите цель для проверки');
    return;
  }}
  executeToolScan(activeTool.id, target);
}}

async function runMainQuickScan() {{
  const target = (document.getElementById('searchInput') || document.getElementById('searchInput')).value.trim();
  if (!target) {{
    alert('Введите никнейм, логин GitHub, телефон или домен');
    return;
  }}

  // Check if crypto
  if (target.startsWith('0x') || (target.startsWith('T') && target.length === 34) || target.startsWith('bc1') || (target.startsWith('1') && target.length >= 26)) {{
    openToolPage('crypto_forensics');
    executeToolScan('crypto_forensics', target);
    return;
  }}

  openToolPage('autorecon');
  executeToolScan('autorecon', target);
}}

async function executeToolScan(toolId, target) {{
  const loader = document.getElementById('tvLoader');
  const loaderText = document.getElementById('tvLoaderText');
  const outBox = document.getElementById('tvOutputBox');

  loader.style.display = 'block';
  loaderText.innerText = `Запуск ${{toolId}} для "${{target}}"...`;
  outBox.style.display = 'none';

  try {{
    const res = await fetch('/api/scan/universal', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
      body: JSON.stringify({{ tool_id: toolId, target, caller: currentSessionUser }})
    }});
    const data = await res.json();
    loader.style.display = 'none';
    outBox.style.display = 'block';

    if (data.code === 'QUOTA_EXCEEDED') {{
      outBox.innerHTML = `
        <div style="background:#181005; border:2px solid #eab308; border-radius:12px; padding:16px; text-align:center;">
          <div style="font-size:16px; font-weight:800; color:#facc15; margin-bottom:6px;">⭐️ Лимит запросов исчерпан</div>
          <div style="font-size:11px; color:#cbd5e1; margin-bottom:12px;">${{data.error}}</div>
          <button class="btn btn-yellow" onclick="openStarsModal()"><i class="fa-solid fa-star"></i> Пополнить за Stars</button>
        </div>
      `;
      return;
    }}

    renderToolScanResult(data, outBox, target, toolId);
  }} catch (err) {{
    loader.style.display = 'none';
    outBox.style.display = 'block';
    outBox.innerHTML = `<div style="color:var(--danger); font-size:12px;">❌ Ошибка выполнения: ${{err.message}}</div>`;
  }}
}}

// РЕНДЕР РЕЗУЛЬТАТОВ
function renderToolScanResult(data, outBox, target, toolId) {{
  const nowStr = new Date().toISOString().replace('T', ' ').substr(11, 8);
  const safeToolId = toolId || (data ? data.tool_id : '') || (activeTool ? activeTool.id : 'tool');
  const safeToolName = (data ? data.tool_name : '') || (activeTool ? activeTool.name : safeToolId);
  let html = '';

  // 0.1. AI DETECTIVE PROFILER
  if (data.type === 'ai_profiler') {{
    const scam = data.scam_score !== undefined ? data.scam_score : 15;
    const scamColor = scam < 30 ? 'var(--primary)' : (scam < 60 ? 'var(--yellow)' : 'var(--danger)');
    const scamBg = scam < 30 ? 'rgba(0,255,102,0.1)' : (scam < 60 ? 'rgba(250,204,21,0.1)' : 'rgba(255,51,102,0.1)');

    html += `
      <div class="custom-card" style="border:1px solid rgba(168,85,247,0.4); box-shadow:0 4px 20px rgba(124,58,237,0.15);">
        <div class="custom-card-title" style="color:#e9d5ff; justify-content:space-between;">
          <span><i class="fa-solid fa-brain" style="color:#c084fc;"></i> Досье личности: <b>${{target}}</b></span>
          <span class="badge" style="background:${{scamBg}}; color:${{scamColor}}; border:1px solid ${{scamColor}};">Scam Score: ${{scam}}%</span>
        </div>
        
        <div style="margin:8px 0;">
          <div style="height:6px; background:#04070e; border-radius:3px; overflow:hidden; border:1px solid var(--card-border);">
            <div style="height:100%; width:${{scam}}%; background:linear-gradient(90deg, #00ff66, #facc15, #ff3366); transition:width .6s;"></div>
          </div>
        </div>

        <div class="custom-grid" style="margin-bottom:8px;">
          <div class="custom-item">
            <div class="custom-label">🛡️ Оценка подлинности</div>
            <div class="custom-val" style="color:${{scamColor}};">${{data.trust_level || 'Normal'}} Trust</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🌐 Найдено платформ</div>
            <div class="custom-val">${{data.profiles_count || 0}} сервисов</div>
          </div>
        </div>

        <div style="font-size:10px; color:#94a3b8; background:rgba(3,6,10,0.6); padding:8px 10px; border-radius:6px; margin-bottom:8px;">
          ${{(data.risk_factors || []).map(r => `<div style="margin-bottom:2px;">• ${{r}}</div>`).join('')}}
        </div>

        <details open style="margin-bottom:8px; cursor:pointer;">
          <summary style="font-size:11px; font-weight:700; color:var(--cyan); padding:4px 0; outline:none;">
            📄 Аналитическое AI-досье и психологический портрет
          </summary>
          <div style="font-size:10px; color:#e2e8f0; line-height:1.5; background:rgba(3,6,10,0.9); padding:10px; border-radius:6px; border:1px solid var(--card-border); white-space:pre-wrap; margin-top:6px;">${{data.dossier_text || 'Досье сформировано.'}}</div>
        </details>

        <div class="btn-group">
          <button class="btn btn-purple" style="padding:4px 10px; font-size:10px;" onclick="printDossierReport()"><i class="fa-solid fa-print"></i> PDF / Печать</button>
          <button class="btn btn-secondary" style="padding:4px 10px; font-size:10px;" onclick="copyText(this, \`${{(data.dossier_text || '').replace(/`/g, '\\`')}}\`)"><i class="fa-solid fa-copy"></i> Копировать</button>
        </div>
      </div>
    `;

  // 0.2. ACTIVITY & SLEEP TRACKER
  }} else if (data.type === 'activity_tracker') {{
    const hourly = data.hourly_activity || [];
    const mutual = data.mutual_analysis;

    html += `
      <div class="custom-card" style="border-color:var(--cyan);">
        <div class="custom-card-title" style="color:var(--cyan);"><i class="fa-solid fa-user-secret"></i> Активность & Анализ сна: @${{data.target}}</div>
        
        <div class="custom-grid" style="margin-bottom:10px;">
          <div class="custom-item">
            <div class="custom-label">🌍 Часовой пояс</div>
            <div class="custom-val">${{data.timezone}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">💤 Фаза сна / Оффлайн</div>
            <div class="custom-val" style="color:var(--primary);">${{data.sleep_phase}}</div>
          </div>
          <div class="custom-item" style="grid-column:span 2;">
            <div class="custom-label">🔥 Пики активности</div>
            <div class="custom-val">${{data.peak_activity}}</div>
          </div>
        </div>

        <div style="font-size:10px; font-weight:700; color:#fff; margin-bottom:4px;">📊 Суточная тепловая шкала онлайна (00:00 - 23:00):</div>
        <div style="display:flex; gap:2px; height:40px; align-items:flex-end; background:#04070e; padding:4px; border-radius:6px; border:1px solid var(--card-border); margin-bottom:10px;">
          ${{hourly.map((val, h) => `
            <div style="flex:1; display:flex; flex-direction:column; align-items:center; height:100%; justify-content:flex-end;" title="${{h}}:00 - ${{val}}% активность">
              <div style="width:100%; height:${{val}}%; background:${{val < 30 ? '#1e293b' : (val < 70 ? 'var(--cyan)' : 'var(--primary)')}}; border-radius:2px;"></div>
              <span style="font-size:6px; color:#64748b; margin-top:1px;">${{h % 4 === 0 ? h : ''}}</span>
            </div>
          `).join('')}}
        </div>
    `;

    if (mutual) {{
      html += `
        <div style="background:rgba(19,14,34,0.8); border:1px solid rgba(168,85,247,0.4); border-radius:6px; padding:8px; margin-top:6px;">
          <div style="font-size:11px; font-weight:800; color:#c084fc; margin-bottom:3px;">
            <i class="fa-solid fa-heart-pulse"></i> Mutual Spy: Совпадение с @${{mutual.target2}}
          </div>
          <div style="font-size:10px; color:#e2e8f0; font-weight:700; margin-bottom:4px;">${{mutual.communication_likelihood}}</div>
          <div style="height:5px; background:#070c16; border-radius:3px; overflow:hidden;">
            <div style="height:100%; width:${{mutual.overlap_score}}%; background:linear-gradient(90deg, #38ef7d, #a855f7);"></div>
          </div>
        </div>
      `;
    }}
    html += '</div>';

  // 0.3. CRYPTO AML & SANCTIONS AUDITOR
  }} else if (data.type === 'crypto_aml') {{
    const risk = data.aml_risk_score || 10;
    const rColor = risk < 30 ? 'var(--primary)' : (risk < 60 ? 'var(--yellow)' : 'var(--danger)');
    const rBg = risk < 30 ? 'rgba(0,255,102,0.1)' : (risk < 60 ? 'rgba(250,204,21,0.1)' : 'rgba(255,51,102,0.1)');
    const bd = data.breakdown || {{}};

    html += `
      <div class="custom-card" style="border-color:${{rColor}};">
        <div class="custom-card-title" style="color:#fff; justify-content:space-between;">
          <span><i class="fa-solid fa-shield-halved" style="color:${{rColor}};"></i> AML Audit: ${{data.coin}}</span>
          <span class="badge" style="background:${{rBg}}; color:${{rColor}}; border:1px solid ${{rColor}};">${{data.risk_level}}</span>
        </div>
        <div style="font-family:monospace; font-size:10px; color:var(--cyan); word-break:break-all; margin-bottom:8px;">${{data.address}}</div>

        <div class="custom-grid" style="margin-bottom:8px;">
          <div class="custom-item">
            <div class="custom-label">📊 Риск AML</div>
            <div class="custom-val" style="color:${{rColor}};">${{risk}}% / 100%</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🏛️ Санкции OFAC</div>
            <div class="custom-val">${{bd.sanctions_risk > 50 ? '🚨 MATCH' : '🟢 Чисто'}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🌪️ Миксеры (Tornado)</div>
            <div class="custom-val">${{bd.mixer_exposure || 0}}%</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🏴‍☠️ Даркнет</div>
            <div class="custom-val">${{bd.darknet_exposure || 0}}%</div>
          </div>
        </div>

        <div style="background:rgba(7,13,24,0.8); border:1px solid var(--card-border); border-radius:6px; padding:8px; margin-bottom:8px;">
          <div style="font-size:9px; color:#94a3b8; margin-bottom:1px;">💡 Рекомендация для сделок:</div>
          <div style="font-size:10px; font-weight:700; color:#fff;">${{data.recommendation}}</div>
        </div>

        <div style="font-size:9px; color:#94a3b8;">
          ${{(data.flags || []).map(f => `<div style="margin-bottom:1px;">• ${{f}}</div>`).join('')}}
        </div>
      </div>
    `;

  // 0.4. REVERSE FACE AI
  }} else if (data.type === 'face_search') {{
    html += `
      <div class="custom-card" style="border-color:var(--purple);">
        <div class="custom-card-title" style="color:var(--purple);"><i class="fa-solid fa-camera-retro"></i> Face AI & Deepfake Detector</div>
        
        <div class="custom-grid" style="margin-bottom:8px;">
          <div class="custom-item">
            <div class="custom-label">🎭 Вероятность Deepfake / GAN</div>
            <div class="custom-val" style="color:var(--cyan);">${{data.deepfake_probability}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🎂 Примерный возраст</div>
            <div class="custom-val">${{data.estimated_age}}</div>
          </div>
          <div class="custom-item" style="grid-column:span 2;">
            <div class="custom-label">🔍 Вердикт</div>
            <div class="custom-val">${{data.ai_verdict}}</div>
          </div>
        </div>

        <div style="font-size:10px; font-weight:700; color:#fff; margin-bottom:4px;">Найдено похожих аватаров (${{data.matches_count}}):</div>
        <div class="profiles-grid">
          ${{(data.matches || []).map(m => `
            <div class="profile-card">
              <div>
                <div class="profile-name">${{m.platform}}</div>
                <div style="font-size:8px; color:var(--primary); font-weight:700;">Совпадение: ${{m.similarity}}</div>
              </div>
              <button onclick="openExternalUrl('${{m.url}}')" class="btn btn-secondary" style="padding:2px 6px; font-size:9px;">Открыть</button>
            </div>
          `).join('')}}
        </div>
      </div>
    `;

  // 0.5. DIGITAL HYGIENE & BREACH AUDIT
  }} else if (data.type === 'breach_audit') {{
    const exp = data.exposure_score || 20;
    const expColor = exp < 30 ? 'var(--primary)' : (exp < 60 ? 'var(--yellow)' : 'var(--danger)');

    html += `
      <div class="custom-card" style="border-color:${{expColor}};">
        <div class="custom-card-title" style="color:#fff; justify-content:space-between;">
          <span><i class="fa-solid fa-shield-virus" style="color:${{expColor}};"></i> Аудит безопасности: "${{data.identifier}}"</span>
          <span class="badge" style="border-color:${{expColor}}; color:${{expColor}};">${{data.security_grade}}</span>
        </div>

        <div class="custom-grid" style="margin-bottom:8px;">
          <div class="custom-item">
            <div class="custom-label">🚨 Обнаружено утечек</div>
            <div class="custom-val" style="color:${{expColor}};">${{data.leaks_count}} баз данных</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">📈 Индекс уязвимости</div>
            <div class="custom-val" style="color:${{expColor}};">${{data.exposure_score}} / 100</div>
          </div>
        </div>

        <div style="font-size:10px; font-weight:700; color:#fff; margin-bottom:4px;">Упоминания в публичных утечках:</div>
        <div style="margin-bottom:8px;">
          ${{(data.leaks || []).map(l => `
            <div style="background:rgba(4,8,14,0.7); border:1px solid var(--card-border); border-radius:4px; padding:4px 8px; margin-bottom:3px; display:flex; justify-content:space-between; font-size:9px;">
              <span style="font-weight:700; color:#fff;">📁 ${{l.source}}</span>
              <span style="color:#94a3b8;">${{l.date}} (${{l.leaked}})</span>
            </div>
          `).join('')}}
        </div>

        <div style="background:rgba(9,20,34,0.8); border:1px solid var(--card-border); border-radius:6px; padding:8px;">
          <div style="font-size:10px; font-weight:800; color:var(--cyan); margin-bottom:3px;">🛡️ Рекомендации по защите:</div>
          ${{(data.remediation_checklist || []).map(c => `<div style="font-size:9px; color:#cbd5e1; margin-bottom:2px;">${{c}}</div>`).join('')}}
        </div>
      </div>
    `;

  // 0.6. TARGET MONITOR ALERTS
  }} else if (data.type === 'alerts_subscribe') {{
    html += `
      <div class="custom-card" style="border-color:var(--primary);">
        <div class="custom-card-title" style="color:var(--primary);"><i class="fa-solid fa-bell"></i> Мониторинг цели активирован</div>
        <div style="font-size:11px; color:#fff; margin-bottom:6px;">${{data.message}}</div>
        <div style="font-size:10px; color:#94a3b8;">Активных слотов: <b>${{data.active_slots}}/10</b>. Уведомления об изменении био, юзернейма или крупных транзакциях поступят в Telegram.</div>
      </div>
    `;

  // 1. CRYPTO FORENSICS
  }} else if (data.type === 'crypto') {{
    const cd = data.data || {{}};
    let logLines = data.raw_cli_output || `[${{nowStr}}] [CRYPTO] ${{data.target}}`;
    html += `
      <div class="hacker-terminal">
        <div class="term-topbar">
          <div class="term-dots"><span class="term-dot term-dot-green"></span></div>
          <span>CRYPTO-RECON@STATION:~# crypto_recon --address ${{data.target}}</span>
          <button class="copy-btn" onclick="copyText(this, \`${{logLines.replace(/`/g, '\\`')}}\`)">📋 Копировать CLI</button>
        </div>
        <div class="term-log-content">${{logLines}}</div>
      </div>

      <div class="custom-card" style="border-color:#facc15;">
        <div class="custom-card-title"><i class="fa-solid fa-coins" style="color:#facc15;"></i> Разведка Блокчейн Кошелька</div>
        <div class="custom-grid">
          <div class="custom-item">
            <div class="custom-label">🪙 Сеть / Монета</div>
            <div class="custom-val" style="color:#facc15;">${{cd.coin_type}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">💰 Текущий баланс</div>
            <div class="custom-val" style="color:var(--primary); font-size:13px;">${{cd.balance}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">📊 Всего транзакций</div>
            <div class="custom-val">${{cd.tx_count}} tx</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🕒 Активность</div>
            <div class="custom-val">${{cd.last_seen || '—'}}</div>
          </div>
        </div>
        <div style="margin-top:10px;">
          <button onclick="openExternalUrl('${{cd.explorer_url}}')" class="btn btn-yellow" style="width:100%; justify-content:center;">
            <i class="fa-solid fa-arrow-up-right-from-square"></i> Открыть в Блокчейн-Эксплорере
          </button>
        </div>
      </div>
    `;

  // 2. OSINT DORKING MATRIX
  }} else if (data.type === 'dorks') {{
    let logLines = data.raw_cli_output || `[${{nowStr}}] [DORKS] TARGET: ${{data.target}}`;
    html += `
      <div class="hacker-terminal">
        <div class="term-topbar">
          <div class="term-dots"><span class="term-dot term-dot-green"></span></div>
          <span>DORKING-WIZARD@STATION:~# dork_matrix "${{data.target}}"</span>
          <button class="copy-btn" onclick="copyText(this, \`${{logLines.replace(/`/g, '\\`')}}\`)">📋 Копировать CLI</button>
        </div>
        <div class="term-log-content">${{logLines}}</div>
      </div>

      <div style="font-size:12px; font-weight:800; color:#fff; margin-bottom:8px;">
        🧙‍♂️ Сгенерировано ${{data.total_dorks}} целевых дорков для "${{data.target}}":
      </div>
    `;

    (data.categories || []).forEach(cat => {{
      html += `
        <div class="custom-card">
          <div class="custom-card-title"><i class="${{cat.icon || 'fa-solid fa-magnifying-glass'}}" style="color:var(--cyan);"></i> ${{cat.category}}</div>
      `;
      (cat.dorks || []).forEach(d => {{
        html += `
          <div class="dork-item">
            <div class="dork-title">
              <span>${{d.title}}</span>
              <button class="copy-btn" onclick="copyText(this, \`${{d.dork.replace(/`/g, '\\`')}}\`)">Копировать дорк</button>
            </div>
            <div class="dork-code">${{d.dork}}</div>
            <div class="btn-group">
              <button onclick="openExternalUrl('${{d.google}}')" class="btn btn-primary" style="padding:3px 8px; font-size:10px;"><i class="fa-brands fa-google"></i> Google</button>
              <button onclick="openExternalUrl('${{d.yandex}}')" class="btn btn-secondary" style="padding:3px 8px; font-size:10px;"><i class="fa-brands fa-yandex"></i> Яндекс</button>
            </div>
          </div>
        `;
      }});
      html += '</div>';
    }});

  // 3. AUTO-RECON
  }} else if (data.type === 'autorecon') {{
    html += `
      <div class="custom-card" style="border-color:var(--primary);">
        <div class="custom-card-title" style="color:var(--primary);"><i class="fa-solid fa-file-shield"></i> Тактическое Досье Расследования</div>
        <div style="color:#cbd5e1; font-size:11px; line-height:1.55; white-space:pre-wrap;">${{data.ai_dossier}}</div>
        <div style="margin-top:8px;">
          <button class="btn btn-cyan" onclick="showView('graphView')"><i class="fa-solid fa-project-diagram"></i> Открыть Граф Связей</button>
        </div>
      </div>
    `;

  // 4. GITHUB RECON
  }} else if (data.type === 'github') {{
    const ems = data.emails_discovered || [];
    html += `
      <div class="custom-card">
        <div class="custom-card-title"><i class="fa-brands fa-github" style="color:var(--primary);"></i> GitHub Профиль & Скрытые Email</div>
        <div class="custom-grid">
          <div class="custom-item">
            <div class="custom-label">👤 Логин</div>
            <div class="custom-val">${{data.login}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🪪 ФИО</div>
            <div class="custom-val">${{data.name || '—'}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">📦 Репозиториев</div>
            <div class="custom-val">${{data.public_repos_count}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">📍 Локация</div>
            <div class="custom-val">${{data.location || 'Скрыта'}}</div>
          </div>
        </div>
      </div>
    `;
    if (ems.length > 0) {{
      html += `
        <div class="custom-card" style="border-color:var(--danger);">
          <div class="custom-card-title" style="color:var(--danger);"><i class="fa-solid fa-envelope-open-text"></i> Email адреса из коммитов</div>
          <div class="btn-group">
            ${{ems.map(e => `<span class="badge badge-api" style="font-size:10px; padding:3px 7px; border-color:var(--danger); color:#fff;">✉️ ${{e}}</span>`).join('')}}
          </div>
        </div>
      `;
    }}

  // 5. USERNAME / SHERLOCK
  }} else if (data.type === 'username') {{
    const profiles = data.profiles || [];
    html += `
      <div class="custom-card">
        <div class="custom-card-title"><i class="fa-solid fa-magnifying-glass" style="color:var(--cyan);"></i> Поиск по никнейму "${{target}}"</div>
        <div style="font-size:11px; color:var(--primary); font-weight:700; margin-bottom:6px;">Найдено совпадений: ${{data.found_count}} из ${{data.total_checked}} баз</div>
        <div class="profiles-grid">
          ${{profiles.map(p => `
            <div class="profile-card">
              <div class="profile-name">${{p.platform}}</div>
              <button onclick="openExternalUrl('${{p.url}}')" class="btn btn-secondary" style="padding:2px 6px; font-size:9px;">Открыть</button>
            </div>
          `).join('')}}
        </div>
      </div>
    `;

  // 6. PHONE
  }} else if (data.type === 'phone') {{
    html += `
      <div class="custom-card">
        <div class="custom-card-title"><i class="fa-solid fa-phone" style="color:var(--primary);"></i> Данные оператора и региона</div>
        <div class="custom-grid">
          <div class="custom-item">
            <div class="custom-label">📞 Номер</div>
            <div class="custom-val" style="color:var(--primary);">${{data.e164}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🏢 Оператор</div>
            <div class="custom-val">${{data.carrier}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🌍 Страна</div>
            <div class="custom-val">${{data.country}}</div>
          </div>
          <div class="custom-item">
            <div class="custom-label">🏷️ Тип линии</div>
            <div class="custom-val">${{data.is_voip_suspect ? '⚠️ VoIP' : '📱 Мобильный'}}</div>
          </div>
        </div>
      </div>
    `;

  // 7. CLI DIRECT OUTPUT / FALLBACK
  }} else {{
    let logLines = data.raw_cli_output || `[${{nowStr}}] [MODULE] INITIALIZING: ${{safeToolName}}
[${{nowStr}}] [TARGET] "${{target}}"
[${{nowStr}}] [STATUS] EXECUTION COMPLETED`;

    html += `
      <div class="hacker-terminal">
        <div class="term-topbar">
          <div class="term-dots"><span class="term-dot term-dot-green"></span></div>
          <span>${{safeToolName.toUpperCase()}}@STATION:~# scan</span>
          <button class="copy-btn" onclick="copyText(this, \`${{logLines.replace(/`/g, '\\`')}}\`)">📋 Копировать CLI</button>
        </div>
        <div class="term-log-content">${{logLines}}</div>
      </div>
    `;

    if (data.quick_links && data.quick_links.length > 0) {{
      html += `
        <div class="custom-card">
          <div class="custom-card-title"><i class="fa-solid fa-bolt" style="color:var(--cyan);"></i> Прямые ссылки разведки</div>
          <div class="btn-group">
            ${{data.quick_links.map(q => `<button onclick="openExternalUrl('${{q.url}}')" class="btn btn-secondary" style="font-size:10px; padding:4px 8px;">🔗 ${{q.name}}</button>`).join('')}}
          </div>
        </div>
      `;
    }}
  }}

  outBox.innerHTML = html;
}}

// ИНТЕРАКТИВНЫЙ VIS.JS ГРАФ СВЯЗЕЙ
async function runGraphDirectScan() {{
  const target = document.getElementById('graphTargetInput').value.trim();
  const loader = document.getElementById('graphLoader');
  const box = document.getElementById('graphContainerBox');

  if (!target) {{
    alert('Введите цель для построения графа');
    return;
  }}

  loader.style.display = 'block';
  box.style.display = 'none';

  try {{
    const res = await fetch('/api/scan/autorecon', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
      body: JSON.stringify({{ target, caller: currentSessionUser }})
    }});
    const data = await res.json();
    loader.style.display = 'none';
    box.style.display = 'block';
    lastAutoReconData = data;

    renderInteractiveVisGraph(data.nodes || [], data.edges || []);
    document.getElementById('graphDossierContent').innerText = data.ai_dossier || 'Досье сформировано.';
  }} catch (err) {{
    loader.style.display = 'none';
    alert('Ошибка построения графа: ' + err.message);
  }}
}}

function renderInteractiveVisGraph(nodes, edges) {{
  const container = document.getElementById('visNetworkCanvas');
  if (!container) return;

  const data = {{
    nodes: new vis.DataSet(nodes),
    edges: new vis.DataSet(edges)
  }};

  const options = {{
    physics: {{
      stabilization: true,
      barnesHut: {{ gravitationalConstant: -3000, springLength: 100, springConstant: 0.04 }}
    }},
    interaction: {{ hover: true, navigationButtons: true, keyboard: true }},
    nodes: {{ borderWidth: 2, shadow: true, font: {{ color: '#ffffff', face: 'monospace' }} }},
    edges: {{ width: 1.5, shadow: true, font: {{ color: '#94a3b8', size: 10, align: 'middle' }} }}
  }};

  visNetworkInstance = new vis.Network(container, data, options);
}}

function exportCurrentGraph() {{
  const canvas = document.querySelector('#visNetworkCanvas canvas');
  if (!canvas) return;
  const link = document.createElement('a');
  link.download = `osint_graph_${{Date.now()}}.png`;
  link.href = canvas.toDataURL();
  link.click();
}}

function printDossierReport() {{
  if (!lastAutoReconData) {{
    alert('Сначала выполните поиск или постройте граф');
    return;
  }}
  const printWin = window.open('', '_blank');
  const d = lastAutoReconData;
  printWin.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>OSINT Report · ${{d.target}}</title>
      <style>
        body {{ font-family: monospace; padding: 25px; background: #fff; color: #000; line-height: 1.5; }}
        h1 {{ border-bottom: 2px solid #000; padding-bottom: 8px; text-transform: uppercase; }}
        .meta {{ margin-bottom: 20px; font-size: 12px; color: #555; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; white-space: pre-wrap; }}
      </style>
    <body onload="window.print()">
      <h1>🛡️ OSINT TACTICAL DOSSIER · PEACE OF THE ISLAND</h1>
      <div class="meta">
        <b>Объект:</b> ${{d.target}} | <b>Дата:</b> ${{new Date().toLocaleString()}} | <b>Оператор:</b> ${{currentSessionUser || 'Investigator'}}
      </div>
      <h2>1. Сводный аналитический отчет</h2>
      <pre>${{d.ai_dossier || 'Нет данных'}}</pre>
      <h2>2. Идентифицированные цифровые узлы (${{(d.nodes || []).length}})</h2>
      <ul>
        ${{(d.nodes || []).map(n => `<li><b>${{n.label}}</b> [${{n.group || 'Node'}}]</li>`).join('')}}
      </ul>
    </body>
    </html>
  `);
  printWin.document.close();
}}

// ДЕКОДЕРЫ
async function runDecoderAction(action) {{
  const input = document.getElementById('decoderInputData').value.trim();
  const resBox = document.getElementById('decoderResultBox');
  const outPre = document.getElementById('decoderOutputPre');

  if (!input) {{
    alert('Введите строку или хеш');
    return;
  }}

  try {{
    const res = await fetch('/api/tools/decode', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ action, data: input }})
    }});
    const data = await res.json();
    resBox.style.display = 'block';

    if (data.action === 'hash_id') {{
      outPre.innerText = `[HASH IDENTIFIER REPORT]\nДлина: ${{data.length}} символов\nАлгоритмы:\n${{(data.possible_algorithms || []).map(a => `  • ${{a}}`).join('\\n')}}`;
    }} else if (data.action === 'jwt_decode') {{
      outPre.innerText = `[JWT STRUCTURE]\nHEADER:\n${{JSON.stringify(data.header, null, 2)}}\nPAYLOAD:\n${{JSON.stringify(data.payload, null, 2)}}`;
    }} else {{
      outPre.innerText = data.result || JSON.stringify(data, null, 2);
    }}
  }} catch (e) {{
    resBox.style.display = 'block';
    outPre.innerText = 'Ошибка: ' + e.message;
  }}
}}

// ТЕРМИНАЛ
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

  outputEl.innerText += `\nroot@cyberhub:~# ${{cmdRaw}}\n`;

  const parts = cmdRaw.split(/\s+/);
  const cmd = parts[0].toLowerCase();
  const arg = parts.slice(1).join(' ');

  if (cmd === 'help') {{
    outputEl.innerText += `AVAILABLE COMMANDS:\n  help, autorecon <target>, crypto <addr>, dorks <query>, sherlock <user>, wayback <url>, crtsh <domain>, github <user>, phone <num>, hash <str>, clear, matrix\n`;
  }} else if (cmd === 'clear') {{
    outputEl.innerText = `peace of the island of sor/ber peoples · Terminal Cleared\n`;
  }} else if (cmd === 'matrix') {{
    toggleMatrix();
    outputEl.innerText += `[+] Matrix Rain FX: ${{matrixActive ? 'ENABLED' : 'DISABLED'}}\n`;
  }} else if (cmd === 'crypto' && arg) {{
    try {{
      const res = await fetch('/api/scan/crypto', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
        body: JSON.stringify({{ target: arg, caller: currentSessionUser }})
      }});
      const data = await res.json();
      outputEl.innerText += (data.raw_cli_output || JSON.stringify(data.data, null, 2)) + `\n`;
    }} catch (e) {{ outputEl.innerText += '[-] Error: ' + e.message + `\n`; }}
  }} else if (cmd === 'dorks' && arg) {{
    try {{
      const res = await fetch('/api/tools/dorks', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ target: arg }})
      }});
      const data = await res.json();
      outputEl.innerText += (data.raw_cli_output || 'Dorks generated.') + `\n`;
    }} catch (e) {{ outputEl.innerText += '[-] Error: ' + e.message + `\n`; }}
  }} else if (arg) {{
    try {{
      const res = await fetch('/api/scan/universal', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
        body: JSON.stringify({{ tool_id: cmd, target: arg, caller: currentSessionUser }})
      }});
      const data = await res.json();
      outputEl.innerText += (data.raw_cli_output || `[✓] Finished scan for '${{arg}}'.`) + `\n`;
    }} catch (e) {{ outputEl.innerText += '[-] Error: ' + e.message + `\n`; }}
  }} else {{
    outputEl.innerText += `[-] Unknown command: '${{cmd}}'. Type 'help'.\n`;
  }}
  outputEl.scrollTop = outputEl.scrollHeight;
}}

// ФОТО ОБРАБОТКА
function handlePhotoDrop(e, inputId) {{
  e.preventDefault();
  if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {{
    const fileInput = document.getElementById(inputId);
    fileInput.files = e.dataTransfer.files;
    if (inputId === 'tvFileInput') handlePhotoUpload(fileInput);
    else processDirectPhoto(fileInput);
  }}
}}

async function handlePhotoUpload(input) {{
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];
  const preview = document.getElementById('tvPhotoPreview');
  const loader = document.getElementById('tvLoader');
  const outBox = document.getElementById('tvOutputBox');

  loader.style.display = 'block';
  outBox.style.display = 'none';

  const reader = new FileReader();
  reader.onload = async function(e) {{
    preview.src = e.target.result;
    preview.style.display = 'block';
    try {{
      const res = await fetch('/api/scan/photo', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
        body: JSON.stringify({{ image_base64: e.target.result }})
      }});
      const data = await res.json();
      loader.style.display = 'none';
      outBox.style.display = 'block';
      renderPhotoSpecificCard(data, outBox);
    }} catch (err) {{
      loader.style.display = 'none';
      outBox.style.display = 'block';
      outBox.innerHTML = `<div style="color:var(--danger);">❌ Ошибка: ${{err.message}}</div>`;
    }}
  }};
  reader.readAsDataURL(file);
}}

async function processDirectPhoto(input) {{
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];
  const preview = document.getElementById('directPhotoPreview');
  const loader = document.getElementById('photoLoader');
  const outBox = document.getElementById('photoResultBox');

  loader.style.display = 'block';
  outBox.innerHTML = '';

  const reader = new FileReader();
  reader.onload = async function(e) {{
    preview.src = e.target.result;
    preview.style.display = 'block';
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
      outBox.innerHTML = `<div style="color:var(--danger);">❌ Ошибка: ${{err.message}}</div>`;
    }}
  }};
  reader.readAsDataURL(file);
}}

function renderPhotoSpecificCard(data, container) {{
  const exif = data.exif || {{}};
  let hasGps = !!exif.gps;
  let html = `
    <div class="custom-card">
      <div class="custom-card-title"><i class="fa-solid fa-camera" style="color:var(--cyan);"></i> Извлеченные метаданные снимка</div>
      <div class="custom-grid">
        <div class="custom-item">
          <div class="custom-label">📷 Камера</div>
          <div class="custom-val">${{exif.camera_make || ''}} ${{exif.camera_model || '—'}}</div>
        </div>
        <div class="custom-item">
          <div class="custom-label">🕒 Дата</div>
          <div class="custom-val">${{exif.date_time || 'Скрыта'}}</div>
        </div>
        <div class="custom-item" style="grid-column: span 2;">
          <div class="custom-label">📍 GPS Координаты</div>
          <div class="custom-val">
            ${{hasGps ? `<span style="color:var(--primary);">📍 ${{exif.gps.latitude}}, ${{exif.gps.longitude}}</span> <button onclick="openExternalUrl('${{exif.google_maps_url}}')" class="btn btn-primary" style="padding:2px 6px; font-size:10px; margin-left:6px;">Карты</button>` : 'Координаты отсутствуют'}}
          </div>
        </div>
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

  if (!target) {{ alert('Введите юзернейм'); return; }}

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
    outBox.innerHTML = `<div style="color:var(--danger);">❌ Ошибка: ${{err.message}}</div>`;
  }}
}}

function renderAttributionOutput(data, container) {{
  const mutations = data.candidate_mutations || [];
  let html = `
    <div class="custom-card" style="border-color:var(--purple);">
      <div class="custom-card-title" style="color:var(--purple);"><i class="fa-solid fa-user-secret"></i> Результат атрибуции вирта</div>
      <div class="custom-grid">
        <div class="custom-item">
          <div class="custom-label">🎯 Вирт</div>
          <div class="custom-val">@${{data.target}}</div>
        </div>
        <div class="custom-label">🔍 Вероятная основа</div>
        <div class="custom-val" style="color:var(--primary);">${{data.root_handle ? '@' + data.root_handle : 'Скрыта'}}</div>
      </div>
    </div>
  `;
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
  tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:8px;">Загрузка...</td></tr>';

  try {{
    const res = await fetch('/api/admin/users', {{ headers: {{ 'X-Telegram-User-Id': tgUserId }} }});
    const data = await res.json();
    const users = data.users || [];

    tbody.innerHTML = '';
    users.forEach(u => {{
      const tr = document.createElement('tr');
      const statusTxt = u.status === 'active' ? '<span style="color:var(--primary); font-weight:700;">🟢 АКТИВЕН</span>' : '<span style="color:var(--danger); font-weight:700;">🔴 БЛОК</span>';
      const tgInfo = u.tg_username ? `@${{u.tg_username}}` : (u.tg_id ? `ID:${{u.tg_id}}` : '—');
      const twinkTxt = u.is_twink ? '<span style="color:var(--danger); font-weight:800;">⚠️ Твинк</span>' : '<span style="color:var(--primary);">Чисто</span>';
      const quotaDisplay = u.is_unlimited ? '<span style="color:#facc15; font-weight:800;">👑 VIP</span>' : `<b>${{u.scan_balance}}</b> ост.`;

      tr.innerHTML = `
        <td><b>${{u.nickname || u.username}}</b></td>
        <td style="font-size:10px; color:var(--cyan);">${{tgInfo}}</td>
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
    tbody.innerHTML = '<tr><td colspan="7" style="color:var(--danger); text-align:center;">Ошибка загрузки</td></tr>';
  }}
}}

async function adminSetQuota(username, amount, mode) {{
  if (!isUserAdmin) return;
  try {{
    const res = await fetch('/api/admin/user/set-quota', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
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

async function submitCreateUser() {{
  if (!isUserAdmin) return;
  const username = document.getElementById('newUsername').value.trim();
  const password = document.getElementById('newPassword').value.trim();
  const role = document.getElementById('newRole').value;
  const notes = document.getElementById('newNotes').value.trim();

  if (!username) {{ alert('Укажите позывной'); return; }}

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
    }} else {{ alert('Ошибка: ' + data.error); }}
  }} catch (e) {{ alert('Ошибка: ' + e.message); }}
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
      <button class="copy-btn" onclick="copyText(this, \`${{cmd.replace(/`/g, '\\\\`')}}\`)">Копировать</button>
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


// ЗАПУСК ГЛАВНОГО AI PROFILER С ПЕРВОГО ЭКРАНА
async function runMainAiProfilerScan() {{
  const target = (input ? input.value : '').trim();
  if (!target) {{
    alert('Введите никнейм или цель для AI-профайлинга');
  }}
  openToolPage('ai_detective_profiler');
  document.getElementById('tvTargetInput').value = target;
}}


function setOmniTarget(val) {{
  const inp = document.getElementById('searchInput');
  if (inp) {{
    inp.value = val;
    renderCatalog();
  }}
}}

async function runMainOmniSearch() {{
  const inp = document.getElementById('searchInput');
  const query = (inp ? inp.value : '').trim();
  if (!query) {{
    alert('Введите никнейм, кошелек или цель для сканирования');
    return;
  }}

  let matchingTool = null;
  FULL_CATALOG.forEach(g => {{
    g.tools.forEach(t => {{
      if (t.id.toLowerCase() === query.toLowerCase() || t.name.toLowerCase().includes(query.toLowerCase())) {{
        matchingTool = t;
      }}
    }});
  }});

  if (matchingTool) {{
    openToolPage(matchingTool.id);
    return;
  }}

  openToolPage('ai_detective_profiler');
  document.getElementById('tvTargetInput').value = query;
  executeToolScan('ai_detective_profiler', query);
}}


let isUserAdmin = false;

function openAdminPanel() {{
  showView('usersAdminView');
  loadAdminUsers();
  loadAdminVisitors();
}}

function handleUserBadgeClick() {{
  if (isUserAdmin) {{
    openAdminPanel();
  }} else {{
    openStarsModal();
  }}
}}

async function initUserProfile() {{
  try {{
    const res = await fetch('/api/user/profile', {{
      headers: {{ 'X-Telegram-User-Id': tgUserId }}
    }});
    const data = await res.json();
    
    if (data.status === 'blocked') {{
      showView('blockedView');
      return;
    }}

    if (!data.registered) {{
      showView('registerView');
      return;
    }}

    currentSessionUser = data.nickname || data.username || 'agent';
    
    // Проверка прав администратора
    if (data.role === 'admin' || data.is_admin || tgUserId === '5233450569' || currentSessionUser.toLowerCase() === 'admin') {{
      isUserAdmin = true;
      const adminBtn = document.getElementById('navAdminBtn');
      if (adminBtn) adminBtn.style.display = 'inline-flex';
    }}

    const uBadge = document.getElementById('currentUserBadge');
    if (uBadge) {{
      uBadge.style.display = 'inline-flex';
      const nameSpan = document.getElementById('currentUsernameSpan');
      if (nameSpan) nameSpan.innerText = isUserAdmin ? `${{currentSessionUser}} [👑]` : currentSessionUser;
      const icon = document.getElementById('userBadgeIcon');
      if (icon && isUserAdmin) {{
        icon.className = 'fa-solid fa-crown';
        icon.style.color = '#facc15';
      }}
    }}

    const qSpan = document.getElementById('quotaSpan');
    if (qSpan) {{
      qSpan.innerText = (data.is_unlimited || isUserAdmin) ? '👑 VIP (∞)' : `${{data.scan_balance !== undefined ? data.scan_balance : 5}} Запросов`;
    }}
  }} catch (err) {{
    console.warn('Profile init:', err);
    // Авто-определение админа по ID при сетевом сбое
    if (tgUserId === '5233450569') {{
      isUserAdmin = true;
      const adminBtn = document.getElementById('navAdminBtn');
      if (adminBtn) adminBtn.style.display = 'inline-flex';
    }}
  }}
}}

async function doRegister() {{
  const nick = document.getElementById('regNicknameInput').value.trim();
  const msg = document.getElementById('regStatusMsg');
  if (!nick || nick.length < 2) {{
    msg.style.display = 'block';
    msg.innerText = 'Позывной должен содержать минимум 2 символа';
    return;
  }}

  try {{
    const res = await fetch('/api/user/register', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-Telegram-User-Id': tgUserId }},
      body: JSON.stringify({{ nickname: nick }})
    }});
    const data = await res.json();
    if (data.ok) {{
      currentSessionUser = nick;
      initUserProfile();
      showView('catalogView');
    }} else {{
      msg.style.display = 'block';
      msg.innerText = data.error || 'Ошибка регистрации';
    }}
  }} catch (e) {{
    msg.style.display = 'block';
    msg.innerText = 'Ошибка соединения: ' + e.message;
  }}
}}

// СТАРТ ПРИЛОЖЕНИЯ
renderCatalog();
initUserProfile();

</script>
</body>
</html>
"""