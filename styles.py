"""
NOVA — styles.py
CSS premium dividido en secciones. Importado por config.py.
"""

# ── 1. BASE: fuente, fondo, layout, scrollbar, hide elements ───
_CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background: linear-gradient(160deg, #0a0e1a 0%, #0d1224 100%) !important;
    color: #f1f5f9 !important;
}
.stApp { background: linear-gradient(160deg, #0a0e1a 0%, #0d1224 100%) !important; min-height: 100vh; }
.main .block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; max-width: 1400px !important; }
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden !important; display: none !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.3); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: rgba(59,130,246,0.55); }

hr { border: none !important; border-top: 1px solid rgba(255,255,255,0.08) !important; margin: 16px 0 !important; }
"""

# ── 2. SIDEBAR: fondo, logo, nav buttons, scrollbar fino ──────
_CSS_SIDEBAR = """
[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
[data-testid="stSidebar"] ::-webkit-scrollbar { width: 3px; }
[data-testid="stSidebar"] ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); }

.nova-logo {
    background: linear-gradient(135deg, #1a2035 0%, #0f1729 100%);
    border-bottom: 1px solid rgba(59,130,246,0.18);
    padding: 22px 18px 18px; text-align: center; margin-bottom: 6px;
}
.nova-logo h1 {
    font-size: 1.55rem !important; font-weight: 800 !important;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
    -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
    margin: 0 0 4px 0 !important;
}
.nova-logo p { font-size: 0.72rem !important; color: #64748b !important; margin: 0 !important; }
.nova-logo-img { max-height: 52px; max-width: 150px; object-fit: contain; border-radius: 8px; margin-bottom: 8px; }

[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; color: #94a3b8 !important;
    border: none !important; border-radius: 10px !important;
    font-size: 0.88rem !important; font-weight: 500 !important;
    padding: 9px 14px !important; width: 100% !important;
    text-align: left !important; justify-content: flex-start !important;
    box-shadow: none !important; transition: all 0.18s ease !important; margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(59,130,246,0.1) !important; color: #93c5fd !important;
    transform: none !important; box-shadow: none !important;
}

.nav-active {
    background: rgba(59,130,246,0.15) !important;
    border: 1px solid rgba(59,130,246,0.3) !important;
    border-left: 3px solid #3b82f6 !important;
    border-radius: 10px; padding: 9px 14px; margin-bottom: 4px;
    font-size: 0.9rem; font-weight: 600; color: #93c5fd;
}
"""

# ── 3. CARDS, KPI, MODULE HEADER ─────────────────────────────
_CSS_CARDS = """
.card {
    background: #1a2035; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 22px 24px; margin-bottom: 16px;
    transition: border-color 0.2s ease;
}
.card:hover { border-color: rgba(59,130,246,0.22); }
.card-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }

.kpi-card {
    background: linear-gradient(135deg, #1a2035, #1e2744);
    border: 1px solid rgba(59,130,246,0.2); border-radius: 16px;
    padding: 20px 16px; text-align: center; position: relative; overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(0,0,0,0.45); border-color: rgba(59,130,246,0.35); }
.kpi-card-accent { position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 16px 16px 0 0; }
.kpi-icon  { font-size: 1.8rem; margin-bottom: 8px; }
.kpi-num   { font-size: 2.4rem; font-weight: 800; color: #3b82f6; line-height: 1; font-family: 'Inter', sans-serif; }
.kpi-label { font-size: 0.72rem; color: #94a3b8; margin-top: 6px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; }

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a2035, #1e2744) !important;
    border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 16px !important;
    padding: 18px 16px !important; box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stMetric"]:hover { transform: translateY(-2px) !important; box-shadow: 0 12px 32px rgba(0,0,0,0.45) !important; }
[data-testid="stMetricLabel"] > div { color: #94a3b8 !important; font-size: 0.75rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.7px !important; }
[data-testid="stMetricValue"] > div { color: #3b82f6 !important; font-size: 2.1rem !important; font-weight: 800 !important; }

.module-header {
    background: linear-gradient(135deg, #1a2035, #0f1729);
    border-left: 4px solid #3b82f6; border-radius: 0 14px 14px 0;
    padding: 18px 24px; margin-bottom: 24px; position: relative; overflow: hidden;
}
.module-header::before {
    content: ''; position: absolute; right: 0; top: 0; bottom: 0; width: 35%;
    background: radial-gradient(ellipse at right center, rgba(59,130,246,0.07) 0%, transparent 70%);
    pointer-events: none;
}
.module-header h2 { margin: 0; font-size: 1.35rem; font-weight: 800; color: #f1f5f9; }
.module-header p  { margin: 4px 0 0; font-size: 0.83rem; color: #64748b; }
"""

# ── 4. INPUTS, SELECTS, BOTONES ───────────────────────────────
_CSS_FORMS = """
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #ffffff !important; color: #111111 !important;
    border: 1px solid rgba(59,130,246,0.35) !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.92rem !important;
    caret-color: #111111 !important; transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #3b82f6 !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.18) !important;
}
.stTextInput > div > div > input::placeholder,
.stNumberInput > div > div > input::placeholder { color: #9ca3af !important; }

.stTextArea > div > div > textarea {
    background: #ffffff !important; color: #111111 !important;
    border: 1px solid rgba(59,130,246,0.35) !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.92rem !important;
    caret-color: #111111 !important; transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextArea > div > div > textarea:focus {
    border-color: #3b82f6 !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.18) !important;
}
.stTextArea > div > div > textarea::placeholder { color: #9ca3af !important; }

.stTextInput > label, .stTextArea > label, .stSelectbox > label,
.stNumberInput > label, .stDateInput > label, .stFileUploader > label,
.stRadio > label, .stCheckbox > label, .stMultiSelect > label {
    color: #94a3b8 !important; font-size: 0.82rem !important; font-weight: 500 !important; margin-bottom: 4px !important;
}

.stSelectbox > div > div {
    background: #1a2035 !important; color: #f1f5f9 !important;
    border: 1px solid rgba(59,130,246,0.3) !important; border-radius: 8px !important;
}
.stSelectbox > div > div > div { color: #f1f5f9 !important; }
[data-baseweb="select"] ul { background: #1a2035 !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 10px !important; }
[data-baseweb="select"] li { color: #f1f5f9 !important; font-size: 0.88rem !important; }
[data-baseweb="select"] li:hover { background: rgba(59,130,246,0.15) !important; }
[data-baseweb="select"] [aria-selected="true"] { background: rgba(59,130,246,0.2) !important; }

.stDateInput > div > div > input {
    background: #ffffff !important; color: #111111 !important;
    border: 1px solid rgba(59,130,246,0.3) !important; border-radius: 8px !important;
}

.stRadio > div { gap: 6px !important; }
.stRadio > div > label {
    background: #1a2035; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 6px 14px !important;
    color: #94a3b8 !important; font-size: 0.88rem !important; transition: all 0.15s ease; cursor: pointer;
}
.stRadio > div > label:has(input:checked) {
    background: rgba(59,130,246,0.15) !important;
    border-color: rgba(59,130,246,0.4) !important; color: #93c5fd !important;
}

[data-testid="stFileUploader"] {
    background: #1a2035 !important; border: 2px dashed rgba(59,130,246,0.35) !important;
    border-radius: 12px !important; padding: 12px !important; transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: rgba(59,130,246,0.6) !important; }
"""

# ── 5. BOTONES ────────────────────────────────────────────────
_CSS_BUTTONS = """
.main .stButton > button,
[data-testid="column"] .stButton > button,
[data-testid="stForm"] .stButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: #ffffff !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.9rem !important;
    font-family: 'Inter', sans-serif !important; padding: 10px 20px !important;
    width: 100% !important; transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(59,130,246,0.3) !important; letter-spacing: 0.2px !important;
}
.main .stButton > button:hover,
[data-testid="column"] .stButton > button:hover,
[data-testid="stForm"] .stButton > button:hover {
    background: linear-gradient(135deg, #60a5fa, #3b82f6) !important;
    transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(59,130,246,0.42) !important;
}
.main .stButton > button:active { transform: translateY(0) !important; }

.btn-danger  .stButton > button { background: linear-gradient(135deg,#ef4444,#dc2626) !important; box-shadow: 0 4px 12px rgba(239,68,68,0.3) !important; }
.btn-danger  .stButton > button:hover { background: linear-gradient(135deg,#f87171,#ef4444) !important; transform: translateY(-1px) !important; }
.btn-success .stButton > button { background: linear-gradient(135deg,#10b981,#059669) !important; box-shadow: 0 4px 12px rgba(16,185,129,0.3) !important; }
.btn-success .stButton > button:hover { background: linear-gradient(135deg,#34d399,#10b981) !important; transform: translateY(-1px) !important; }
.btn-warning .stButton > button { background: linear-gradient(135deg,#f59e0b,#d97706) !important; box-shadow: 0 4px 12px rgba(245,158,11,0.3) !important; }
.btn-warning .stButton > button:hover { background: linear-gradient(135deg,#fbbf24,#f59e0b) !important; transform: translateY(-1px) !important; }
.btn-ghost   .stButton > button { background: rgba(255,255,255,0.06) !important; box-shadow: none !important; border: 1px solid rgba(255,255,255,0.12) !important; color: #94a3b8 !important; }
.btn-ghost   .stButton > button:hover { background: rgba(255,255,255,0.1) !important; transform: none !important; box-shadow: none !important; }
"""

# ── 6. TABLAS, BADGES, DATAFRAME ──────────────────────────────
_CSS_DATA = """
.tabla-row {
    background: #1a2035; border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px; padding: 11px 15px; margin-bottom: 7px; transition: all 0.15s ease;
}
.tabla-row:hover { background: #1e2744; border-color: rgba(59,130,246,0.25); }
.tabla-row:nth-child(even) { background: #1c2340; }

.badge { display: inline-flex; align-items: center; border-radius: 99px; padding: 3px 11px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.3px; }
.badge-abierto  { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.35); }
.badge-proceso  { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.35); }
.badge-resuelto { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.35); }
.badge-alta     { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.35); }
.badge-media    { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.35); }
.badge-baja     { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.35); }
.badge-azul     { background: rgba(59,130,246,0.15); color: #93c5fd; border: 1px solid rgba(59,130,246,0.35); }
.badge-purpura  { background: rgba(139,92,246,0.15); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.35); }
.badge-cyan     { background: rgba(6,182,212,0.15);  color: #67e8f9; border: 1px solid rgba(6,182,212,0.35); }

[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.07) !important; }
.dvn-scroller { background: #1a2035 !important; }
[data-testid="stDataFrame"] th { background: #111827 !important; color: #94a3b8 !important; font-size: 0.78rem !important; font-weight: 600 !important; text-transform: uppercase !important; }
[data-testid="stDataFrame"] td { color: #f1f5f9 !important; font-size: 0.87rem !important; border-color: rgba(255,255,255,0.05) !important; }
"""

# ── 7. COMPONENTES: tabs, expander, alerts, kanban, ping, mobile
_CSS_COMPONENTS = """
.stTabs [data-baseweb="tab-list"] { background: #111827; border-radius: 10px; padding: 4px; gap: 2px; border: 1px solid rgba(255,255,255,0.06); }
.stTabs [data-baseweb="tab"] { background: transparent; border-radius: 8px; color: #64748b; font-weight: 500; font-size: 0.88rem; transition: all 0.15s ease; }
.stTabs [aria-selected="true"] { background: #1a2035 !important; color: #f1f5f9 !important; }

.stExpander { background: #1a2035 !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 12px !important; }
.stExpander > details > summary { color: #94a3b8 !important; font-size: 0.9rem !important; }
.stExpander > details > summary:hover { color: #f1f5f9 !important; }

.stAlert { border-radius: 10px !important; font-size: 0.9rem !important; }
[data-testid="stSuccess"] { background: rgba(16,185,129,0.1) !important; border: 1px solid rgba(16,185,129,0.3) !important; border-radius: 10px !important; }
[data-testid="stError"]   { background: rgba(239,68,68,0.1) !important;  border: 1px solid rgba(239,68,68,0.3) !important;  border-radius: 10px !important; }
[data-testid="stWarning"] { background: rgba(245,158,11,0.1) !important; border: 1px solid rgba(245,158,11,0.3) !important; border-radius: 10px !important; }
[data-testid="stInfo"]    { background: rgba(59,130,246,0.1) !important; border: 1px solid rgba(59,130,246,0.3) !important; border-radius: 10px !important; }

.kanban-col { background: rgba(26,32,53,0.6); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 14px; min-height: 280px; }
.kanban-header { font-size: 0.85rem; font-weight: 700; text-align: center; padding: 8px; border-radius: 8px; margin-bottom: 12px; }
.kanban-card { background: #1a2035; border: 1px solid rgba(255,255,255,0.09); border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; border-left: 3px solid; transition: all 0.2s ease; }
.kanban-card:hover { background: #1e2744; transform: translateX(2px); }

.stock-bar-wrap { background: rgba(255,255,255,0.07); border-radius: 99px; height: 7px; overflow: hidden; margin: 6px 0; }
.stock-bar-fill { height: 100%; border-radius: 99px; transition: width 0.5s ease; }

@keyframes ping { 0%{transform:scale(1);opacity:1} 75%,100%{transform:scale(2.2);opacity:0} }
.ping { display: inline-block; width: 9px; height: 9px; border-radius: 50%; position: relative; margin-right: 6px; vertical-align: middle; }
.ping::after { content:''; position:absolute; inset:0; border-radius:50%; animation: ping 1.3s cubic-bezier(0,0,.2,1) infinite; }
.ping-red    { background: #ef4444; } .ping-red::after    { background: #ef4444; }
.ping-yellow { background: #f59e0b; } .ping-yellow::after { background: #f59e0b; }
.ping-green  { background: #10b981; } .ping-green::after  { background: #10b981; }

@media (max-width: 768px) {
    .main .block-container { padding: 0.8rem 0.8rem 2rem !important; }
    .module-header { padding: 14px 16px; border-radius: 0 10px 10px 0; }
    .module-header h2 { font-size: 1.1rem; }
    .kpi-card { padding: 14px 10px; }
    .kpi-num  { font-size: 1.9rem; }
    .kpi-icon { font-size: 1.5rem; }
    .card { padding: 14px 14px; border-radius: 12px; }
    .badge { font-size: 0.68rem; padding: 2px 8px; }
    [data-testid="stMetricValue"] > div { font-size: 1.7rem !important; }
    .stTabs [data-baseweb="tab"] { font-size: 0.8rem !important; }
}
@media (max-width: 480px) {
    .kpi-num { font-size: 1.6rem; }
    .nova-logo h1 { font-size: 1.3rem !important; }
    .module-header h2 { font-size: 1rem; }
}
"""

# ── CSS_GLOBAL: todo unido ─────────────────────────────────────
CSS_GLOBAL = (
    "<style>"
    + _CSS_BASE
    + _CSS_SIDEBAR
    + _CSS_CARDS
    + _CSS_FORMS
    + _CSS_BUTTONS
    + _CSS_DATA
    + _CSS_COMPONENTS
    + "</style>"
)
