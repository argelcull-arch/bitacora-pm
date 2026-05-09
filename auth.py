"""
NOVA — auth.py
Sistema de autenticación con Supabase + fallback a diccionario.
"""
import streamlit as st
from supabase import Client

# Fallback si la tabla usuarios_config está vacía o hay error de BD
USERS_FALLBACK = {
    "admin":    {"password": "admin2024", "nombre": "Administrador",  "rol": "admin"},
    "tecnico1": {"password": "mant2024",  "nombre": "Técnico 1",      "rol": "tecnico"},
    "tecnico2": {"password": "mant2024",  "nombre": "Técnico 2",      "rol": "tecnico"},
    "tecnico3": {"password": "mant2024",  "nombre": "Técnico 3",      "rol": "tecnico"},
}


def cargar_usuarios(supabase: Client) -> dict:
    """
    Carga usuarios desde Supabase.
    Retorna dict {username: {password, nombre, rol}} o fallback si falla.
    """
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


def verificar_login(username: str, password: str, usuarios: dict) -> bool:
    """Verifica credenciales. Retorna True si son correctas."""
    if username in usuarios and usuarios[username]["password"] == password:
        return True
    return False


def pantalla_login(supabase: Client):
    """Renderiza la pantalla de login."""
    # Intentar cargar configuración del hotel para mostrar el nombre
    nombre_hotel = "Hotel"
    logo_url = ""
    try:
        resp = supabase.table("configuracion_hotel").select("clave,valor").execute()
        cfg = {r["clave"]: r["valor"] for r in (resp.data or [])}
        nombre_hotel = cfg.get("nombre_hotel", "Hotel NOVA")
        logo_url     = cfg.get("logo_url", "")
    except Exception:
        nombre_hotel = "Hotel NOVA"

    # CSS del login
    st.markdown("""
    <style>
    .login-wrap {
        max-width:420px; margin:50px auto 0; text-align:center;
        background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1);
        border-radius:22px; padding:38px 32px 30px;
        backdrop-filter:blur(10px); box-shadow:0 24px 64px rgba(0,0,0,0.5);
    }
    .login-logo-img { max-height:72px; max-width:200px; object-fit:contain;
                      border-radius:10px; margin-bottom:10px; }
    .login-brand { font-size:2rem; font-weight:800; color:#fff;
                   background:linear-gradient(135deg,#4a90e2,#805ad5);
                   -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .login-sub { font-size:0.82rem; color:#94a3b8; margin-top:2px; margin-bottom:26px; }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2.2, 1])
    with col_m:
        # Logo o ícono
        if logo_url:
            st.markdown(f"""
            <div class="login-wrap">
                <img src="{logo_url}" class="login-logo-img">
                <div class="login-brand">⚡ NOVA</div>
                <div class="login-sub">{nombre_hotel} · Gestión de Ingeniería</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="login-wrap">
                <div style="font-size:3rem;margin-bottom:6px;">⚡</div>
                <div class="login-brand">NOVA</div>
                <div class="login-sub">{nombre_hotel} · Gestión de Ingeniería</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Usuario", placeholder="ej. admin", key="login_user")
            password = st.text_input("🔒 Contraseña", type="password",
                                     placeholder="••••••••", key="login_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Iniciar Sesión →", use_container_width=True)

        if submitted:
            usuarios = cargar_usuarios(supabase)
            if verificar_login(username, password, usuarios):
                u = usuarios[username]
                st.session_state["logged_in"]  = True
                st.session_state["usuario"]    = username
                st.session_state["nombre"]     = u["nombre"]
                st.session_state["rol"]        = u["rol"]
                st.rerun()
            else:
                st.error("⚠️ Usuario o contraseña incorrectos.")


def cerrar_sesion():
    """Cierra la sesión del usuario."""
    st.session_state.clear()
    st.rerun()


def es_admin() -> bool:
    """Retorna True si el usuario actual es administrador."""
    return st.session_state.get("rol", "tecnico") == "admin"


def requiere_admin():
    """Muestra error y detiene ejecución si no es admin."""
    if not es_admin():
        st.error("🔒 Este módulo es exclusivo para administradores.")
        st.stop()
