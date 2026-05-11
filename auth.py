"""
NOVA — auth.py  (v3 — login WOW con glassmorphism real)
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


_LOGIN_CSS = """
<style>
/* ── FONDO CON IMAGEN HOTEL ── */
.stApp {
    background-image:
        linear-gradient(135deg, rgba(10,14,26,0.92) 0%, rgba(13,18,36,0.88) 50%, rgba(10,14,26,0.95) 100%),
        url('https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1920&q=80') !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}

/* ── OCULTAR CHROME DE STREAMLIT ── */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], .stDeployButton { display: none !important; }

/* ── CARD GLASSMORPHISM ── */
.login-card {
    max-width: 440px;
    margin: 0 auto;
    background: rgba(10,14,26,0.82);
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 28px;
    padding: 52px 44px 40px;
    box-shadow:
        0 32px 80px rgba(0,0,0,0.7),
        0 0 0 1px rgba(59,130,246,0.1),
        inset 0 1px 0 rgba(255,255,255,0.08);
    position: relative;
    overflow: hidden;
}
.login-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(59,130,246,0.5), transparent);
}
.login-card::after {
    content: '';
    position: absolute; top: -80px; right: -80px;
    width: 200px; height: 200px; border-radius: 50%;
    background: radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%);
    pointer-events: none;
}

/* ── LOGO ANIMADO ── */
@keyframes logoPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(59,130,246,0.4), 0 8px 32px rgba(59,130,246,0.3); }
    50%       { box-shadow: 0 0 0 12px rgba(59,130,246,0), 0 8px 32px rgba(59,130,246,0.5); }
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.login-logo-wrap {
    display: flex; justify-content: center; margin-bottom: 20px;
}
.login-logo-circle {
    width: 72px; height: 72px; border-radius: 22px;
    background: linear-gradient(135deg, #1d4ed8, #3b82f6, #8b5cf6, #1d4ed8);
    background-size: 300% 300%;
    animation: gradientShift 4s ease infinite, logoPulse 2.5s ease-in-out infinite;
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem; line-height: 1;
    box-shadow: 0 8px 32px rgba(59,130,246,0.3);
}
.login-title {
    text-align: center;
    font-size: 2.4rem; font-weight: 800; letter-spacing: -1px;
    background: linear-gradient(135deg, #ffffff 30%, #93c5fd 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 4px; line-height: 1;
}
.login-sub {
    text-align: center; font-size: 0.85rem;
    color: rgba(148,163,184,0.8); margin-bottom: 32px; letter-spacing: 0.3px;
}
.login-divider {
    height: 1px; margin: 0 0 24px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
}

/* ── INPUTS PREMIUM ── */
.login-form .stTextInput > label {
    color: #94a3b8 !important; font-size: 0.8rem !important;
    font-weight: 600 !important; letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}
.login-form .stTextInput > div > div > input {
    background: rgba(255,255,255,0.97) !important;
    color: #0f172a !important;
    border: 1.5px solid rgba(59,130,246,0.3) !important;
    border-radius: 12px !important;
    font-size: 0.97rem !important;
    padding: 12px 16px !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
    caret-color: #1d4ed8 !important;
}
.login-form .stTextInput > div > div > input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 4px rgba(59,130,246,0.18) !important;
    background: #ffffff !important;
}
.login-form .stTextInput > div > div > input::placeholder { color: #9ca3af !important; }

/* ── BOTÓN LOGIN ── */
@keyframes btnGlow {
    0%, 100% { box-shadow: 0 4px 20px rgba(59,130,246,0.4); }
    50%       { box-shadow: 0 4px 30px rgba(59,130,246,0.65); }
}
.login-form .stButton > button {
    background: linear-gradient(135deg, #2563eb 0%, #3b82f6 50%, #1d4ed8 100%) !important;
    background-size: 200% auto !important;
    color: #ffffff !important; border: none !important;
    border-radius: 14px !important; font-weight: 700 !important;
    font-size: 1rem !important; padding: 14px !important;
    width: 100% !important; letter-spacing: 0.3px !important;
    animation: btnGlow 2.5s ease-in-out infinite !important;
    transition: all 0.25s ease !important;
}
.login-form .stButton > button:hover {
    background-position: right center !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(59,130,246,0.6) !important;
}

/* ── FOOTER LOGIN ── */
.login-footer {
    text-align: center; margin-top: 24px;
    font-size: 0.73rem; color: rgba(100,116,139,0.7);
    letter-spacing: 0.5px;
}
.login-footer span { color: #3b82f6; font-weight: 600; }

/* ── FEATURE CHIPS (opcional visual) ── */
.login-chips {
    display: flex; justify-content: center; gap: 8px;
    flex-wrap: wrap; margin-bottom: 28px;
}
.login-chip {
    background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2);
    border-radius: 99px; padding: 4px 12px;
    font-size: 0.7rem; color: #93c5fd; font-weight: 500;
}
</style>
"""


def pantalla_login(supabase: Client):
    """Pantalla de login rediseñada — glassmorphism + imagen de hotel."""
    st.markdown(_LOGIN_CSS, unsafe_allow_html=True)

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

    # Layout: columna central ancha
    _, col_m, _ = st.columns([1, 2, 1])
    with col_m:
        # Logo / imagen
        if logo_url:
            logo_html = f'<img src="{logo_url}" style="max-height:64px;border-radius:14px;">'
        else:
            logo_html = '<div class="login-logo-circle">⚡</div>'

        st.markdown(f"""
        <div class="login-card">
            <div class="login-logo-wrap">{logo_html}</div>
            <div class="login-title">NOVA</div>
            <div class="login-sub">{nombre_hotel} · Sistema de Ingeniería</div>
            <div class="login-chips">
                <span class="login-chip">🏨 Hotelería</span>
                <span class="login-chip">🔧 Mantenimiento</span>
                <span class="login-chip">📊 Analytics</span>
            </div>
            <div class="login-divider"></div>
        </div>
        """, unsafe_allow_html=True)

        # Espacio para que el form quede dentro visualmente
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            st.text_input("👤  Usuario", placeholder="Ingresa tu usuario", key="li_user")
            st.text_input("🔒  Contraseña", type="password", placeholder="••••••••", key="li_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Iniciar Sesión  →", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted:
            username = st.session_state.get("li_user", "").strip()
            password = st.session_state.get("li_pass", "").strip()
            if not username or not password:
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

        st.markdown("""
        <div class="login-footer">
            Powered by <span>NOVA</span> · Ingeniería Hotelera v3.0
        </div>
        """, unsafe_allow_html=True)


def cerrar_sesion():
    st.session_state.clear()
    st.rerun()


def es_admin() -> bool:
    return st.session_state.get("rol", "tecnico") == "admin"


def requiere_admin():
    if not es_admin():
        st.error("🔒 Este módulo es exclusivo para administradores.")
        st.stop()
