"""
NOVA — config.py  (v3)
Constantes de negocio, helpers UI y función inject_css().
El CSS completo vive en styles.py.
"""
import streamlit as st
from styles import CSS_GLOBAL

# ── Paleta de colores ──────────────────────────────────────────
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


# ── CSS global (desde styles.py) ───────────────────────────────
def inject_css():
    st.markdown(CSS_GLOBAL, unsafe_allow_html=True)


# ── Helpers UI ─────────────────────────────────────────────────

def badge_estado(estado: str) -> str:
    mapa = {
        "Abierto":           ("badge-abierto",  "🔴 Abierto"),
        "En Proceso":        ("badge-proceso",  "🟡 En Proceso"),
        "Resuelto":          ("badge-resuelto", "🟢 Resuelto"),
        "Operativo":         ("badge-resuelto", "🟢 Operativo"),
        "En Reparación":     ("badge-proceso",  "🟡 En Reparación"),
        "Fuera de Servicio": ("badge-abierto",  "🔴 Fuera de Servicio"),
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
