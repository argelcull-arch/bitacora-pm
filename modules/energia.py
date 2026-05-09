"""
NOVA — modules/energia.py (v3)
Fix: todos los valores son enteros (int), step=1, format="%d".
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta
from config import seccion_titulo, kpi_card, COLOR, PLOTLY_LAYOUT, TIPOS_ENERGIA, UNIDADES_ENERGIA
from database import get_energia_lecturas, registrar_lectura_energia


def _consumo_df(lecturas: list, tipo: str) -> pd.DataFrame:
    datos = sorted([l for l in lecturas if l.get("tipo")==tipo], key=lambda x: x["fecha"])
    if len(datos) < 2:
        return pd.DataFrame()
    rows = []
    for i in range(1, len(datos)):
        consumo = int(datos[i]["valor"]) - int(datos[i-1]["valor"])
        if consumo >= 0:
            rows.append({"fecha": datos[i]["fecha"], "consumo": int(consumo)})
    return pd.DataFrame(rows)


def render(sb):
    seccion_titulo("💡","Energía & Consumos","Monitoreo de electricidad, agua y gas")
    usuario = st.session_state.get("usuario","")

    tab_reg, tab_e, tab_a, tab_g = st.tabs(["📝 Registrar","⚡ Electricidad","💧 Agua","🔥 Gas"])

    # ── TAB REGISTRO ────────────────────────────────────────────
    with tab_reg:
        st.markdown('<div class="card">',unsafe_allow_html=True)
        st.markdown('<div class="card-title">📝 Nueva Lectura de Medidor</div>',unsafe_allow_html=True)
        with st.form("form_energia",clear_on_submit=True):
            c1,c2,c3 = st.columns(3)
            tipo   = c1.selectbox("Tipo",TIPOS_ENERGIA,key="en_tipo",
                                   format_func=lambda x: {"electricidad":"⚡ Electricidad","agua":"💧 Agua","gas":"🔥 Gas"}.get(x,x))
            # ENTERO: step=1, format="%d"
            valor  = c2.number_input("Lectura del medidor *",min_value=0,value=0,step=1,format="%d",key="en_val")
            fecha  = c3.date_input("Fecha",value=date.today(),key="en_fecha")
            notas  = st.text_input("Notas (opcional)",key="en_notas")
            submit = st.form_submit_button("💾 Registrar Lectura",use_container_width=True)
        if submit:
            if valor <= 0:
                st.warning("⚠️ Ingresa un valor mayor a 0.")
            else:
                ok = registrar_lectura_energia(sb,{
                    "tipo":   tipo,
                    "valor":  int(valor),
                    "unidad": UNIDADES_ENERGIA.get(tipo,""),
                    "fecha":  fecha.isoformat(),
                    "usuario":usuario,
                    "notas":  notas.strip(),
                })
                if ok:
                    st.success(f"✅ Lectura de {tipo}: {int(valor)} {UNIDADES_ENERGIA.get(tipo,'')} registrada.")
                    st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

        # Últimas lecturas
        st.markdown('<div class="card">',unsafe_allow_html=True)
        st.markdown('<div class="card-title">🕐 Últimas Lecturas</div>',unsafe_allow_html=True)
        lecs_todas = sorted(get_energia_lecturas(sb), key=lambda x: x.get("fecha",""), reverse=True)[:20]
        colores_t  = {"electricidad":"#f59e0b","agua":"#3b82f6","gas":"#ef4444"}
        for lec in lecs_todas:
            c_t = colores_t.get(lec["tipo"],"#f1f5f9")
            st.markdown(f"""
            <div class="tabla-row">
                <span style="color:{c_t};font-weight:700;">{lec['tipo'].title()}</span>
                &nbsp;·&nbsp; <strong style="color:#f1f5f9;">{int(lec['valor'])} {lec['unidad']}</strong>
                &nbsp;·&nbsp; 📅 {lec['fecha']}
                &nbsp;·&nbsp; <span style="color:#64748b;font-size:0.78rem;">👤 {lec.get('usuario','-')}</span>
                {f' &nbsp;·&nbsp; <span style="color:#64748b;font-size:0.78rem;">{lec["notas"]}</span>' if lec.get("notas") else ''}
            </div>
            """,unsafe_allow_html=True)
        if not lecs_todas:
            st.info("Sin lecturas registradas.")
        st.markdown('</div>',unsafe_allow_html=True)

    # ── Función reutilizable por tipo ────────────────────────────
    def _render_tipo(tipo: str, unidad: str, color: str):
        lecturas = get_energia_lecturas(sb, tipo=tipo)
        df = _consumo_df(lecturas, tipo)

        if df.empty:
            st.info(f"Registra al menos 2 lecturas de {tipo} para ver el consumo.")
            return

        df["fecha"]  = pd.to_datetime(df["fecha"])
        df["consumo"] = df["consumo"].apply(int)

        prom_dia = int(round(df["consumo"].mean()))
        prom_sem = int(round(df["consumo"].mean() * 7))
        prom_mes = int(round(df["consumo"].mean() * 30))

        # Alerta consumo >20%
        if len(df) >= 2 and prom_dia > 0:
            ultimo = int(df.iloc[-1]["consumo"])
            if ultimo > prom_dia * 1.2:
                st.warning(f"⚠️ Último consumo diario ({int(ultimo)} {unidad}) supera >20% el promedio ({prom_dia} {unidad}).")

        c1,c2,c3 = st.columns(3)
        with c1: kpi_card("📅",f"{prom_dia} {unidad}","Prom. Diario",color)
        with c2: kpi_card("📆",f"{prom_sem} {unidad}","Prom. Semanal",color)
        with c3: kpi_card("🗓️",f"{prom_mes} {unidad}","Prom. Mensual",color)

        st.markdown("<br>",unsafe_allow_html=True)

        periodo = st.radio("Período",["30 días","12 semanas","6 meses"],horizontal=True,key=f"per_{tipo}")

        if periodo == "30 días":
            df_f = df[df["fecha"] >= pd.Timestamp.now()-pd.Timedelta(days=30)]
            x_col = "fecha"
        elif periodo == "12 semanas":
            df_f = df.copy()
            df_f["semana"] = df_f["fecha"].dt.to_period("W").dt.start_time.astype(str)
            df_f = df_f.groupby("semana")["consumo"].sum().reset_index()
            df_f.columns = ["fecha","consumo"]
            df_f = df_f.tail(12)
            x_col = "fecha"
        else:
            df_f = df.copy()
            df_f["mes"] = df_f["fecha"].dt.to_period("M").astype(str)
            df_f = df_f.groupby("mes")["consumo"].sum().reset_index()
            df_f.columns = ["fecha","consumo"]
            df_f = df_f.tail(6)
            x_col = "fecha"

        if not df_f.empty:
            fig = go.Figure(go.Scatter(
                x=df_f[x_col].astype(str), y=df_f["consumo"].apply(int),
                mode="lines+markers",
                line=dict(color=color,width=2.5),
                marker=dict(size=8,color=color,line=dict(width=2,color="#fff")),
                fill="tozeroy",fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.1)",
                name=f"Consumo {unidad}",
                text=df_f["consumo"].apply(int),textposition="top center",
            ))
            fig.update_layout(**PLOTLY_LAYOUT,height=300,xaxis_title="Fecha",yaxis_title=unidad)
            fig.update_yaxes(tickformat="d")
            st.plotly_chart(fig,use_container_width=True)

        # Comparativa mensual
        st.markdown('<div class="card">',unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 Este mes vs anterior</div>',unsafe_allow_html=True)
        hoy = date.today()
        ini_act = hoy.replace(day=1)
        ini_ant = (ini_act - timedelta(days=1)).replace(day=1)
        cons_act = int(df[df["fecha"]>=pd.Timestamp(ini_act)]["consumo"].sum())
        cons_ant = int(df[(df["fecha"]>=pd.Timestamp(ini_ant))&(df["fecha"]<pd.Timestamp(ini_act))]["consumo"].sum())
        variacion = ((cons_act-cons_ant)/cons_ant*100) if cons_ant>0 else 0
        var_c  = "#ef4444" if variacion>0 else "#10b981"
        var_sg = "▲" if variacion>0 else "▼"
        cm,ca  = st.columns(2)
        with cm: kpi_card("🗓️",f"{cons_act} {unidad}",f"Consumo {hoy.strftime('%B')}",color)
        with ca: kpi_card("↩️",f"{cons_ant} {unidad}","Mes anterior","#8b5cf6")
        st.markdown(f'<div style="text-align:center;font-size:1.1rem;font-weight:700;color:{var_c};padding:8px;">{var_sg} {abs(variacion):.1f}% vs mes anterior</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    with tab_e: _render_tipo("electricidad","kWh","#f59e0b")
    with tab_a: _render_tipo("agua","m³","#3b82f6")
    with tab_g: _render_tipo("gas","m³","#ef4444")
