"""
⚡ NOVA — Sistema de Gestión de Ingeniería Hotelera
Entry point principal: configuración de página, sidebar y routing de módulos.
Stack: Python + Streamlit + Supabase (PostgreSQL)
"""
import streamlit as st
from database import init_supabase, get_config
from config import inject_css
from auth import pantalla_login, cerrar_sesion, es_admin

# ── Configuración de página (debe ser la PRIMERA llamada de Streamlit) ─────────
st.set_page_config(
    page_title="⚡ NOVA — Ingeniería Hotelera",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inyectar CSS global ─────────────────────────────────────────────────────────
inject_css()

# ── Inicializar sesión ──────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ── Inicializar Supabase ────────────────────────────────────────────────────────
sb = init_supabase()

# ── Pantalla de Login ───────────────────────────────────────────────────────────
if not st.session_state["logged_in"]:
    pantalla_login(sb)
    st.stop()

# ── APLICACIÓN PRINCIPAL (usuario autenticado) ──────────────────────────────────

# Sidebar
with st.sidebar:
    # Logo / nombre del hotel
    cfg = {}
    try:
        cfg = get_config(sb)
    except Exception:
        pass

    nombre_hotel = cfg.get("nombre_hotel", "Hotel NOVA")
    logo_url     = cfg.get("logo_url", "")

    if logo_url:
        st.markdown(f"""
        <div class="nova-logo">
            <img src="{logo_url}" class="nova-logo-img">
            <h1>⚡ NOVA</h1>
            <p>{nombre_hotel}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="nova-logo">
            <h1>⚡ NOVA</h1>
            <p>{nombre_hotel}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Menú de navegación
    MODULOS = [
        ("🏠 Dashboard",        "dashboard"),
        ("📋 Requerimientos",   "requerimientos"),
        ("⚠️ Pendientes",       "pendientes"),
        ("📦 Inventario",       "inventario"),
        ("🔧 Activos & Equipos","activos"),
        ("✅ Preventivo",       "preventivo"),
        ("💡 Energía & Consumos","energia"),
        ("📊 Estadísticas",     "estadisticas"),
        ("📄 Reportes",         "reportes"),
    ]

    # Sólo mostrar Configuración a admins
    if es_admin():
        MODULOS.append(("⚙️ Configuración", "configuracion"))

    # Opción activa por defecto
    if "modulo_activo" not in st.session_state:
        st.session_state["modulo_activo"] = "dashboard"

    for label, key in MODULOS:
        es_activo = st.session_state["modulo_activo"] == key
        btn_style = """
        <style>
        div[data-testid="stButton"] button:hover { background: linear-gradient(135deg,#2d3a4a,#1e3a5f) !important; }
        </style>
        """ if not es_activo else ""

        if es_activo:
            st.markdown(f"""
            <div style="background:rgba(74,144,226,0.15);border:1px solid rgba(74,144,226,0.3);
                        border-radius:10px;padding:9px 14px;margin-bottom:4px;
                        border-left:3px solid #4a90e2;font-size:0.92rem;font-weight:600;color:#90cdf4;">
                {label}
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state["modulo_activo"] = key
                st.rerun()

    st.markdown("---")

    # Info del usuario con iniciales
    nombre_user = st.session_state.get("nombre","")
    rol_user    = st.session_state.get("rol","tecnico")
    initials    = "".join(w[0].upper() for w in nombre_user.split()[:2])
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:10px 4px;">
        <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#8b5cf6);
                    display:flex;align-items:center;justify-content:center;font-weight:800;
                    font-size:0.85rem;color:#fff;flex-shrink:0;">{initials}</div>
        <div>
            <div style="font-size:0.85rem;font-weight:600;color:#f1f5f9;">{nombre_user}</div>
            <div style="font-size:0.7rem;color:#3b82f6;font-weight:600;text-transform:uppercase;letter-spacing:.5px;">
                {'🔑 Admin' if rol_user=='admin' else '🔧 Técnico'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", key="btn_logout", use_container_width=True):
        cerrar_sesion()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Router de módulos ───────────────────────────────────────────────────────────
modulo = st.session_state.get("modulo_activo", "dashboard")

if modulo == "dashboard":
    from modules.dashboard import render
    render(sb)

elif modulo == "requerimientos":
    from modules.requerimientos import render
    render(sb)

elif modulo == "pendientes":
    from modules.pendientes import render
    render(sb)

elif modulo == "inventario":
    from modules.inventario import render
    render(sb)

elif modulo == "activos":
    from modules.activos import render
    render(sb)

elif modulo == "preventivo":
    from modules.preventivo import render
    render(sb)

elif modulo == "energia":
    from modules.energia import render
    render(sb)

elif modulo == "estadisticas":
    from modules.estadisticas import render
    render(sb)

elif modulo == "reportes":
    from modules.reportes import render
    render(sb)

elif modulo == "configuracion":
    from modules.configuracion import render
    render(sb)

else:
    st.error(f"Módulo '{modulo}' no encontrado.")
