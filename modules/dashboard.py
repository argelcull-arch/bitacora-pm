"""
NOVA — modules/dashboard.py  (v2)
Fixes: Plotly dark theme, enteros en KPIs, colores v2.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from collections import Counter
import pandas as pd
from config import kpi_card, seccion_titulo, badge_estado, badge_prioridad, COLOR, PLOTLY_LAYOUT, PLOTLY_COLORS
from database import get_tareas, get_pendientes, get_inventario_items, get_activos, get_usuarios, get_config


def render(sb):
    cfg          = get_config(sb)
    nombre_hotel = cfg.get("nombre_hotel", "Hotel NOVA")
    logo_url     = cfg.get("logo_url", "")
    hoy_str      = datetime.now().strftime("%A %d de %B, %Y")

    # ── Hero Banner ──────────────────────────────────────────────
    logo_html = (f'<img src="{logo_url}" style="max-height:44px;border-radius:8px;margin-right:12px;vertical-align:middle;">'
                 if logo_url else '<span style="font-size:2rem;margin-right:10px;">⚡</span>')
    st.markdown(f"""
    <div class="module-header" style="padding:22px 28px;margin-bottom:24px;">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
            <div style="display:flex;align-items:center;">
                {logo_html}
                <div>
                    <h2 style="margin:0;font-size:1.5rem;">{nombre_hotel}</h2>
                    <p style="margin:0;">{hoy_str}</p>
                </div>
            </div>
            <span style="font-size:2rem;">🏨</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Datos ────────────────────────────────────────────────────
    hoy      = date.today()
    hoy_iso  = datetime.combine(hoy, datetime.min.time()).isoformat()
    mañana   = datetime.combine(hoy + timedelta(days=1), datetime.min.time()).isoformat()

    todas_tareas     = get_tareas(sb)
    todos_pendientes = get_pendientes(sb)
    items_inv        = get_inventario_items(sb)
    activos          = get_activos(sb)

    tareas_hoy    = [t for t in todas_tareas if t.get("created_at","") >= hoy_iso]
    pend_criticos = [p for p in todos_pendientes if p["estado"]=="Abierto" and p.get("prioridad")=="Alta"]
    bajo_minimo   = [i for i in items_inv if i["stock_actual"] < i["stock_minimo"]]
    mant_vencidos = [a for a in activos
                     if a.get("proximo_mantenimiento") and
                        a["proximo_mantenimiento"] < hoy.isoformat() and
                        a.get("estado") == "Operativo"]

    # ── KPI Row ──────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("📋", int(len(tareas_hoy)),    "Requerimientos Hoy",     COLOR["primary"])
    with c2: kpi_card("🚨", int(len(pend_criticos)), "Pendientes Críticos",    COLOR["danger"])
    with c3: kpi_card("📦", int(len(bajo_minimo)),   "Ítems Bajo Mínimo",      COLOR["warning"])
    with c4: kpi_card("🔧", int(len(mant_vencidos)), "Mantenimientos Vencidos", COLOR["info"])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gráficos ─────────────────────────────────────────────────
    c_izq, c_der = st.columns(2)

    with c_izq:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📍 Top 10 Áreas — últimos 30 días</div>', unsafe_allow_html=True)
        hace30     = (datetime.utcnow() - timedelta(days=30)).isoformat()
        tareas_30  = [t for t in todas_tareas if t.get("created_at","") >= hace30]
        if tareas_30:
            conteo = Counter(t.get("lugar","Sin área") for t in tareas_30)
            top10  = dict(sorted(conteo.items(), key=lambda x: x[1], reverse=True)[:10])
            df_b   = pd.DataFrame({"Área": list(top10.keys()), "Requerimientos": list(top10.values())})
            fig    = px.bar(df_b, x="Requerimientos", y="Área", orientation="h",
                            color="Requerimientos",
                            color_continuous_scale=["#1e3a5f","#3b82f6"])
            fig.update_layout(**PLOTLY_LAYOUT, height=290, coloraxis_showscale=False)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de los últimos 30 días.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_der:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📈 Tendencia Semanal — 8 semanas</div>', unsafe_allow_html=True)
        semanas, conteos = [], []
        for w in range(7, -1, -1):
            ini = datetime.utcnow() - timedelta(weeks=w+1)
            fin = datetime.utcnow() - timedelta(weeks=w)
            cnt = sum(1 for t in todas_tareas
                      if ini.isoformat() <= t.get("created_at","") < fin.isoformat())
            semanas.append("Esta sem" if w == 0 else f"S-{w}")
            conteos.append(int(cnt))
        fig2 = go.Figure(go.Scatter(
            x=semanas, y=conteos, mode="lines+markers",
            line=dict(color=COLOR["primary"], width=2.5),
            marker=dict(size=8, color=COLOR["primary"], line=dict(width=2, color="#fff")),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, height=290)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Tablas rápidas ───────────────────────────────────────────
    c_l, c_r = st.columns(2)

    with c_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🕐 Últimos 5 Requerimientos</div>', unsafe_allow_html=True)
        for t in todas_tareas[:5]:
            hora = t.get("created_at","")[:16].replace("T"," ")
            st.markdown(f"""
            <div class="tabla-row">
                <div style="display:flex;gap:6px;align-items:center;margin-bottom:4px;flex-wrap:wrap;">
                    <span style="font-weight:700;color:#93c5fd;font-size:0.85rem;">{t.get('lugar','-')}</span>
                    {badge_prioridad(t.get('prioridad','Media'))} {badge_estado(t.get('estado','Abierto'))}
                </div>
                <div style="font-size:0.85rem;color:#f1f5f9;">{t.get('detalle','')[:65]}{'…' if len(t.get('detalle',''))>65 else ''}</div>
                <div style="font-size:0.72rem;color:#64748b;margin-top:4px;">👤 {t.get('usuario','-')} · {hora}</div>
            </div>
            """, unsafe_allow_html=True)
        if not todas_tareas:
            st.info("Sin requerimientos registrados.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_r:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🚨 Top 5 Pendientes Urgentes</div>', unsafe_allow_html=True)
        abiertos = sorted(
            [p for p in todos_pendientes if p["estado"] != "Resuelto"],
            key=lambda x: {"Alta":0,"Media":1,"Baja":2}.get(x.get("prioridad","Baja"), 2)
        )[:5]
        for p in abiertos:
            crea_date = p.get("created_at","")[:10]
            try:
                dias = (date.today() - date.fromisoformat(crea_date)).days
            except Exception:
                dias = 0
            dias_c  = "#ef4444" if dias > 3 else "#64748b"
            area_n  = p.get("areas",{}).get("nombre","-") if isinstance(p.get("areas"),dict) else "-"
            st.markdown(f"""
            <div class="tabla-row">
                <div style="display:flex;gap:6px;align-items:center;margin-bottom:4px;">
                    <span style="font-weight:700;color:#fde68a;font-size:0.85rem;">{area_n}</span>
                    {badge_prioridad(p.get('prioridad','Media'))}
                </div>
                <div style="font-size:0.85rem;color:#f1f5f9;">{p.get('descripcion','')[:60]}{'…' if len(p.get('descripcion',''))>60 else ''}</div>
                <div style="font-size:0.72rem;color:{dias_c};font-weight:600;margin-top:4px;">⏱ {int(dias)} días abierto · {p.get('asignado_a','-')}</div>
            </div>
            """, unsafe_allow_html=True)
        if not abiertos:
            st.success("✅ Sin pendientes urgentes.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Productividad técnicos ───────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👷 Productividad de Técnicos</div>', unsafe_allow_html=True)
    tecnicos = [u for u in get_usuarios(sb) if u.get("rol")=="tecnico" and u.get("activo")]
    if tecnicos:
        cols = st.columns(min(len(tecnicos), 4))
        for i, tec in enumerate(tecnicos[:4]):
            uname   = tec["username"]
            t_hoy_u = int(sum(1 for t in tareas_hoy if t.get("usuario")==uname))
            t_sem_u = int(sum(1 for t in todas_tareas
                              if t.get("usuario")==uname and
                                 t.get("created_at","") >= (datetime.utcnow()-timedelta(days=7)).isoformat()))
            initials = "".join(w[0].upper() for w in tec["nombre_completo"].split()[:2])
            with cols[i]:
                st.markdown(f"""
                <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.15);
                            border-radius:14px;padding:16px;text-align:center;">
                    <div style="width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#8b5cf6);
                                display:flex;align-items:center;justify-content:center;margin:0 auto 8px;
                                font-weight:800;font-size:0.95rem;color:#fff;">{initials}</div>
                    <div style="font-weight:700;font-size:0.88rem;color:#f1f5f9;margin-bottom:10px;">{tec['nombre_completo']}</div>
                    <div style="display:flex;justify-content:center;gap:16px;">
                        <div><div style="font-size:1.6rem;font-weight:800;color:#3b82f6;">{t_hoy_u}</div>
                             <div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;letter-spacing:.5px;">Hoy</div></div>
                        <div><div style="font-size:1.6rem;font-weight:800;color:#10b981;">{t_sem_u}</div>
                             <div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;letter-spacing:.5px;">Semana</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Sin técnicos registrados.")
    st.markdown('</div>', unsafe_allow_html=True)
