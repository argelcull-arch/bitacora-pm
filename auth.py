"""
NOVA — auth.py  (v2 — login rediseñado)
Autenticación con Supabase + fallback a diccionario.
"""
import streamlit as st
from supabase import Client

USERS_FALLBACK = {
    "admin":    {"password": "admin2024", "nombre": "Administrador", "rol": "admin"},
    "tecnico1": {"password": "mant2024",  "nombre": "Técnico 1",     "rol": "tecnico"},
    "tecnico2": {"password": "mant2024",  "nombre": "Técnico 2",     "rol": "tecnico"},
    "tecnico3": {"password": "mant2024",  "nombre": "Técnico 3",     "rol": "tecnico"},
}


def cargar_usuarios(supabase: Client) -> dict:
    try:
        resp = supabase.table("usuarios_config").select("*").eq("activo", True).execute()
        if resp.data:
            return {
                u["username"]: {
                    "password": u["password_plain"],
                    "nombre":   u["nombre_completo"],
                    "rol":      u["rol"],
                }
                for u in resp.data
            }
    except Exception:
        pass
    return USERS_FALLBACK


def pantalla_login(supabase: Client):
    """Pantalla de login rediseñada con glassmorphism."""
    # CSS específico del login
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0a0e1a 100%) !important; }

    /* Login card glassmorphism */
    .login-glass {
        max-width: 420px; margin: 48px auto 0;
        background: rgba(26,32,53,0.92);
        backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px; padding: 40px 36px 32px;
        box-shadow: 0 24px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(59,130,246,0.08);
    }
    .login-icon {
        font-size: 3rem; text-align: center;
        background: linear-gradient(135deg,#3b82f6,#8b5cf6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: block; margin-bottom: 2px;
    }
    .login-title {
        text-align: center; font-size: 1.8rem; font-weight: 800;
        color: #ffffff; letter-spacing: -0.5px; margin-bottom: 2px;
    }
    .login-sub {
        text-align: center; font-size: 0.82rem; color: #64748b;
        margin-bottom: 28px;
    }
    /* Inputs del login — TEXTO NEGRO */
    .login-area .stTextInput > div > div > input {
        background: #ffffff !important;
        color: #000000 !important;
        border: 1px solid rgba(59,130,246,0.4) !important;
        border-radius: 10px !important;
        font-size: 0.95rem !important;
        padding: 10px 14px !important;
    }
    .login-area .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.25) !important;
    }
    .login-area .stTextInput > label {
        color: #94a3b8 !important; font-size: 0.82rem !important; font-weight: 500 !important;
    }
    .login-area .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: #ffffff !important; border: none !important;
        border-radius: 10px !important; font-weight: 700 !important;
        font-size: 1rem !important; padding: 12px !important;
        box-shadow: 0 4px 16px rgba(59,130,246,0.4) !important;
    }
    .login-area .stButton > button:hover {
        background: linear-gradient(135deg, #60a5fa, #3b82f6) !important;
        transform: translateY(-1px) !important;
    }
    .login-hint { text-align:center; color:#374151; font-size:0.72rem; margin-top:14px; }
    </style>
    """, unsafe_allow_html=True)

    # Cargar nombre del hotel
    nombre_hotel = "Hotel NOVA"
    logo_url     = ""
    try:
        resp = supabase.table("configuracion").select("clave,valor").execute()
        cfg  = {r["clave"]: r["valor"] for r in (resp.data or [])}
        nombre_hotel = cfg.get("nombre_hotel", "Hotel NOVA")
        logo_url     = cfg.get("logo_url", "")
    except Exception:
        pass

    col_l, col_m, col_r = st.columns([1, 2.2, 1])
    with col_m:
        # Card
        if logo_url:
            st.markdown(f"""
            <div class="login-glass">
                <div style="text-align:center;margin-bottom:10px;">
                    <img src="{logo_url}" style="max-height:64px;border-radius:10px;margin-bottom:8px;">
                </div>
                <div class="login-title">⚡ NOVA</div>
                <div class="login-sub">{nombre_hotel} · Gestión de Ingeniería</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="login-glass">
                <span class="login-icon">⚡</span>
                <div class="login-title">NOVA</div>
                <div class="login-sub">{nombre_hotel} · Gestión de Ingeniería</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="login-area">', unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario", key="li_user")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="••••••••", key="li_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Iniciar Sesión →", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted:
            if not username.strip() or not password.strip():
                st.error("⚠️ Completa usuario y contraseña.")
            else:
                usuarios = cargar_usuarios(supabase)
                if username in usuarios and usuarios[username]["password"] == password:
                    u = usuarios[username]
                    st.session_state.update({
                        "logged_in": True,
                        "usuario":   username,
                        "nombre":    u["nombre"],
                        "rol":       u["rol"],
                    })
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")

        st.markdown('<div class="login-hint">Sistema NOVA · Ingeniería Hotelera</div>',
                    unsafe_allow_html=True)


def cerrar_sesion():
    st.session_state.clear()
    st.rerun()


def es_admin() -> bool:
    return st.session_state.get("rol", "tecnico") == "admin"


def requiere_admin():
    if not es_admin():
        st.error("🔒 Este módulo es exclusivo para administradores.")
        st.stop()
