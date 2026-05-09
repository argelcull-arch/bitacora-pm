"""
NOVA — modules/preventivo.py
Módulo 6: Mantenimiento preventivo con checklist y KPIs de cumplimiento.
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import date, timedelta, datetime
from config import seccion_titulo, COLOR, PLOTLY_LAYOUT
from database import get_preventivo_tareas, get_preventivo_registros, registrar_preventivo


def _esta_cumplido_hoy(registros: list, tarea_id: int) -> dict | None:
    """Retorna el registro de hoy para la tarea, o None si no existe."""
    hoy = date.today().isoformat()
    for r in registros:
        if r.get("tarea_id") == tarea_id and r.get("fecha","")[:10] == hoy:
            return r
    return None


def _seccion_frecuencia(label: str, icono: str, tareas: list, registros: list, sb, usuario: str):
    """Renderiza bloque de tareas por frecuencia."""
    cumplidas = sum(1 for t in tareas if _esta_cumplido_hoy(registros, t["id"]) and
                    _esta_cumplido_hoy(registros, t["id"]).get("cumplido"))
    total = len(tareas)
    pct   = int(cumplidas / total * 100) if total > 0 else 0
    pct_c = "#38a169" if pct == 100 else ("#d69e2e" if pct >= 50 else "#e53e3e")

    st.markdown(f"""
    <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <div class="card-title" style="margin-bottom:0;">{icono} {label}</div>
            <div style="font-size:1.4rem;font-weight:800;color:{pct_c};">{pct}%</div>
        </div>
    """, unsafe_allow_html=True)

    for t in tareas:
        tid   = t["id"]
        reg   = _esta_cumplido_hoy(registros, tid)
        cumpl = reg and reg.get("cumplido", False)
        es_hoy_vencida = not cumpl  # Si es diaria y no cumplida hoy, es vencida

        estado_label = "✅ Cumplida" if cumpl else "🔴 Pendiente"
        est_c        = "#38a169" if cumpl else "#e53e3e"

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                    border-left:3px solid {est_c};border-radius:10px;padding:12px 14px;margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px;">
                <span style="font-weight:700;color:#e2e8f0;font-size:0.9rem;">{t['nombre']}</span>
                <span style="font-size:0.75rem;color:{est_c};font-weight:700;">{estado_label}</span>
            </div>
            <div style="font-size:0.78rem;color:#94a3b8;margin:4px 0;">{t.get('descripcion','')}</div>
            {f'<div style="font-size:0.75rem;color:#68d391;">👤 {reg["completado_por"]} · {reg.get("observaciones","")}</div>' if cumpl and reg else ''}
        </div>
        """, unsafe_allow_html=True)

        if not cumpl:
            with st.expander(f"✍️ Marcar como cumplida — {t['nombre']}", expanded=False):
                with st.form(f"prev_form_{tid}_{date.today().isoformat()}"):
                    tecnico  = st.text_input("Tu nombre / firma", value=usuario, key=f"pf_tec_{tid}")
                    obs      = st.text_area("Observaciones", height=60, key=f"pf_obs_{tid}")
                    cumplida = st.checkbox("✅ Confirmo que esta tarea fue realizada", key=f"pf_chk_{tid}")
                    submit_p = st.form_submit_button("💾 Registrar")
                if submit_p:
                    if not cumplida:
                        st.warning("⚠️ Confirma el checkbox para registrar.")
                    else:
                        ok = registrar_preventivo(sb, {
                            "tarea_id":       tid,
                            "completado_por": tecnico.strip() or usuario,
                            "fecha":          date.today().isoformat(),
                            "cumplido":       True,
                            "observaciones":  obs.strip(),
                        })
                        if ok:
                            st.success("✅ Tarea registrada.")
                            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render(sb):
    seccion_titulo("✅", "Mantenimiento Preventivo", "Checklists diarios, semanales y mensuales")

    usuario  = st.session_state.get("nombre","Técnico")
    hoy      = date.today()
    ini_sem  = hoy - timedelta(days=hoy.weekday())
    ini_mes  = hoy.replace(day=1)

    # Cargar datos
    t_diarias   = get_preventivo_tareas(sb, "diaria")
    t_semanales = get_preventivo_tareas(sb, "semanal")
    t_mensuales = get_preventivo_tareas(sb, "mensual")

    regs_hoy  = get_preventivo_registros(sb, fecha_desde=hoy.isoformat(), fecha_hasta=hoy.isoformat())
    regs_sem  = get_preventivo_registros(sb, fecha_desde=ini_sem.isoformat(), fecha_hasta=hoy.isoformat())
    regs_mes  = get_preventivo_registros(sb, fecha_desde=ini_mes.isoformat(), fecha_hasta=hoy.isoformat())

    # ── KPIs ────────────────────────────────────────────────────
    def _pct(tareas, regs):
        if not tareas: return 0
        c = sum(1 for t in tareas
                for r in regs if r.get("tarea_id")==t["id"] and r.get("cumplido"))
        return int(c / len(tareas) * 100)

    pct_dia = _pct(t_diarias, regs_hoy)
    pct_sem = _pct(t_semanales, regs_sem)
    pct_mes = _pct(t_mensuales, regs_mes)

    c1, c2, c3 = st.columns(3)
    for col, pct, label, icon in [
        (c1, pct_dia, "Cumplimiento Hoy",        "📅"),
        (c2, pct_sem, "Cumplimiento Semana",      "📆"),
        (c3, pct_mes, "Cumplimiento Mes",         "🗓️"),
    ]:
        color = "#38a169" if pct==100 else ("#d69e2e" if pct>=50 else "#e53e3e")
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-card-accent" style="background:{color};"></div>
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-num" style="color:{color};">{pct}%</div>
                <div class="kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gráfico gauge de cumplimiento semanal ──────────────────
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_sem,
        title={"text": "Cumplimiento Semanal", "font": {"color": COLOR["text"], "size": 14}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": COLOR["muted"]},
            "bar":  {"color": COLOR["success"] if pct_sem >= 80 else COLOR["warning"] if pct_sem >= 50 else COLOR["danger"]},
            "bgcolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0, 50],   "color": "rgba(229,62,62,0.1)"},
                {"range": [50, 80],  "color": "rgba(214,158,46,0.1)"},
                {"range": [80, 100], "color": "rgba(56,161,105,0.1)"},
            ],
            "threshold": {"line": {"color": COLOR["primary"], "width": 2}, "value": 80},
        },
        number={"suffix": "%", "font": {"color": COLOR["text"]}},
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=200)
    st.plotly_chart(fig, use_container_width=True)

    # ── Checklists por frecuencia ──────────────────────────────
    tab_d, tab_s, tab_m = st.tabs(["📅 Diarias", "📆 Semanales", "🗓️ Mensuales"])

    with tab_d:
        _seccion_frecuencia("Tareas Diarias", "📅", t_diarias, regs_hoy, sb, usuario)
    with tab_s:
        _seccion_frecuencia("Tareas Semanales", "📆", t_semanales, regs_sem, sb, usuario)
    with tab_m:
        _seccion_frecuencia("Tareas Mensuales", "🗓️", t_mensuales, regs_mes, sb, usuario)
