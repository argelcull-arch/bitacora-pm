"""
NOVA — modules/energia.py
Módulo 7: Registro y análisis de consumos de energía, agua y gas.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date, timedelta
from config import seccion_titulo, kpi_card, COLOR, PLOTLY_LAYOUT, PLOTLY_COLORS, TIPOS_ENERGIA, UNIDADES_ENERGIA
from database import get_energia_lecturas, registrar_lectura_energia


def _consumo_df(lecturas: list, tipo: str) -> pd.DataFrame:
    """Convierte lecturas en DataFrame con consumo diario (diferencia entre lecturas)."""
    datos = sorted([l for l in lecturas if l.get("tipo") == tipo], key=lambda x: x["fecha"])
    if len(datos) < 2:
        return pd.DataFrame()
    rows = []
    for i in range(1, len(datos)):
        consumo = datos[i]["valor"] - datos[i-1]["valor"]
        if consumo >= 0:
            rows.append({"fecha": datos[i]["fecha"], "consumo": consumo})
    return pd.DataFrame(rows)


def render(sb):
    seccion_titulo("💡", "Energía & Consumos", "Monitoreo de electricidad, agua y gas")

    usuario = st.session_state.get("usuario","")

    tab_reg, tab_elec, tab_agua, tab_gas = st.tabs(
        ["📝 Registrar Lectura", "⚡ Electricidad", "💧 Agua", "🔥 Gas"]
    )

    # ── TAB 1: REGISTRO ─────────────────────────────────────────
    with tab_reg:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📝 Nueva Lectura de Medidor</div>', unsafe_allow_html=True)
        with st.form("form_energia", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            tipo    = c1.selectbox("Tipo", TIPOS_ENERGIA, key="en_tipo",
                                   format_func=lambda x: {"electricidad":"⚡ Electricidad","agua":"💧 Agua","gas":"🔥 Gas"}.get(x,x))
            valor   = c2.number_input("Lectura del medidor", min_value=0.0, format="%.2f", key="en_val")
            f_lec   = c3.date_input("Fecha", value=date.today(), key="en_fecha")
            notas   = st.text_input("Notas (opcional)", key="en_notas")
            submit  = st.form_submit_button("💾 Registrar Lectura", use_container_width=True)
        if submit:
            if valor <= 0:
                st.warning("⚠️ Ingresa un valor mayor a 0.")
            else:
                ok = registrar_lectura_energia(sb, {
                    "tipo":   tipo,
                    "valor":  valor,
                    "unidad": UNIDADES_ENERGIA.get(tipo,""),
                    "fecha":  f_lec.isoformat(),
                    "usuario":usuario,
                    "notas":  notas.strip(),
                })
                if ok:
                    st.success(f"✅ Lectura de {tipo} registrada.")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Últimas lecturas
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🕐 Últimas Lecturas</div>', unsafe_allow_html=True)
        todas_lecs = get_energia_lecturas(sb)
        ultimas    = sorted(todas_lecs, key=lambda x: x.get("fecha",""), reverse=True)[:15]
        colores_t  = {"electricidad":"#f6e05e","agua":"#90cdf4","gas":"#fc8181"}
        for lec in ultimas:
            c_t = colores_t.get(lec["tipo"],"#e2e8f0")
            st.markdown(f"""
            <div class="tabla-row">
                <span style="color:{c_t};font-weight:700;">{lec['tipo'].title()}</span>
                &nbsp;·&nbsp; <strong>{lec['valor']:.2f} {lec['unidad']}</strong>
                &nbsp;·&nbsp; 📅 {lec['fecha']}
                &nbsp;·&nbsp; <span style="color:#94a3b8;font-size:0.78rem;">👤 {lec.get('usuario','-')}</span>
                {f' &nbsp;·&nbsp; <span style="color:#94a3b8;font-size:0.78rem;">{lec["notas"]}</span>' if lec.get("notas") else ''}
            </div>
            """, unsafe_allow_html=True)
        if not ultimas:
            st.info("Sin lecturas registradas aún.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Función reutilizable por tipo ────────────────────────────
    def _render_tipo(tipo: str, icono: str, unidad: str, color: str):
        lecturas = get_energia_lecturas(sb, tipo=tipo)
        df       = _consumo_df(lecturas, tipo)

        if df.empty:
            st.info(f"Sin suficientes lecturas de {tipo} para calcular consumo. Registra al menos 2.")
            return

        df["fecha"]       = pd.to_datetime(df["fecha"])
        df["consumo"]     = df["consumo"].round(2)
        consumo_prom_dia  = df["consumo"].mean()
        consumo_prom_sem  = consumo_prom_dia * 7
        consumo_prom_mes  = consumo_prom_dia * 30

        # Alerta 20%
        if not df.empty and len(df) >= 2:
            ultimo_cons = df.iloc[-1]["consumo"]
            if ultimo_cons > consumo_prom_dia * 1.2 and consumo_prom_dia > 0:
                st.warning(f"⚠️ El último consumo diario ({ultimo_cons:.1f} {unidad}) supera en >20% el promedio ({consumo_prom_dia:.1f} {unidad}).")

        # KPIs
        c1, c2, c3 = st.columns(3)
        with c1: kpi_card("📅", f"{consumo_prom_dia:.1f} {unidad}", "Prom. Diario", color)
        with c2: kpi_card("📆", f"{consumo_prom_sem:.1f} {unidad}", "Prom. Semanal", color)
        with c3: kpi_card("🗓️", f"{consumo_prom_mes:.0f} {unidad}", "Prom. Mensual", color)

        st.markdown("<br>", unsafe_allow_html=True)

        # Período
        periodo = st.radio("Período", ["Últimos 30 días","Últimas 12 semanas","Últimos 6 meses"],
                           horizontal=True, key=f"en_per_{tipo}")

        if periodo == "Últimos 30 días":
            df_f = df[df["fecha"] >= pd.Timestamp.now() - pd.Timedelta(days=30)]
            x_col = "fecha"
            title_x = "Fecha"
        elif periodo == "Últimas 12 semanas":
            df_f = df.copy()
            df_f["semana"] = df_f["fecha"].dt.to_period("W").dt.start_time.astype(str)
            df_f = df_f.groupby("semana")["consumo"].sum().reset_index()
            df_f.columns = ["fecha","consumo"]
            df_f = df_f.tail(12)
            x_col = "fecha"; title_x = "Semana"
        else:
            df_f = df.copy()
            df_f["mes"] = df_f["fecha"].dt.to_period("M").astype(str)
            df_f = df_f.groupby("mes")["consumo"].sum().reset_index()
            df_f.columns = ["fecha","consumo"]
            df_f = df_f.tail(6)
            x_col = "fecha"; title_x = "Mes"

        if not df_f.empty:
            fig = go.Figure(go.Scatter(
                x=df_f[x_col].astype(str), y=df_f["consumo"],
                mode="lines+markers",
                line=dict(color=color, width=2.5),
                marker=dict(size=7, color=color),
                fill="tozeroy", fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.1)",
                name=f"Consumo {unidad}",
            ))
            fig.update_layout(**PLOTLY_LAYOUT, height=300,
                              xaxis_title=title_x, yaxis_title=unidad)
            st.plotly_chart(fig, use_container_width=True)

        # Comparativa mes actual vs anterior
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 Comparativa Mensual</div>', unsafe_allow_html=True)
        hoy = date.today()
        ini_mes_act  = hoy.replace(day=1)
        ini_mes_ant  = (ini_mes_act - pd.Timedelta(days=1)).replace(day=1)
        cons_act = df[df["fecha"] >= pd.Timestamp(ini_mes_act)]["consumo"].sum()
        cons_ant = df[(df["fecha"] >= pd.Timestamp(ini_mes_ant)) &
                      (df["fecha"] < pd.Timestamp(ini_mes_act))]["consumo"].sum()
        variacion = ((cons_act - cons_ant) / cons_ant * 100) if cons_ant > 0 else 0
        var_color = "#e53e3e" if variacion > 0 else "#38a169"
        var_signo = "▲" if variacion > 0 else "▼"

        cm, ca = st.columns(2)
        with cm:
            kpi_card("🗓️", f"{cons_act:.1f} {unidad}", f"Consumo {hoy.strftime('%B')}", color)
        with ca:
            kpi_card("↩️", f"{cons_ant:.1f} {unidad}", f"Mes anterior", "#805ad5")
        st.markdown(f"""
        <div style="text-align:center;font-size:1.1rem;font-weight:700;color:{var_color};padding:8px;">
            {var_signo} {abs(variacion):.1f}% vs mes anterior
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_elec:
        _render_tipo("electricidad", "⚡", "kWh", COLOR["warning"])
    with tab_agua:
        _render_tipo("agua", "💧", "m³", COLOR["primary"])
    with tab_gas:
        _render_tipo("gas", "🔥", "m³", COLOR["danger"])
