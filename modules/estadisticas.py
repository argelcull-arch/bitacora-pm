"""
NOVA — modules/estadisticas.py  (v2)
Fixes: Plotly dark theme correcto, enteros en todos los conteos.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta, date
from collections import Counter
from config import seccion_titulo, kpi_card, COLOR, PLOTLY_LAYOUT, PLOTLY_COLORS
from database import (get_tareas, get_pendientes, get_usuarios,
                      get_preventivo_registros, get_preventivo_tareas)


def render(sb):
    seccion_titulo("📊", "Estadísticas", "Análisis de rendimiento y métricas del sistema")

    # ── Filtros globales ─────────────────────────────────────────
    with st.expander("🔍 Filtros Globales", expanded=True):
        c1, c2, c3 = st.columns(3)
        hoy   = date.today()
        f_ini = c1.date_input("Desde", value=hoy - timedelta(days=30), key="est_ini")
        f_fin = c2.date_input("Hasta", value=hoy, key="est_fin")
        usuarios  = get_usuarios(sb)
        u_opciones = ["Todos"] + [u["username"] for u in usuarios if u.get("rol")=="tecnico"]
        f_user    = c3.selectbox("Técnico", u_opciones, key="est_user")

    filtros = {
        "fecha_desde": f_ini.isoformat(),
        "fecha_hasta": (f_fin + timedelta(days=1)).isoformat(),
    }
    if f_user != "Todos":
        filtros["usuario"] = f_user

    tareas     = get_tareas(sb, filtros)
    todas      = get_tareas(sb)
    pendientes = get_pendientes(sb)
    pend_f     = [p for p in pendientes
                  if p.get("created_at","")[:10] >= f_ini.isoformat() and
                     p.get("created_at","")[:10] <= f_fin.isoformat()]
    regs_prev  = get_preventivo_registros(sb)

    if not tareas:
        st.info("Sin datos en el período seleccionado. Ajusta los filtros.")
        return

    # ── KPIs destacados ──────────────────────────────────────────
    cat_counter  = Counter(t.get("categoria","General") for t in tareas)
    area_counter = Counter(t.get("lugar","-") for t in tareas)
    user_counter = Counter(t.get("usuario","-") for t in tareas)

    tiempos = []
    for p in pend_f:
        if p.get("estado")=="Resuelto" and p.get("resuelto_at") and p.get("created_at"):
            try:
                diff = (datetime.fromisoformat(p["resuelto_at"].replace("Z","+00:00")) -
                        datetime.fromisoformat(p["created_at"].replace("Z","+00:00"))).days
                tiempos.append(diff)
            except Exception:
                pass

    prom_res  = f"{int(round(sum(tiempos)/len(tiempos)))} días" if tiempos else "N/D"
    cat_top   = cat_counter.most_common(1)[0][0]  if cat_counter  else "-"
    area_top  = area_counter.most_common(1)[0][0] if area_counter else "-"
    tec_top   = user_counter.most_common(1)[0][0] if user_counter else "-"
    tec_nombre = next((u["nombre_completo"] for u in usuarios if u["username"]==tec_top), tec_top)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("📋", int(len(tareas)), "Requerimientos",        COLOR["primary"])
    with c2: kpi_card("⏱",  prom_res,        "Tpo. Prom. Resolución", COLOR["warning"])
    with c3: kpi_card("🏷️", cat_top,          "Categoría Frecuente",   COLOR["info"])
    with c4: kpi_card("👷", tec_nombre,       "Técnico Más Activo",    COLOR["success"])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── GRÁFICO 1 + 2 ────────────────────────────────────────────
    c_izq, c_der = st.columns(2)

    with c_izq:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📍 Top 15 Áreas con más Incidencias</div>', unsafe_allow_html=True)
        top15 = dict(area_counter.most_common(15))
        df1   = pd.DataFrame({"Área": list(top15.keys()), "Total": list(top15.values())})
        df1   = df1.sort_values("Total")
        fig1  = px.bar(df1, x="Total", y="Área", orientation="h",
                       color="Total", color_continuous_scale=["#1e3a5f","#3b82f6"])
        fig1.update_layout(**PLOTLY_LAYOUT, height=380, coloraxis_showscale=False)
        fig1.update_traces(marker_line_width=0)
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_der:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🏷️ Distribución por Categoría</div>', unsafe_allow_html=True)
        df2  = pd.DataFrame({"Categoría": list(cat_counter.keys()), "Total": list(cat_counter.values())})
        fig2 = px.pie(df2, values="Total", names="Categoría",
                      color_discrete_sequence=PLOTLY_COLORS, hole=0.42)
        fig2.update_layout(**PLOTLY_LAYOUT, height=380)
        fig2.update_traces(textfont_size=11, textfont_color="#f1f5f9")
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── GRÁFICO 3: Evolución mensual ──────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📈 Evolución de Requerimientos — últimos 6 meses</div>', unsafe_allow_html=True)
    meses, conteos = [], []
    for offset in range(5, -1, -1):
        primer = (datetime.utcnow().replace(day=1) - timedelta(days=offset*30)).replace(day=1)
        ultimo = (primer.replace(day=28) + timedelta(days=4)).replace(day=1)
        cnt    = int(sum(1 for t in todas
                         if primer.date().isoformat() <= t.get("created_at","")[:10] < ultimo.date().isoformat()))
        meses.append(primer.strftime("%b %Y"))
        conteos.append(cnt)
    fig3 = go.Figure([go.Bar(
        x=meses, y=conteos,
        marker_color=PLOTLY_COLORS[0],
        text=conteos, textposition="outside",
        textfont=dict(color="#f1f5f9", size=13),
    )])
    fig3.update_layout(**PLOTLY_LAYOUT, height=260)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── GRÁFICO 4: Productividad técnicos ─────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👷 Productividad por Técnico</div>', unsafe_allow_html=True)
    tecnicos = [u for u in usuarios if u.get("rol")=="tecnico"]
    if tecnicos:
        filas = []
        for u in tecnicos:
            uname  = u["username"]
            t_tot  = int(sum(1 for t in tareas if t.get("usuario")==uname))
            t_res  = int(sum(1 for t in tareas if t.get("usuario")==uname and t.get("estado")=="Resuelto"))
            pct_c  = int(t_res/t_tot*100) if t_tot > 0 else 0
            filas.append({"Técnico": u["nombre_completo"], "Total": t_tot,
                          "Completadas": t_res, "Pendientes": t_tot-t_res, "% Cumplimiento": f"{pct_c}%"})
        df_p = pd.DataFrame(filas)
        fig4 = go.Figure(data=[
            go.Bar(name="Completadas", x=df_p["Técnico"], y=df_p["Completadas"], marker_color=COLOR["success"]),
            go.Bar(name="Pendientes",  x=df_p["Técnico"], y=df_p["Pendientes"],  marker_color=COLOR["danger"]),
        ])
        fig4.update_layout(**PLOTLY_LAYOUT, barmode="group", height=270)
        st.plotly_chart(fig4, use_container_width=True)
        st.dataframe(df_p, use_container_width=True, hide_index=True)
    else:
        st.info("Sin técnicos registrados.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── GRÁFICO 5: Comparativa mensual ────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Este Mes vs Mes Anterior</div>', unsafe_allow_html=True)
    ini_mes = hoy.replace(day=1).isoformat()
    ini_ant = ((hoy.replace(day=1) - timedelta(days=1)).replace(day=1)).isoformat()
    fin_ant = hoy.replace(day=1).isoformat()

    def _cnt(items, campo, desde, hasta=None):
        return int(sum(1 for i in items
                       if i.get(campo,"")[:10] >= desde and
                          (hasta is None or i.get(campo,"")[:10] < hasta)))

    pend_res_all = [p for p in pendientes if p.get("estado")=="Resuelto"]
    prev_ok_all  = [r for r in regs_prev if r.get("cumplido")]

    comp = {
        "Categoría":     ["Requerimientos","Pendientes Resueltos","Preventivos"],
        "Este Mes":      [_cnt(todas,"created_at",ini_mes),
                          _cnt(pend_res_all,"resuelto_at",ini_mes),
                          _cnt(prev_ok_all,"fecha",ini_mes)],
        "Mes Anterior":  [_cnt(todas,"created_at",ini_ant,fin_ant),
                          _cnt(pend_res_all,"resuelto_at",ini_ant,fin_ant),
                          _cnt(prev_ok_all,"fecha",ini_ant,fin_ant)],
    }
    df_c = pd.DataFrame(comp)
    fig5 = go.Figure(data=[
        go.Bar(name="Este Mes",     x=df_c["Categoría"], y=df_c["Este Mes"],    marker_color=COLOR["primary"]),
        go.Bar(name="Mes Anterior", x=df_c["Categoría"], y=df_c["Mes Anterior"],marker_color=COLOR["info"]),
    ])
    fig5.update_layout(**PLOTLY_LAYOUT, barmode="group", height=270)
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
