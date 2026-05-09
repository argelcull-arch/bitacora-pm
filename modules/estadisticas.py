"""
NOVA — modules/estadisticas.py
Módulo 8: Estadísticas y análisis con gráficos Plotly.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta, date
from collections import Counter
from config import seccion_titulo, kpi_card, COLOR, PLOTLY_LAYOUT, PLOTLY_COLORS
from database import get_tareas, get_pendientes, get_usuarios, get_preventivo_registros, get_preventivo_tareas


def render(sb):
    seccion_titulo("📊", "Estadísticas", "Análisis de rendimiento y métricas del sistema")

    # ── Filtros globales ────────────────────────────────────────
    with st.expander("🔍 Filtros Globales", expanded=True):
        c1, c2, c3 = st.columns(3)
        hoy   = date.today()
        f_ini = c1.date_input("Desde", value=hoy - timedelta(days=30), key="est_ini")
        f_fin = c2.date_input("Hasta", value=hoy, key="est_fin")
        usuarios = get_usuarios(sb)
        u_names  = ["Todos"] + [u["username"] for u in usuarios if u.get("rol")=="tecnico"]
        f_user   = c3.selectbox("Técnico", u_names, key="est_user")

    # Cargar datos filtrados
    filtros = {"fecha_desde": f_ini.isoformat(), "fecha_hasta": (f_fin + timedelta(days=1)).isoformat()}
    if f_user != "Todos":
        filtros["usuario"] = f_user

    tareas     = get_tareas(sb, filtros)
    pendientes = get_pendientes(sb)
    pend_f     = [p for p in pendientes
                  if p.get("created_at","")[:10] >= f_ini.isoformat() and
                     p.get("created_at","")[:10] <= f_fin.isoformat()]

    if not tareas:
        st.info("Sin datos en el período seleccionado.")
        return

    # ── KPIs destacados ─────────────────────────────────────────
    total_reqs = len(tareas)
    pend_res   = sum(1 for p in pend_f if p.get("estado")=="Resuelto")

    # Tiempo promedio de resolución (pendientes resueltos)
    tiempos = []
    for p in pend_f:
        if p.get("estado")=="Resuelto" and p.get("resuelto_at") and p.get("created_at"):
            try:
                diff = (datetime.fromisoformat(p["resuelto_at"].replace("Z","+00:00")) -
                        datetime.fromisoformat(p["created_at"].replace("Z","+00:00"))).days
                tiempos.append(diff)
            except Exception:
                pass
    prom_res = f"{sum(tiempos)/len(tiempos):.1f} días" if tiempos else "N/D"

    # Categoría y área más frecuente
    cat_counter  = Counter(t.get("categoria","General") for t in tareas)
    area_counter = Counter(t.get("lugar","-") for t in tareas)
    cat_top  = cat_counter.most_common(1)[0][0] if cat_counter else "-"
    area_top = area_counter.most_common(1)[0][0] if area_counter else "-"

    # Técnico más activo
    user_counter = Counter(t.get("usuario","-") for t in tareas)
    tec_top = user_counter.most_common(1)[0][0] if user_counter else "-"
    tec_nombre_top = next((u["nombre_completo"] for u in usuarios if u["username"]==tec_top), tec_top)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("📋", total_reqs,    "Total Requerimientos", COLOR["primary"])
    with c2: kpi_card("⏱",  prom_res,      "Tiempo Prom. Resolución", COLOR["warning"])
    with c3: kpi_card("🏆", cat_top,       "Categoría Más Frecuente", COLOR["info"])
    with c4: kpi_card("👷", tec_nombre_top,"Técnico Más Activo",      COLOR["success"])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── GRÁFICO 1: Áreas con más incidencias ────────────────────
    c_izq, c_der = st.columns(2)
    with c_izq:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📍 Top 15 Áreas con más Incidencias</div>', unsafe_allow_html=True)
        top15 = dict(area_counter.most_common(15))
        if top15:
            df1 = pd.DataFrame({"Área": list(top15.keys()), "Total": list(top15.values())})
            fig1 = px.bar(df1.sort_values("Total"), x="Total", y="Área", orientation="h",
                          color="Total", color_continuous_scale=["#1a365d","#4a90e2"],
                          template="plotly_dark")
            fig1.update_layout(**PLOTLY_LAYOUT, height=380, coloraxis_showscale=False)
            fig1.update_traces(marker_line_width=0)
            st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── GRÁFICO 2: Requerimientos por categoría ─────────────────
    with c_der:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🏷️ Requerimientos por Categoría</div>', unsafe_allow_html=True)
        if cat_counter:
            df2 = pd.DataFrame({"Categoría": list(cat_counter.keys()), "Total": list(cat_counter.values())})
            fig2 = px.pie(df2, values="Total", names="Categoría",
                          color_discrete_sequence=PLOTLY_COLORS, template="plotly_dark",
                          hole=0.4)
            fig2.update_layout(**PLOTLY_LAYOUT, height=380)
            fig2.update_traces(textfont_size=11)
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── GRÁFICO 3: Evolución mensual (6 meses) ──────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📈 Evolución Mensual de Requerimientos (últimos 6 meses)</div>', unsafe_allow_html=True)
    meses, conteos = [], []
    for m_offset in range(5, -1, -1):
        primer_dia = (datetime.utcnow().replace(day=1) - timedelta(days=m_offset*30)).replace(day=1)
        ultimo_dia = (primer_dia.replace(day=28) + timedelta(days=4)).replace(day=1)
        cnt = sum(1 for t in get_tareas(sb)
                  if primer_dia.date().isoformat() <= t.get("created_at","")[:10] < ultimo_dia.date().isoformat())
        meses.append(primer_dia.strftime("%b %Y"))
        conteos.append(cnt)
    fig3 = go.Figure([
        go.Bar(x=meses, y=conteos, marker_color=PLOTLY_COLORS[0],
               text=conteos, textposition="outside", textfont_color=COLOR["text"])
    ])
    fig3.update_layout(**PLOTLY_LAYOUT, height=260)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── GRÁFICO 4: Productividad por técnico ────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👷 Productividad por Técnico</div>', unsafe_allow_html=True)
    tecnicos_activos = [u for u in usuarios if u.get("rol")=="tecnico"]
    if tecnicos_activos:
        filas = []
        for u in tecnicos_activos:
            uname = u["username"]
            t_total = sum(1 for t in tareas if t.get("usuario")==uname)
            t_res   = sum(1 for t in tareas if t.get("usuario")==uname and t.get("estado")=="Resuelto")
            t_pend  = t_total - t_res
            pct_c   = int(t_res/t_total*100) if t_total > 0 else 0
            filas.append({
                "Técnico":        u["nombre_completo"],
                "Total":          t_total,
                "Completadas":    t_res,
                "Pendientes":     t_pend,
                "% Cumplimiento": f"{pct_c}%",
            })
        df_prod = pd.DataFrame(filas)
        # Gráfico de barras agrupadas
        fig4 = go.Figure(data=[
            go.Bar(name="Completadas", x=df_prod["Técnico"], y=df_prod["Completadas"],
                   marker_color=COLOR["success"]),
            go.Bar(name="Pendientes",  x=df_prod["Técnico"], y=df_prod["Pendientes"],
                   marker_color=COLOR["danger"]),
        ])
        fig4.update_layout(**PLOTLY_LAYOUT, barmode="group", height=280)
        st.plotly_chart(fig4, use_container_width=True)
        # Tabla de resumen
        st.dataframe(df_prod, use_container_width=True, hide_index=True)
    else:
        st.info("Sin técnicos registrados.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── GRÁFICO 5: Comparativa este mes vs anterior ─────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Comparativa: Este Mes vs Mes Anterior</div>', unsafe_allow_html=True)
    todas = get_tareas(sb)
    regs_prev = get_preventivo_registros(sb)
    t_prev_tareas = get_preventivo_tareas(sb)

    hoy_d     = date.today()
    ini_mes   = hoy_d.replace(day=1).isoformat()
    ini_ant   = (hoy_d.replace(day=1) - timedelta(days=1)).replace(day=1).isoformat()
    fin_ant   = hoy_d.replace(day=1).isoformat()

    def _cnt(items, campo_fecha, desde, hasta=None):
        return sum(1 for i in items
                   if i.get(campo_fecha,"")[:10] >= desde and
                      (hasta is None or i.get(campo_fecha,"")[:10] < hasta))

    comp = {
        "Categoría": ["Requerimientos","Pendientes Resueltos","Preventivos Completados"],
        "Este Mes":  [
            _cnt(todas, "created_at", ini_mes),
            _cnt([p for p in pendientes if p.get("estado")=="Resuelto"], "resuelto_at", ini_mes),
            _cnt([r for r in regs_prev if r.get("cumplido")], "fecha", ini_mes),
        ],
        "Mes Anterior": [
            _cnt(todas, "created_at", ini_ant, fin_ant),
            _cnt([p for p in pendientes if p.get("estado")=="Resuelto"], "resuelto_at", ini_ant, fin_ant),
            _cnt([r for r in regs_prev if r.get("cumplido")], "fecha", ini_ant, fin_ant),
        ],
    }
    df_comp = pd.DataFrame(comp)
    fig5 = go.Figure(data=[
        go.Bar(name="Este Mes",     x=df_comp["Categoría"], y=df_comp["Este Mes"],
               marker_color=COLOR["primary"]),
        go.Bar(name="Mes Anterior", x=df_comp["Categoría"], y=df_comp["Mes Anterior"],
               marker_color="#805ad5"),
    ])
    fig5.update_layout(**PLOTLY_LAYOUT, barmode="group", height=280)
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
