"""
NOVA — config.py
Estilos CSS, constantes de colores, y helpers de componentes UI.
"""
import streamlit as st

# ── Paleta de colores del sistema ─────────────────────────────
COLOR = {
    "bg":        "#0f1117",
    "card":      "rgba(255,255,255,0.05)",
    "primary":   "#4a90e2",
    "success":   "#38a169",
    "danger":    "#e53e3e",
    "warning":   "#d69e2e",
    "info":      "#805ad5",
    "text":      "#e2e8f0",
    "muted":     "#94a3b8",
    "border":    "rgba(255,255,255,0.1)",
    "plot_bg":   "#0f1117",
    "plot_paper":"#1a1f2e",
}

# ── Opciones de negocio ────────────────────────────────────────
CATEGORIAS_TAREA = [
    "Eléctrico", "Plomería", "AC-Climatización", "Equipos AV",
    "Carpintería", "Pintura", "Equipos de Cocina", "Piscina", "General",
]
CATEGORIAS_INVENTARIO = [
    "Focos", "Cables", "Repuestos AC", "Herramientas",
    "Equipos AV", "Materiales Eléctricos", "Plomería", "Limpieza", "Otros",
]
CATEGORIAS_ACTIVOS = [
    "AC/Climatización", "Eléctrico", "Plomería", "Cocina",
    "Audio-Visual", "Seguridad", "Piscina", "General",
]
ESTADOS_TAREA    = ["Abierto", "En Proceso", "Resuelto"]
PRIORIDADES      = ["Alta", "Media", "Baja"]
TIPOS_AREA       = [
    "habitacion", "area_comun", "servicio", "cocina",
    "bar", "restaurante", "piscina", "ingenieria", "administracion", "general",
]
TIPOS_ENERGIA    = ["electricidad", "agua", "gas"]
UNIDADES_ENERGIA = {"electricidad": "kWh", "agua": "m³", "gas": "m³"}

# ── Plotly theme base ──────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor=COLOR["plot_paper"],
    plot_bgcolor=COLOR["plot_bg"],
    font=dict(family="Inter, sans-serif", color=COLOR["text"]),
    xaxis=dict(gridcolor="rgba(255,255,255,0.07)", zerolinecolor="rgba(255,255,255,0.07)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.07)", zerolinecolor="rgba(255,255,255,0.07)"),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=COLOR["text"])),
)
PLOTLY_COLORS = [COLOR["primary"], COLOR["success"], COLOR["danger"],
                 COLOR["warning"], COLOR["info"], "#06b6d4", "#f97316"]


# ── CSS completo del sistema ───────────────────────────────────
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* === RESET & BASE === */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background: #0f1117 !important;
    color: #e2e8f0 !important;
}
.stApp { background: linear-gradient(135deg,#0f1117 0%,#1a1f2e 60%,#0f1117 100%) !important; }

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#141824 0%,#0f1117 100%) !important;
    border-right: 1px solid rgba(74,144,226,0.15) !important;
}
[data-testid="stSidebar"] .stRadio > label { color:#94a3b8 !important; font-size:0.78rem; }
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    font-size:0.95rem !important; padding:6px 0 !important;
}

/* === SIDEBAR LOGO AREA === */
.nova-logo {
    background: linear-gradient(135deg,#1e3a5f,#2d1b69);
    border-radius:14px; padding:18px 16px; margin-bottom:20px;
    border:1px solid rgba(74,144,226,0.3);
    box-shadow: 0 4px 24px rgba(74,144,226,0.15);
    text-align:center;
}
.nova-logo-img { max-height:60px; max-width:100%; object-fit:contain; border-radius:8px; margin-bottom:6px; }
.nova-logo h1 { margin:0; font-size:1.6rem; font-weight:800; color:#fff; letter-spacing:-1px; }
.nova-logo p  { margin:2px 0 0; font-size:0.75rem; color:rgba(255,255,255,0.5); }

/* === KPI CARD === */
.kpi-card {
    background: rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.1);
    border-radius:16px; padding:20px 18px;
    position:relative; overflow:hidden;
    transition: transform .2s ease, box-shadow .2s ease;
    text-align:center;
}
.kpi-card:hover { transform:translateY(-3px); box-shadow:0 12px 32px rgba(0,0,0,0.4); }
.kpi-card-accent { position:absolute; top:0; left:0; right:0; height:3px; border-radius:16px 16px 0 0; }
.kpi-icon  { font-size:2rem; margin-bottom:8px; }
.kpi-num   { font-size:2.2rem; font-weight:800; color:#fff; line-height:1; }
.kpi-label { font-size:0.78rem; color:#94a3b8; margin-top:6px; font-weight:500; text-transform:uppercase; letter-spacing:.5px; }

/* === CARDS GENERALES === */
.card {
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.1);
    border-radius:14px; padding:22px 24px; margin-bottom:18px;
    backdrop-filter:blur(10px); box-shadow:0 4px 24px rgba(0,0,0,0.3);
}
.card-title { font-size:1.05rem; font-weight:700; color:#e2e8f0; margin-bottom:16px; }

/* === KANBAN === */
.kanban-col {
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:14px; padding:14px; min-height:300px;
}
.kanban-header { font-size:0.9rem; font-weight:700; text-align:center; padding:8px; border-radius:8px; margin-bottom:12px; }
.kanban-card {
    background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.12);
    border-radius:10px; padding:12px 14px; margin-bottom:10px;
    transition:all .2s ease; border-left:3px solid;
}
.kanban-card:hover { background:rgba(255,255,255,0.1); transform:translateX(2px); }

/* === BADGES === */
.badge {
    display:inline-block; border-radius:20px;
    padding:3px 11px; font-size:0.73rem; font-weight:700; text-transform:uppercase; letter-spacing:.4px;
}
.badge-rojo    { background:rgba(229,62,62,0.2);   color:#fc8181; border:1px solid rgba(229,62,62,0.4); }
.badge-verde   { background:rgba(56,161,105,0.2);  color:#68d391; border:1px solid rgba(56,161,105,0.4); }
.badge-amarillo{ background:rgba(214,158,46,0.2);  color:#f6e05e; border:1px solid rgba(214,158,46,0.4); }
.badge-azul    { background:rgba(74,144,226,0.2);  color:#90cdf4; border:1px solid rgba(74,144,226,0.4); }
.badge-purpura { background:rgba(128,90,213,0.2);  color:#b794f4; border:1px solid rgba(128,90,213,0.4); }

/* === PROGRESS BAR STOCK === */
.stock-bar-wrap { background:rgba(255,255,255,0.08); border-radius:999px; height:8px; overflow:hidden; margin:6px 0; }
.stock-bar-fill { height:100%; border-radius:999px; transition:width .6s ease; }

/* === TABLA CUSTOM === */
.tabla-header { background:rgba(74,144,226,0.1); border-radius:8px 8px 0 0; padding:10px 14px; font-size:0.78rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:.5px; }
.tabla-row    { padding:10px 14px; border-bottom:1px solid rgba(255,255,255,0.06); font-size:0.88rem; transition:background .15s; }
.tabla-row:hover { background:rgba(255,255,255,0.04); }
.tabla-row:last-child { border-bottom:none; }

/* === PING ALERT === */
@keyframes ping { 0%{transform:scale(1);opacity:1} 75%,100%{transform:scale(2);opacity:0} }
.ping { display:inline-block; width:10px; height:10px; border-radius:50%; position:relative; }
.ping::after { content:''; position:absolute; top:0;left:0;right:0;bottom:0; border-radius:50%; animation:ping 1.2s cubic-bezier(0,0,.2,1) infinite; }
.ping-red  { background:#e53e3e; } .ping-red::after  { background:#e53e3e; }
.ping-yellow{background:#d69e2e;} .ping-yellow::after{background:#d69e2e;}

/* === INPUTS === */
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
    background:rgba(255,255,255,0.07) !important; border:1px solid rgba(255,255,255,0.15) !important;
    border-radius:10px !important; color:#e2e8f0 !important; font-family:'Inter',sans-serif !important;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    border-color:#4a90e2 !important; box-shadow:0 0 0 3px rgba(74,144,226,0.2) !important;
}
.stTextInput>label,.stTextArea>label,.stSelectbox>label,.stNumberInput>label,.stDateInput>label {
    color:#94a3b8 !important; font-size:0.83rem !important; font-weight:500 !important;
}

/* === BOTONES === */
.stButton>button {
    background:linear-gradient(135deg,#4a90e2,#357abd) !important;
    color:#fff !important; border:none !important; border-radius:10px !important;
    padding:10px 20px !important; font-weight:600 !important; font-family:'Inter',sans-serif !important;
    transition:all .2s ease !important; box-shadow:0 4px 15px rgba(74,144,226,0.3) !important;
    width:100% !important;
}
.stButton>button:hover { transform:translateY(-1px) !important; box-shadow:0 6px 20px rgba(74,144,226,0.45) !important; }
.btn-danger .stButton>button  { background:linear-gradient(135deg,#e53e3e,#c53030) !important; box-shadow:0 4px 15px rgba(229,62,62,0.3) !important; }
.btn-success .stButton>button { background:linear-gradient(135deg,#38a169,#2f855a) !important; box-shadow:0 4px 15px rgba(56,161,105,0.3) !important; }
.btn-warning .stButton>button { background:linear-gradient(135deg,#d69e2e,#b7791f) !important; box-shadow:0 4px 15px rgba(214,158,46,0.3) !important; }

/* === HERO BANNER === */
.hero-banner {
    background:linear-gradient(135deg,#1e3a5f 0%,#2d1b69 50%,#1a4731 100%);
    border-radius:18px; padding:28px 32px; margin-bottom:24px;
    border:1px solid rgba(74,144,226,0.25); position:relative; overflow:hidden;
}
.hero-banner::before {
    content:''; position:absolute; top:-50%; right:-10%; width:300px; height:300px;
    background:radial-gradient(circle,rgba(74,144,226,0.15) 0%,transparent 70%); border-radius:50%;
}
.hero-banner h2 { margin:0; font-size:1.4rem; font-weight:800; color:#fff; }
.hero-banner p  { margin:4px 0 0; color:rgba(255,255,255,0.6); font-size:0.88rem; }

/* === MISC === */
hr { border:none !important; border-top:1px solid rgba(255,255,255,0.1) !important; margin:18px 0 !important; }
.stAlert { border-radius:10px !important; }
#MainMenu,footer,header,.stDeployButton { visibility:hidden; display:none; }
.stExpander { background:rgba(255,255,255,0.03) !important; border:1px solid rgba(255,255,255,0.1) !important; border-radius:12px !important; }
[data-testid="stMetricValue"] { font-size:2rem !important; color:#fff !important; }

/* === MOBILE === */
@media(max-width:768px){
    .hero-banner{padding:18px 16px;}
    .kpi-card{padding:14px 12px;}
    .kpi-num{font-size:1.7rem;}
    .card{padding:14px 16px;}
}
</style>
""", unsafe_allow_html=True)


# ── Helpers de UI ──────────────────────────────────────────────

def badge_estado(estado: str) -> str:
    """Retorna HTML de badge según estado de tarea/pendiente."""
    mapa = {
        "Abierto":    ("badge-rojo",     "🔴 Abierto"),
        "En Proceso": ("badge-amarillo", "🟡 En Proceso"),
        "Resuelto":   ("badge-verde",    "🟢 Resuelto"),
        "Operativo":  ("badge-verde",    "🟢 Operativo"),
        "En Reparación":    ("badge-amarillo","🟡 En Reparación"),
        "Fuera de Servicio":("badge-rojo",    "🔴 Fuera de Servicio"),
    }
    cls, label = mapa.get(estado, ("badge-azul", estado))
    return f'<span class="badge {cls}">{label}</span>'


def badge_prioridad(prioridad: str) -> str:
    """Retorna HTML de badge según prioridad."""
    mapa = {
        "Alta":  ("badge-rojo",     "🔴 Alta"),
        "Media": ("badge-amarillo", "🟡 Media"),
        "Baja":  ("badge-verde",    "🔵 Baja"),
    }
    cls, label = mapa.get(prioridad, ("badge-azul", prioridad))
    return f'<span class="badge {cls}">{label}</span>'


def kpi_card(icono: str, numero, label: str, color: str = "#4a90e2"):
    """Renderiza una KPI card con acento de color."""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-card-accent" style="background:{color};"></div>
        <div class="kpi-icon">{icono}</div>
        <div class="kpi-num">{numero}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def seccion_titulo(icono: str, titulo: str, subtitulo: str = ""):
    """Header de sección con gradiente."""
    sub = f'<p>{subtitulo}</p>' if subtitulo else ""
    st.markdown(f"""
    <div class="hero-banner">
        <h2>{icono} {titulo}</h2>
        {sub}
    </div>
    """, unsafe_allow_html=True)


def stock_bar(actual: float, minimo: float) -> str:
    """Barra de progreso de stock con color según nivel."""
    if minimo <= 0:
        pct = 100
        color = "#38a169"
    else:
        pct = min(100, (actual / minimo) * 100)
        color = "#38a169" if pct >= 100 else ("#d69e2e" if pct >= 50 else "#e53e3e")
    return f"""
    <div class="stock-bar-wrap">
        <div class="stock-bar-fill" style="width:{pct:.0f}%;background:{color};"></div>
    </div>
    <span style="font-size:0.75rem;color:#94a3b8;">{actual:.0f} / mín {minimo:.0f}</span>
    """


def separador():
    st.markdown('<hr>', unsafe_allow_html=True)
