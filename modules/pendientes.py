"""
NOVA — modules/pendientes.py
Módulo 3: Tablero Kanban de pendientes de mantenimiento.
"""
import streamlit as st
from datetime import datetime, date
from config import (seccion_titulo, badge_prioridad, badge_estado,
                    PRIORIDADES, separador)
from database import (get_pendientes, get_area_nombres, get_usuarios,
                      crear_pendiente, actualizar_pendiente, borrar_pendiente)
from auth import es_admin


def _dias_abierto(created_at: str) -> int:
    try:
        return (date.today() - date.fromisoformat(created_at[:10])).days
    except Exception:
        return 0


def _tarjeta_kanban(p: dict, sb, col_color: str):
    """Renderiza una tarjeta de pendiente en el Kanban."""
    pid    = p.get("id")
    area   = p.get("areas", {}).get("nombre", "-") if isinstance(p.get("areas"), dict) else "-"
    dias   = _dias_abierto(p.get("created_at",""))
    dias_c = "#e53e3e" if dias > 3 else "#94a3b8"
    desc   = p.get("descripcion","")

    st.markdown(f"""
    <div class="kanban-card" style="border-left-color:{col_color};">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
            <span style="font-weight:700;font-size:0.85rem;color:#90cdf4;">📍 {area}</span>
            {badge_prioridad(p.get('prioridad','Media'))}
        </div>
        <div style="font-size:0.88rem;color:#e2e8f0;margin-bottom:8px;line-height:1.4;">
            {desc[:100]}{'…' if len(desc)>100 else ''}
        </div>
        <div style="font-size:0.72rem;color:#94a3b8;margin-bottom:4px;">
            👷 {p.get('asignado_a','-')} &nbsp;·&nbsp;
            <span style="color:{dias_c};font-weight:600;">⏱ {dias} días</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botones de acción
    estados_sig = {
        "Abierto":    "En Proceso",
        "En Proceso": "Resuelto",
        "Resuelto":   None,
    }
    sig_est = estados_sig.get(p.get("estado","Abierto"))

    ba, bb = st.columns(2)
    if sig_est:
        lbl = f"▶ {sig_est}"
        btn_cls = "btn-success" if sig_est == "Resuelto" else "btn-warning"
        with ba:
            st.markdown(f'<div class="{btn_cls}">', unsafe_allow_html=True)
            if st.button(lbl, key=f"pav_{pid}"):
                actualizar_pendiente(sb, pid, {"estado": sig_est})
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    if es_admin():
        with bb:
            st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
            if st.button("🗑️ Borrar", key=f"pdel_{pid}"):
                borrar_pendiente(sb, pid)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr style="margin:6px 0;">', unsafe_allow_html=True)


def render(sb):
    seccion_titulo("⚠️", "Pendientes", "Tablero Kanban de trabajos en seguimiento")

    usuario = st.session_state.get("usuario","")
    areas   = get_area_nombres(sb)
    usuarios = get_usuarios(sb)
    tec_nombres = [u["nombre_completo"] for u in usuarios] + ["Sin asignar"]

    # ── FORMULARIO NUEVO PENDIENTE ────────────────────────────────
    with st.expander("➕ Agregar Pendiente", expanded=False):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("form_pend", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                area_sel = st.selectbox("📍 Área", areas + ["Otra"], key="p_area")
            with c2:
                prioridad = st.selectbox("⚡ Prioridad", PRIORIDADES, key="p_prio")

            desc    = st.text_area("📝 Descripción del problema", height=80, key="p_desc")
            asignado = st.selectbox("👷 Asignar a", tec_nombres, key="p_asig")
            notas    = st.text_input("📌 Notas adicionales (opcional)", key="p_notas")
            enviado  = st.form_submit_button("💾 Crear Pendiente", use_container_width=True)

        if enviado:
            if not desc.strip():
                st.warning("⚠️ La descripción es obligatoria.")
            else:
                # Buscar area_id
                try:
                    resp = sb.table("areas").select("id").eq("nombre", area_sel).execute()
                    area_id = resp.data[0]["id"] if resp.data else None
                except Exception:
                    area_id = None

                ok = crear_pendiente(sb, {
                    "area_id":        area_id,
                    "descripcion":    desc.strip(),
                    "prioridad":      prioridad,
                    "estado":         "Abierto",
                    "asignado_a":     asignado if asignado != "Sin asignar" else None,
                    "usuario_creador":usuario,
                    "notas":          notas.strip() or None,
                })
                if ok:
                    st.success("✅ Pendiente creado.")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── KANBAN ────────────────────────────────────────────────────
    todos = get_pendientes(sb)

    col_a, col_b, col_c = st.columns(3)
    grupos = {
        "Abierto":    (col_a, "#e53e3e", "🔴"),
        "En Proceso": (col_b, "#d69e2e", "🟡"),
        "Resuelto":   (col_c, "#38a169", "🟢"),
    }

    for estado, (col, color, icono) in grupos.items():
        items = [p for p in todos if p.get("estado") == estado]
        with col:
            st.markdown(f"""
            <div class="kanban-col">
                <div class="kanban-header" style="background:rgba(255,255,255,0.05);color:{color};">
                    {icono} {estado} <span style="font-size:0.78rem;opacity:0.7;">({len(items)})</span>
                </div>
            """, unsafe_allow_html=True)
            if items:
                for p in items:
                    _tarjeta_kanban(p, sb, color)
            else:
                st.markdown(f"""
                <div style="text-align:center;padding:30px 0;color:#4a5568;font-size:0.85rem;">
                    Sin items en {estado}
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
