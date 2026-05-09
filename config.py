"""
NOVA — config.py  (v2 — rediseño completo)
CSS premium oscuro, constantes, helpers de UI.
"""
import streamlit as st

# ── Paleta de colores v2 ───────────────────────────────────────
COLOR = {
    "bg":         "#0a0e1a",
    "bg2":        "#111827",
    "card":       "#1a2035",
    "card_hover": "#1e2744",
    "primary":    "#3b82f6",
    "success":    "#10b981",
    "danger":     "#ef4444",
    "warning":    "#f59e0b",
    "info":       "#8b5cf6",
    "text":       "#f1f5f9",
    "muted":      "#94a3b8",
    "dim":        "#64748b",
    "border":     "rgba(255,255,255,0.08)",
    "border_acc": "rgba(59,130,246,0.4)",
    "plot_bg":    "rgba(26,32,53,0.5)",
    "plot_paper": "rgba(0,0,0,0)",
}

# ── Opciones de negocio ────────────────────────────────────────
CATEGORIAS_TAREA = [
    "Eléctrico", "Plomería", "AC-Climatización", "Equipos AV",
    "Carpintería", "Pintura", "Equipos de Cocina", "Piscina", "General", "Otro",
]
CATEGORIAS_INVENTARIO = [
    "Focos", "Cables", "Repuestos AC", "Herramientas",
    "Equipos AV", "Materiales Eléctricos", "Plomería", "Limpieza", "Otros",
]
CATEGORIAS_ACTIVOS = [
    "AC/Climatización", "Eléctrico", "Plomería", "Cocina",
    "Audio-Visual", "Seguridad", "Piscina", "General",
]
ESTADOS_TAREA  = ["Abierto", "En Proceso", "Resuelto"]
PRIORIDADES    = ["Alta", "Media", "Baja"]
TIPOS_AREA     = [
    "habitacion", "area_comun", "servicio", "cocina",
    "bar", "restaurante", "piscina", "ingenieria", "administracion", "general",
]
TIPOS_ENERGIA    = ["electricidad", "agua", "gas"]
UNIDADES_ENERGIA = {"electricidad": "kWh", "agua": "m³", "gas": "m³"}

# ── Plotly layout base ─────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=COLOR["plot_paper"],
    plot_bgcolor=COLOR["plot_bg"],
    font=dict(family="Inter, sans-serif", color=COLOR["muted"]),
    title_font=dict(color=COLOR["text"], size=15),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)"),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=COLOR["muted"])),
)
PLOTLY_COLORS = ["#3b82f6", "#10b981", "#ef4444", "#f59e0b", "#8b5cf6", "#06b6d4", "#f97316"]


# ── CSS COMPLETO v2 ────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* === RESET BASE === */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background: #0a0e1a !important;
    color: #f1f5f9 !important;
}
.stApp { background: #0a0e1a !important; }
.main .block-container { padding-top: 1.5rem !important; max-width: 1400px !important; }

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background: #111827 !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

/* === LOGO NOVA === */
.nova-logo {
    background: linear-gradient(135deg, #1a2035 0%, #0f1729 100%);
    border-bottom: 1px solid rgba(59,130,246,0.2);
    padding: 20px 16px 16px;
    text-align: center;
    margin-bottom: 8px;
}
.nova-logo-img {
    max-height: 56px; max-width: 160px; object-fit: contain;
    border-radius: 8px; margin-bottom: 8px;
}
.nova-logo-title {
    font-size: 1.5rem; font-weight: 800; color: #fff;
    background: linear-gradient(135deg,#3b82f6,#8b5cf6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    display: block; margin-bottom: 2px;
}
.nova-logo-sub { font-size: 0.72rem; color: #64748b; }

/* === NAV ITEM ACTIVO === */
.nav-active {
    background: rgba(59,130,246,0.15) !important;
    border: 1px solid rgba(59,130,246,0.3) !important;
    border-radius: 10px; padding: 9px 14px; margin-bottom: 4px;
    border-left: 3px solid #3b82f6 !important;
    font-size: 0.9rem; font-weight: 600; color: #93c5fd;
}

/* === INPUTS — TEXTO NEGRO VISIBLE === */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #ffffff !important;
    color: #000000 !important;
    border: 1px solid rgba(59,130,246,0.35) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    caret-color: #000000 !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.2) !important;
}
.stTextArea > div > div > textarea {
    background: #ffffff !important;
    color: #000000 !important;
    border: 1px solid rgba(59,130,246,0.35) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    caret-color: #000000 !important;
}
.stTextArea > div > div > textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.2) !important;
}
/* Labels */
.stTextInput > label, .stTextArea > label, .stSelectbox > label,
.stNumberInput > label, .stDateInput > label, .stFileUploader > label,
.stRadio > label, .stCheckbox > label {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    margin-bottom: 4px !important;
}

/* === SELECTBOX === */
.stSelectbox > div > div {
    background: #1a2035 !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(59,130,246,0.3) !important;
    border-radius: 8px !important;
}
.stSelectbox > div > div > div { color: #f1f5f9 !important; }
/* Dropdown list items */
[data-baseweb="select"] ul { background: #1a2035 !important; }
[data-baseweb="select"] li { color: #f1f5f9 !important; }
[data-baseweb="select"] li:hover { background: rgba(59,130,246,0.15) !important; }

/* === DATE INPUT === */
.stDateInput > div > div > input {
    background: #ffffff !important;
    color: #000000 !important;
    border: 1px solid rgba(59,130,246,0.3) !important;
    border-radius: 8px !important;
}

/* === BOTONES === */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    font-family: 'Inter', sans-serif !important;
    padding: 10px 20px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(59,130,246,0.3) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #60a5fa, #3b82f6) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(59,130,246,0.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

.btn-danger  .stButton > button { background: linear-gradient(135deg,#ef4444,#dc2626) !important; box-shadow: 0 4px 12px rgba(239,68,68,0.3) !important; }
.btn-danger  .stButton > button:hover { background: linear-gradient(135deg,#f87171,#ef4444) !important; }
.btn-success .stButton > button { background: linear-gradient(135deg,#10b981,#059669) !important; box-shadow: 0 4px 12px rgba(16,185,129,0.3) !important; }
.btn-success .stButton > button:hover { background: linear-gradient(135deg,#34d399,#10b981) !important; }
.btn-warning .stButton > button { background: linear-gradient(135deg,#f59e0b,#d97706) !important; box-shadow: 0 4px 12px rgba(245,158,11,0.3) !important; }
.btn-warning .stButton > button:hover { background: linear-gradient(135deg,#fbbf24,#f59e0b) !important; }
.btn-ghost   .stButton > button { background: rgba(255,255,255,0.06) !important; box-shadow: none !important; border: 1px solid rgba(255,255,255,0.12) !important; }
.btn-ghost   .stButton > button:hover { background: rgba(255,255,255,0.1) !important; }

/* === CARDS === */
.card {
    background: #1a2035;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 22px 24px;
    margin-bottom: 16px;
    transition: border-color 0.2s ease;
}
.card:hover { border-color: rgba(59,130,246,0.2); }
.card-title {
    font-size: 1.02rem; font-weight: 700; color: #f1f5f9;
    margin-bottom: 16px; display: flex; align-items: center; gap: 8px;
}

/* === MODULE HEADER === */
.module-header {
    background: linear-gradient(135deg, #1a2035, #0f1729);
    border-left: 4px solid #3b82f6;
    border-radius: 0 14px 14px 0;
    padding: 18px 24px;
    margin-bottom: 24px;
    position: relative; overflow: hidden;
}
.module-header::after {
    content: ''; position: absolute; right: -30px; top: -30px;
    width: 120px; height: 120px; border-radius: 50%;
    background: radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%);
}
.module-header h2 { margin: 0; font-size: 1.35rem; font-weight: 800; color: #f1f5f9; }
.module-header p  { margin: 4px 0 0; font-size: 0.83rem; color: #64748b; }

/* === KPI CARDS === */
.kpi-card {
    background: linear-gradient(135deg, #1a2035, #1e2744);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 16px;
    padding: 20px 16px;
    text-align: center;
    position: relative; overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(0,0,0,0.4); }
.kpi-card-accent { position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 16px 16px 0 0; }
.kpi-icon  { font-size: 1.8rem; margin-bottom: 8px; }
.kpi-num   { font-size: 2.4rem; font-weight: 800; color: #3b82f6; line-height: 1; font-family: 'Inter', sans-serif; }
.kpi-label { font-size: 0.72rem; color: #94a3b8; margin-top: 6px; font-weight: 600;
             text-transform: uppercase; letter-spacing: 0.8px; }

/* === BADGES === */
.badge { display: inline-block; border-radius: 99px; padding: 3px 11px;
         font-size: 0.72rem; font-weight: 700; }
.badge-abierto  { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.35); }
.badge-proceso  { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.35); }
.badge-resuelto { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.35); }
.badge-alta  { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.35); }
.badge-media { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.35); }
.badge-baja  { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.35); }
.badge-azul  { background: rgba(59,130,246,0.15); color: #93c5fd; border: 1px solid rgba(59,130,246,0.35); }
.badge-purpura { background: rgba(139,92,246,0.15); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.35); }

/* === TABLA ROWS === */
.tabla-row {
    background: #1a2035;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 11px 15px;
    margin-bottom: 7px;
    transition: all 0.15s ease;
}
.tabla-row:hover { background: #1e2744; border-color: rgba(59,130,246,0.25); }

/* === KANBAN === */
.kanban-col {
    background: rgba(26,32,53,0.6);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 14px; min-height: 280px;
}
.kanban-header {
    font-size: 0.85rem; font-weight: 700; text-align: center;
    padding: 8px; border-radius: 8px; margin-bottom: 12px;
}
.kanban-card {
    background: #1a2035;
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 10px; padding: 12px 14px; margin-bottom: 10px;
    border-left: 3px solid; transition: all 0.2s ease;
}
.kanban-card:hover { background: #1e2744; transform: translateX(2px); }

/* === STOCK BAR === */
.stock-bar-wrap { background: rgba(255,255,255,0.07); border-radius: 99px; height: 7px; overflow: hidden; margin: 6px 0; }
.stock-bar-fill { height: 100%; border-radius: 99px; transition: width 0.5s ease; }

/* === PING ALERT === */
@keyframes ping { 0%{transform:scale(1);opacity:1} 75%,100%{transform:scale(2.2);opacity:0} }
.ping { display: inline-block; width: 9px; height: 9px; border-radius: 50%; position: relative; margin-right: 6px; }
.ping::after { content:''; position:absolute; inset:0; border-radius:50%; animation: ping 1.3s cubic-bezier(0,0,.2,1) infinite; }
.ping-red    { background: #ef4444; } .ping-red::after    { background: #ef4444; }
.ping-yellow { background: #f59e0b; } .ping-yellow::after { background: #f59e0b; }

/* === EXPANDER === */
.stExpander {
    background: #1a2035 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
.stExpander > details > summary { color: #94a3b8 !important; }

/* === FILE UPLOADER === */
[data-testid="stFileUploader"] {
    background: #1a2035 !important;
    border: 2px dashed rgba(59,130,246,0.35) !important;
    border-radius: 12px !important;
    padding: 12px !important;
}
[data-testid="stFileUploader"]:hover { border-color: rgba(59,130,246,0.6) !important; }

/* === RADIO === */
.stRadio > div { gap: 6px !important; }
.stRadio > div > label {
    background: #1a2035; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 6px 14px !important;
    color: #94a3b8 !important; font-size: 0.88rem !important;
    transition: all 0.15s ease;
}
.stRadio > div > label:has(input:checked) {
    background: rgba(59,130,246,0.15) !important;
    border-color: rgba(59,130,246,0.4) !important;
    color: #93c5fd !important;
}

/* === TABS === */
.stTabs [data-baseweb="tab-list"] { background: #111827; border-radius: 10px; padding: 4px; gap: 2px; }
.stTabs [data-baseweb="tab"] { background: transparent; border-radius: 8px; color: #64748b; font-weight: 500; font-size: 0.88rem; }
.stTabs [aria-selected="true"] { background: #1a2035 !important; color: #f1f5f9 !important; }

/* === ALERT / SUCCESS / ERROR === */
.stAlert { border-radius: 10px !important; }
.stSuccess { background: rgba(16,185,129,0.1) !important; border: 1px solid rgba(16,185,129,0.3) !important; }
.stError   { background: rgba(239,68,68,0.1) !important; border: 1px solid rgba(239,68,68,0.3) !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border: 1px solid rgba(245,158,11,0.3) !important; }
.stInfo    { background: rgba(59,130,246,0.1) !important; border: 1px solid rgba(59,130,246,0.3) !important; }

/* === HR === */
hr { border: none !important; border-top: 1px solid rgba(255,255,255,0.08) !important; margin: 16px 0 !important; }

/* === HIDE STREAMLIT DEFAULT === */
#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; display: none !important; }

/* === DATAFRAME === */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
.dvn-scroller { background: #1a2035 !important; }

/* === MOBILE === */
@media(max-width: 768px) {
    .module-header { padding: 14px 16px; }
    .module-header h2 { font-size: 1.1rem; }
    .kpi-card { padding: 14px 10px; }
    .kpi-num  { font-size: 1.8rem; }
    .card     { padding: 14px 16px; }
}
</style>
""", unsafe_allow_html=True)


# ── Helpers UI ─────────────────────────────────────────────────

def badge_estado(estado: str) -> str:
    mapa = {
        "Abierto":          ("badge-abierto",  "🔴 Abierto"),
        "En Proceso":       ("badge-proceso",  "🟡 En Proceso"),
        "Resuelto":         ("badge-resuelto", "🟢 Resuelto"),
        "Operativo":        ("badge-resuelto", "🟢 Operativo"),
        "En Reparación":    ("badge-proceso",  "🟡 En Reparación"),
        "Fuera de Servicio":("badge-abierto",  "🔴 Fuera de Servicio"),
    }
    cls, label = mapa.get(estado, ("badge-azul", estado))
    return f'<span class="badge {cls}">{label}</span>'


def badge_prioridad(prioridad: str) -> str:
    mapa = {
        "Alta":  ("badge-alta",  "🔴 Alta"),
        "Media": ("badge-media", "🟡 Media"),
        "Baja":  ("badge-baja",  "🟢 Baja"),
    }
    cls, label = mapa.get(prioridad, ("badge-azul", prioridad))
    return f'<span class="badge {cls}">{label}</span>'


def kpi_card(icono: str, numero, label: str, color: str = "#3b82f6"):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-card-accent" style="background:{color};"></div>
        <div class="kpi-icon">{icono}</div>
        <div class="kpi-num" style="color:{color};">{numero}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def seccion_titulo(icono: str, titulo: str, subtitulo: str = ""):
    sub = f'<p>{subtitulo}</p>' if subtitulo else ""
    st.markdown(f"""
    <div class="module-header">
        <h2>{icono} {titulo}</h2>
        {sub}
    </div>
    """, unsafe_allow_html=True)


def stock_bar(actual: float, minimo: float) -> str:
    if minimo <= 0:
        pct, color = 100, "#10b981"
    else:
        pct   = min(100, (actual / minimo) * 100)
        color = "#10b981" if pct >= 100 else ("#f59e0b" if pct >= 50 else "#ef4444")
    return f"""
    <div class="stock-bar-wrap">
        <div class="stock-bar-fill" style="width:{pct:.0f}%;background:{color};"></div>
    </div>
    <span style="font-size:0.73rem;color:#64748b;">{int(actual)} / mín {int(minimo)}</span>
    """


def separador():
    st.markdown('<hr>', unsafe_allow_html=True)


def selectbox_con_otro(label: str, opciones: list, key_sel: str, key_otro: str,
                        placeholder_otro: str = "Escribe aquí...") -> str:
    """
    Selectbox que muestra un text_input si se selecciona la última opción
    ('Otro', 'Otra', etc.). Retorna el valor final seleccionado.
    """
    sel = st.selectbox(label, opciones, key=key_sel)
    if sel in ("Otro", "Otra", "Otra (escribir)", "📝 Otra (escribir)"):
        valor = st.text_input(f"✍️ {label} personalizado", placeholder=placeholder_otro, key=key_otro)
        return valor.strip() if valor.strip() else sel
    return sel
