"""
🛠️ Bitácora de PM - Aplicación de Registro de Mantenimiento
Desarrollada con Streamlit + Supabase (sincronización en la nube)
"""

import streamlit as st
import os
from datetime import datetime
from supabase import create_client, Client
from spellchecker import SpellChecker
import re

# ── Configuración de Página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="🛠️ Bitácora de PM",
    page_icon="🛠️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS Personalizado (Tema Oscuro Premium) ──────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  /* === Reset Global === */
  html, body, [class*="css"], .stApp {
      font-family: 'Inter', sans-serif !important;
      background: #0f1117 !important;
      color: #e2e8f0 !important;
  }

  /* === Fondo de la App === */
  .stApp {
      background: linear-gradient(135deg, #0f1117 0%, #1a1f2e 50%, #0f1117 100%) !important;
  }

  /* === Cabecera Principal === */
  .header-container {
      background: linear-gradient(135deg, #1e3a5f 0%, #2d6a4f 100%);
      border-radius: 16px;
      padding: 24px 28px;
      margin-bottom: 28px;
      border: 1px solid rgba(74, 144, 226, 0.3);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  }
  .header-container h1 {
      margin: 0;
      font-size: 1.9rem;
      font-weight: 700;
      color: #ffffff;
      letter-spacing: -0.5px;
  }
  .header-container p {
      margin: 6px 0 0 0;
      color: rgba(255,255,255,0.7);
      font-size: 0.9rem;
  }

  /* === Cards de Contenido === */
  .card {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 14px;
      padding: 22px 24px;
      margin-bottom: 20px;
      backdrop-filter: blur(10px);
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
  }

  /* === Inputs === */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea {
      background: rgba(255, 255, 255, 0.07) !important;
      border: 1px solid rgba(255, 255, 255, 0.15) !important;
      border-radius: 10px !important;
      color: #e2e8f0 !important;
      font-family: 'Inter', sans-serif !important;
      font-size: 0.95rem !important;
      transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
  }
  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
      border-color: #4a90e2 !important;
      box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2) !important;
  }
  .stTextInput > label, .stTextArea > label {
      color: #94a3b8 !important;
      font-size: 0.85rem !important;
      font-weight: 500 !important;
  }

  /* === Botones Primarios === */
  .stButton > button {
      background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%) !important;
      color: #ffffff !important;
      border: none !important;
      border-radius: 10px !important;
      padding: 10px 20px !important;
      font-weight: 600 !important;
      font-size: 0.9rem !important;
      font-family: 'Inter', sans-serif !important;
      transition: all 0.2s ease !important;
      box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3) !important;
      width: 100% !important;
  }
  .stButton > button:hover {
      transform: translateY(-1px) !important;
      box-shadow: 0 6px 20px rgba(74, 144, 226, 0.45) !important;
      background: linear-gradient(135deg, #5ba0f2 0%, #4a90e2 100%) !important;
  }
  .stButton > button:active {
      transform: translateY(0) !important;
  }

  /* === Botón Danger (Borrar) === */
  .btn-danger > button {
      background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%) !important;
      box-shadow: 0 4px 15px rgba(229, 62, 62, 0.3) !important;
  }
  .btn-danger > button:hover {
      background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%) !important;
      box-shadow: 0 6px 20px rgba(229, 62, 62, 0.45) !important;
  }

  /* === Botón Success (Copiar) === */
  .btn-success > button {
      background: linear-gradient(135deg, #38a169 0%, #2f855a 100%) !important;
      box-shadow: 0 4px 15px rgba(56, 161, 105, 0.3) !important;
  }
  .btn-success > button:hover {
      background: linear-gradient(135deg, #48bb78 0%, #38a169 100%) !important;
      box-shadow: 0 6px 20px rgba(56, 161, 105, 0.45) !important;
  }

  /* === Items de Tarea === */
  .task-item {
      background: rgba(74, 144, 226, 0.08);
      border: 1px solid rgba(74, 144, 226, 0.2);
      border-left: 4px solid #4a90e2;
      border-radius: 10px;
      padding: 14px 16px;
      margin-bottom: 10px;
      transition: all 0.2s ease;
  }
  .task-item:hover {
      background: rgba(74, 144, 226, 0.12);
      border-left-color: #5ba0f2;
  }
  .task-location {
      font-weight: 600;
      color: #63b3ed;
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
  }
  .task-detail {
      color: #e2e8f0;
      font-size: 0.95rem;
      line-height: 1.4;
  }
  .task-time {
      color: #718096;
      font-size: 0.75rem;
      margin-top: 6px;
  }

  /* === Resumen Box === */
  .summary-box {
      background: rgba(56, 161, 105, 0.1);
      border: 1px solid rgba(56, 161, 105, 0.3);
      border-radius: 12px;
      padding: 16px 18px;
      margin: 16px 0;
      font-size: 0.95rem;
      color: #68d391;
      line-height: 1.6;
      font-style: italic;
      word-break: break-word;
  }

  /* === Badges / Chips === */
  .badge {
      display: inline-block;
      background: rgba(74, 144, 226, 0.2);
      border: 1px solid rgba(74, 144, 226, 0.4);
      color: #63b3ed;
      border-radius: 20px;
      padding: 3px 12px;
      font-size: 0.78rem;
      font-weight: 600;
  }

  /* === Alerts / Mensajes === */
  .stAlert {
      border-radius: 10px !important;
  }

  /* === Divisor === */
  hr {
      border: none !important;
      border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
      margin: 20px 0 !important;
  }

  /* === Login Card === */
  .login-container {
      max-width: 420px;
      margin: 60px auto 0 auto;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      padding: 36px 32px;
      backdrop-filter: blur(10px);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  }
  .login-icon {
      font-size: 3rem;
      text-align: center;
      margin-bottom: 8px;
  }
  .login-title {
      text-align: center;
      font-size: 1.5rem;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 4px;
  }
  .login-subtitle {
      text-align: center;
      font-size: 0.85rem;
      color: #718096;
      margin-bottom: 28px;
  }

  /* === Ocultar elementos de Streamlit === */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}
  .stDeployButton {display: none;}

  /* === Responsive Mobile === */
  @media (max-width: 768px) {
      .header-container h1 { font-size: 1.4rem; }
      .card { padding: 16px 18px; }
      [data-testid="column"] { padding: 0 4px !important; }
  }
</style>
""", unsafe_allow_html=True)

# ── Conexión Supabase (SEGURA) ──────────────────────────────────────────────
@st.cache_resource
def init_supabase() -> Client:
    """Inicializa el cliente usando secrets (local o en la nube)."""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except KeyError:
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        st.error("❌ No se encontraron las credenciales de Supabase.")
        st.stop()
    return create_client(url, key)
# ── Corrector Ortográfico en Español ─────────────────────────────────────────
@st.cache_resource
def get_spell_checker():
    return SpellChecker(language='es')


def corregir_ortografia(texto: str) -> tuple[str, list[str]]:
    """
    Intenta corregir palabras en español.
    Retorna (texto_corregido, lista_de_correcciones_aplicadas).
    Conserva números, siglas y palabras en MAYÚSCULAS sin tocarlas.
    """
    spell = get_spell_checker()
    palabras = texto.split()
    corregidas = []
    cambios = []

    for palabra in palabras:
        # Conservar: números, palabras todo-mayúsculas (siglas), con dígitos
        if (palabra.isupper() and len(palabra) > 1) or re.search(r'\d', palabra):
            corregidas.append(palabra)
            continue

        # Limpiar puntuación para revisar
        limpia = re.sub(r'[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ]', '', palabra).lower()
        if not limpia:
            corregidas.append(palabra)
            continue

        corrected = spell.correction(limpia)
        if corrected and corrected != limpia:
            # Restaurar capitalización original
            if palabra[0].isupper():
                corrected = corrected.capitalize()
            cambios.append(f"'{palabra}' → '{corrected}'")
            corregidas.append(corrected)
        else:
            corregidas.append(palabra)

    return ' '.join(corregidas), cambios


# ── Usuarios Hardcodeados (SimpleAuth) ───────────────────────────────────────
# Para producción, usa Supabase Auth. Aquí se definen usuarios locales simples.
USERS = {
    "tecnico1": {"password": "mant2024", "nombre": "Técnico 1"},
    "tecnico2": {"password": "mant2024", "nombre": "Técnico 2"},
    "tecnico3": {"password": "mant2024", "nombre": "Técnico 3"},
    "admin":    {"password": "admin2024", "nombre": "Administrador"},
}


# ── Funciones de Base de Datos ───────────────────────────────────────────────
def obtener_tareas(supabase: Client, usuario: str) -> list[dict]:
    """Obtiene todas las tareas del usuario ordenadas por fecha."""
    try:
        resp = (
            supabase.table("tareas")
            .select("*")
            .eq("usuario", usuario)
            .order("created_at", desc=False)
            .execute()
        )
        return resp.data or []
    except Exception as e:
        st.error(f"❌ Error al obtener tareas: {e}")
        return []


def guardar_tarea(supabase: Client, usuario: str, lugar: str, detalle: str) -> bool:
    """Inserta una nueva tarea en Supabase."""
    try:
        supabase.table("tareas").insert({
            "usuario": usuario,
            "lugar": lugar.strip(),
            "detalle": detalle.strip(),
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")
        return False


def borrar_tareas_usuario(supabase: Client, usuario: str) -> bool:
    """Elimina todas las tareas del usuario de la base de datos."""
    try:
        supabase.table("tareas").delete().eq("usuario", usuario).execute()
        return True
    except Exception as e:
        st.error(f"❌ Error al borrar: {e}")
        return False


def generar_resumen(tareas: list[dict]) -> str:
    """Genera la cadena de resumen separada por ' / '."""
    if not tareas:
        return ""
    partes = [f"{t['lugar']}: {t['detalle']}" for t in tareas]
    return " / ".join(partes)


# ── Pantalla de Login ─────────────────────────────────────────────────────────
def pantalla_login():
    st.markdown("""
    <div class="login-container">
        <div class="login-icon">🛠️</div>
        <div class="login-title">Bitácora de PM</div>
        <div class="login-subtitle">Mantenimiento Preventivo — Inicia sesión para continuar</div>
    </div>
    """, unsafe_allow_html=True)

    # Centrar el formulario con columnas
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("<br>", unsafe_allow_html=True)
            usuario = st.text_input(
                "👤 Usuario",
                placeholder="ej. tecnico1",
                key="login_user"
            )
            password = st.text_input(
                "🔒 Contraseña",
                type="password",
                placeholder="••••••••",
                key="login_pass"
            )
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Iniciar Sesión →", use_container_width=True)

            if submitted:
                if usuario in USERS and USERS[usuario]["password"] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["usuario"] = usuario
                    st.session_state["nombre"] = USERS[usuario]["nombre"]
                    st.rerun()
                else:
                    st.error("⚠️ Usuario o contraseña incorrectos.")

        st.markdown("""
        <p style="text-align:center; color:#4a5568; font-size:0.75rem; margin-top:16px;">
            Usuarios: tecnico1 / tecnico2 / tecnico3 · Contraseña: mant2024
        </p>
        """, unsafe_allow_html=True)


# ── App Principal ─────────────────────────────────────────────────────────────
def app_principal():
    supabase = init_supabase()
    usuario = st.session_state["usuario"]
    nombre  = st.session_state["nombre"]

    # ── Cabecera ────────────────────────────────────────────────
    col_h, col_logout = st.columns([5, 1])
    with col_h:
        st.markdown(f"""
        <div class="header-container">
            <h1>🛠️ Bitácora de PM</h1>
            <p>Mantenimiento Preventivo &nbsp;·&nbsp; Sesión: <strong>{nombre}</strong> &nbsp;·&nbsp;
               {datetime.now().strftime('%d/%m/%Y')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_logout:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Salir", key="btn_logout"):
            st.session_state.clear()
            st.rerun()

    # ── Formulario de Ingreso ────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ➕ Registrar Actividad")

    with st.form("form_actividad", clear_on_submit=True):
        lugar = st.text_input(
            "📍 Lugar / Habitación",
            placeholder="ej. Habitación 30, Piscina, Lobby...",
            key="input_lugar"
        )
        detalle = st.text_input(
            "🔧 Detalle de la actividad",
            placeholder="ej. Cambio de foco, revisión de AC...",
            key="input_detalle"
        )
        guardar = st.form_submit_button("💾 Guardar Actividad", use_container_width=True)

    if guardar:
        if not lugar.strip() or not detalle.strip():
            st.warning("⚠️ Completa ambos campos antes de guardar.")
        else:
            # Corrección ortográfica
            detalle_corregido, cambios = corregir_ortografia(detalle)
            ok = guardar_tarea(supabase, usuario, lugar, detalle_corregido)
            if ok:
                if cambios:
                    st.success(f"✅ Actividad guardada · Ortografía corregida: {', '.join(cambios)}")
                else:
                    st.success("✅ Actividad guardada correctamente.")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Dashboard de Resumen ─────────────────────────────────────
    tareas = obtener_tareas(supabase, usuario)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    col_title, col_badge = st.columns([4, 1])
    with col_title:
        st.markdown("### 📋 Actividades del Día")
    with col_badge:
        st.markdown(f'<br><span class="badge">{len(tareas)} tareas</span>', unsafe_allow_html=True)

    if not tareas:
        st.markdown("""
        <div style="text-align:center; padding:30px; color:#4a5568;">
            <p style="font-size:2.5rem;">📝</p>
            <p>Sin actividades registradas aún.<br>Usa el formulario para agregar la primera.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Lista de tareas
        for i, t in enumerate(tareas, 1):
            hora_str = ""
            try:
                dt = datetime.fromisoformat(t["created_at"].replace("Z", "+00:00"))
                hora_str = dt.strftime("%H:%M")
            except Exception:
                hora_str = ""

            st.markdown(f"""
            <div class="task-item">
                <div class="task-location">📍 {t['lugar']}</div>
                <div class="task-detail">🔧 {t['detalle']}</div>
                <div class="task-time">🕐 {hora_str} &nbsp;·&nbsp; #{i}</div>
            </div>
            """, unsafe_allow_html=True)

        # Resumen concatenado
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 📊 Resumen para Excel")
        resumen = generar_resumen(tareas)
        st.markdown(f'<div class="summary-box">{resumen}</div>', unsafe_allow_html=True)

        # Copiar al portapapeles (via componente JS)
        # Streamlit no tiene acceso nativo al clipboard, usamos un hack con HTML/JS
        st.markdown(f"""
        <div style="margin: 12px 0;">
            <textarea id="resumen_text" style="position:absolute;left:-9999px;opacity:0;"
                      readonly>{resumen}</textarea>
            <button onclick="
                var t = document.getElementById('resumen_text');
                t.select(); t.setSelectionRange(0, 99999);
                navigator.clipboard.writeText(t.value).then(function() {{
                    var b = document.getElementById('copy_btn');
                    b.innerText = '✅ ¡Copiado!';
                    b.style.background = 'linear-gradient(135deg, #38a169, #2f855a)';
                    setTimeout(function(){{
                        b.innerText = '📋 Copiar Resumen';
                        b.style.background = 'linear-gradient(135deg, #4a90e2, #357abd)';
                    }}, 2500);
                }}).catch(function() {{
                    t.select(); document.execCommand('copy');
                    var b = document.getElementById('copy_btn');
                    b.innerText = '✅ ¡Copiado!';
                    setTimeout(function(){{ b.innerText = '📋 Copiar Resumen'; }}, 2500);
                }});
            "
            id="copy_btn"
            style="
                width:100%; padding:11px 20px; font-size:0.95rem; font-weight:600;
                font-family:'Inter',sans-serif; cursor:pointer; border:none; border-radius:10px;
                background:linear-gradient(135deg,#4a90e2,#357abd); color:#fff;
                box-shadow:0 4px 15px rgba(74,144,226,0.3);
                transition: all 0.2s ease;
            ">📋 Copiar Resumen</button>
        </div>
        """, unsafe_allow_html=True)

        # Separador
        st.markdown("<br>", unsafe_allow_html=True)

        # Botón Borrar Tareas (con confirmación)
        if "confirmar_borrar" not in st.session_state:
            st.session_state["confirmar_borrar"] = False

        if not st.session_state["confirmar_borrar"]:
            st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
            if st.button("🗑️ Borrar Todas las Tareas", key="btn_borrar_init", use_container_width=True):
                st.session_state["confirmar_borrar"] = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ ¿Confirmas que deseas eliminar **todas** las tareas? Esta acción es irreversible.")
            col_si, col_no = st.columns(2)
            with col_si:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("✅ Sí, Borrar Todo", key="btn_confirmar_si", use_container_width=True):
                    if borrar_tareas_usuario(supabase, usuario):
                        st.success("🗑️ Todas las tareas han sido eliminadas.")
                        st.session_state["confirmar_borrar"] = False
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with col_no:
                if st.button("❌ Cancelar", key="btn_confirmar_no", use_container_width=True):
                    st.session_state["confirmar_borrar"] = False
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Footer ───────────────────────────────────────────────────
    st.markdown("""
    <p style="text-align:center; color:#2d3748; font-size:0.72rem; margin-top:30px;">
        🛠️ Bitácora de PM · Sincronización en Tiempo Real con Supabase
    </p>
    """, unsafe_allow_html=True)


# ── Punto de Entrada ──────────────────────────────────────────────────────────
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        pantalla_login()
    else:
        app_principal()


if __name__ == "__main__":
    main()
