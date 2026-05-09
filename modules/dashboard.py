"""
NOVA — modules/dashboard.py
Módulo 1: Dashboard principal con KPIs, gráficos y tablas rápidas.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import pandas as pd
from config import kpi_card, seccion_titulo, badge_estado, badge_prioridad, COLOR, PLOTLY_LAYOUT, PLOTLY_COLORS
from database import get_tareas, get_pendientes, get_inventario_items, get_activos, get_usuarios


def render(sb):
    cfg = {}
    try:
        r = sb.table("configuracion_hotel").select("clave,valor").execute()
        cfg = {x["clave"]: x["valor"] for x in (r.data or [])}
    except Exception:
        pass

    nombre_hotel = cfg.get("nombre_hotel", "Hotel NOVA")
    logo_url     = cfg.get("logo_url", "")
    hoy_str      = datetime.now().strftime("%A %d de %B, %Y")

    # ── Hero Banner ─────────────────────────────────────────────
    logo_html = f'<img src="{logo_url}" style="max-height:48px;border-radius:8px;margin-right:14px;vertical-align:middle;">' if logo_url else '<span style="font-size:2.4rem;margin-right:10px;">⚡</span>'
    st.markdown(f"""
    <div class="hero-banner" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
        <div>
            <div style="display:flex;align-items:center;margin-bottom:4px;">
                {logo_html}
                <h2 style="margin:0;font-size:1.6rem;font-weight:800;color:#fff;">{nombre_hotel}</h2>
            </div>
            <p style="margin:0;color:rgba(255,255,255,0.55);font-size:0.85rem;">Sistema de Gestión de Ingeniería &nbsp;·&nbsp; {hoy_str}</p>
        </div>
        <div style="font-size:2.2rem;">🏨</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Cargar datos ────────────────────────────────────────────
    hoy   = date.today()
    hoy_i = datetime.combine(hoy, datetime.min.time()).isoformat()
    manana_i = datetime.combine(hoy + timedelta(days=1), datetime.min.time()).isoformat()

    todas_tareas    = get_tareas(sb)
    todos_pendientes = get_pendientes(sb)
    items_inv       = get_inventario_items(sb)
    activos         = get_activos(sb)

    # KPIs
    tareas_hoy      = [t for t in todas_tareas if t.get("created_at","") >= hoy_i]
    pend_criticos   = [p for p in todos_pendientes if p["estado"]=="Abierto" and p.get("prioridad")=="Alta"]
    bajo_minimo     = [i for i in items_inv if i["stock_actual"] < i["stock_minimo"]]
    mant_vencidos   = [a for a in activos
                       if a.get("proximo_mantenimiento") and
                          a["proximo_mantenimiento"] < hoy.isoformat() and
                          a.get("estado") == "Operativo"]

    # ── Fila 1: KPIs ────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("📋", len(tareas_hoy),    "Requerimientos Hoy",    COLOR["primary"])
    with c2: kpi_card("🚨", len(pend_criticos), "Pendientes Críticos",   COLOR["danger"])
    with c3: kpi_card("📦", len(bajo_minimo),   "Stock Bajo Mínimo",     COLOR["warning"])
    with c4: kpi_card("🔧", len(mant_vencidos), "Mantenimientos Vencidos",COLOR["info"])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Fila 2: Gráficos ────────────────────────────────────────
    c_izq, c_der = st.columns(2)

    with c_izq:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 Top 10 Áreas con más Incidencias (30 días)</div>', unsafe_allow_html=True)
        hace30 = (datetime.utcnow() - timedelta(days=30)).isoformat()
        tareas_30 = [t for t in todas_tareas if t.get("created_at","") >= hace30]
        if tareas_30:
            from collections import Counter
            conteo = Counter(t.get("lugar","Sin área") for t in tareas_30)
            top10  = dict(sorted(conteo.items(), key=lambda x: x[1], reverse=True)[:10])
            df_bar = pd.DataFrame({"Área": list(top10.keys()), "Total": list(top10.values())})
            fig = px.bar(df_bar, x="Total", y="Área", orientation="h",
                         color="Total", color_continuous_scale=["#1a365d","#4a90e2"],
                         template="plotly_dark")
            fig.update_layout(**PLOTLY_LAYOUT, height=280, coloraxis_showscale=False)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de los últimos 30 días.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_der:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📈 Tendencia Semanal (8 semanas)</div>', unsafe_allow_html=True)
        semanas, conteos = [], []
        for w in range(7, -1, -1):
            ini = datetime.utcnow() - timedelta(weeks=w+1)
            fin = datetime.utcnow() - timedelta(weeks=w)
            cnt = sum(1 for t in todas_tareas
                      if ini.isoformat() <= t.get("created_at","") < fin.isoformat())
            semanas.append(f"S-{w}" if w > 0 else "Esta sem")
            conteos.append(cnt)
        fig2 = go.Figure(go.Scatter(
            x=semanas, y=conteos, mode="lines+markers",
            line=dict(color=COLOR["primary"], width=2.5),
            marker=dict(size=7, color=COLOR["primary"]),
            fill="tozeroy", fillcolor="rgba(74,144,226,0.12)",
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, height=280)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Fila 3: Tablas rápidas ───────────────────────────────────
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🕐 Últimos 5 Requerimientos</div>', unsafe_allow_html=True)
        ultimos5 = todas_tareas[:5]
        if ultimos5:
            for t in ultimos5:
                hora = t.get("created_at","")[:16].replace("T"," ")
                st.markdown(f"""
                <div class="tabla-row" style="border-radius:8px;margin-bottom:6px;background:rgba(255,255,255,0.04);padding:10px 12px;">
                    <span style="font-size:0.83rem;font-weight:600;color:#63b3ed;">{t.get('lugar','-')}</span>
                    &nbsp;{badge_prioridad(t.get('prioridad','Media'))}&nbsp;{badge_estado(t.get('estado','Abierto'))}<br>
                    <span style="font-size:0.8rem;color:#e2e8f0;">{t.get('detalle','')[:60]}{'…' if len(t.get('detalle',''))>60 else ''}</span><br>
                    <span style="font-size:0.72rem;color:#94a3b8;">{hora} · {t.get('usuario','-')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Sin requerimientos registrados.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🚨 Top 5 Pendientes Urgentes</div>', unsafe_allow_html=True)
        abiertos = [p for p in todos_pendientes if p["estado"] != "Resuelto"]
        prio_ord = {"Alta":0,"Media":1,"Baja":2}
        abiertos_sorted = sorted(abiertos, key=lambda x: prio_ord.get(x.get("prioridad","Baja"),2))[:5]
        if abiertos_sorted:
            for p in abiertos_sorted:
                crea  = p.get("created_at","")[:10]
                try:
                    dias = (date.today() - date.fromisoformat(crea)).days
                except Exception:
                    dias = 0
                dias_color = "#e53e3e" if dias > 3 else "#94a3b8"
                area_nombre = p.get("areas",{}).get("nombre","-") if isinstance(p.get("areas"),dict) else p.get("lugar","-")
                st.markdown(f"""
                <div class="tabla-row" style="border-radius:8px;margin-bottom:6px;background:rgba(255,255,255,0.04);padding:10px 12px;">
                    <span style="font-size:0.83rem;font-weight:600;color:#fbd38d;">{area_nombre}</span>
                    &nbsp;{badge_prioridad(p.get('prioridad','Media'))}<br>
                    <span style="font-size:0.8rem;color:#e2e8f0;">{p.get('descripcion','')[:55]}{'…' if len(p.get('descripcion',''))>55 else ''}</span><br>
                    <span style="font-size:0.72rem;color:{dias_color};font-weight:600;">⏱ {dias} días abierto · {p.get('asignado_a','-')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Sin pendientes urgentes.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Fila 4: Productividad de técnicos hoy ───────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👷 Productividad de Técnicos</div>', unsafe_allow_html=True)
    usuarios = get_usuarios(sb)
    tecnicos = [u for u in usuarios if u.get("rol") == "tecnico" and u.get("activo")]
    if tecnicos:
        cols = st.columns(len(tecnicos) if len(tecnicos) <= 4 else 4)
        for i, tec in enumerate(tecnicos[:4]):
            uname = tec["username"]
            t_hoy_u  = sum(1 for t in tareas_hoy if t.get("usuario") == uname)
            t_sem_u  = sum(1 for t in todas_tareas
                           if t.get("usuario") == uname and
                              t.get("created_at","") >= (datetime.utcnow()-timedelta(days=7)).isoformat())
            with cols[i]:
                st.markdown(f"""
                <div style="background:rgba(74,144,226,0.08);border:1px solid rgba(74,144,226,0.2);border-radius:12px;padding:14px;text-align:center;">
                    <div style="font-size:1.5rem;">👷</div>
                    <div style="font-weight:700;font-size:0.9rem;color:#e2e8f0;">{tec['nombre_completo']}</div>
                    <div style="margin-top:8px;display:flex;justify-content:center;gap:14px;">
                        <div><div style="font-size:1.4rem;font-weight:800;color:#4a90e2;">{t_hoy_u}</div>
                             <div style="font-size:0.68rem;color:#94a3b8;">HOY</div></div>
                        <div><div style="font-size:1.4rem;font-weight:800;color:#38a169;">{t_sem_u}</div>
                             <div style="font-size:0.68rem;color:#94a3b8;">SEMANA</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Sin técnicos registrados.")
    st.markdown('</div>', unsafe_allow_html=True)
