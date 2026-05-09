"""
NOVA — modules/activos.py
Módulo 5: Registro y seguimiento de activos y equipos del hotel.
"""
import streamlit as st
from datetime import date, datetime
from config import (seccion_titulo, badge_estado, CATEGORIAS_ACTIVOS, separador)
from database import (get_activos, get_area_nombres, crear_activo,
                      actualizar_activo, get_historial_activo, agregar_historial_activo)
from auth import es_admin


def _indicador_mant(proximo: str) -> str:
    """Retorna emoji indicador según fecha de próximo mantenimiento."""
    if not proximo:
        return "⚪"
    try:
        dias = (date.fromisoformat(proximo) - date.today()).days
        if dias < 0:     return "🔴"
        if dias <= 7:    return "🟡"
        return "🟢"
    except Exception:
        return "⚪"


def render(sb):
    seccion_titulo("🔧", "Activos & Equipos", "Inventario de equipos, estados y mantenimientos")

    areas   = get_area_nombres(sb)
    activos = get_activos(sb)

    tab_lista, tab_nuevo, tab_hist = st.tabs(["🗂️ Activos", "➕ Nuevo Activo", "📖 Historial"])

    # ── TAB 1: LISTA ───────────────────────────────────────────
    with tab_lista:
        # Filtros
        c1, c2 = st.columns(2)
        f_cat = c1.selectbox("Categoría", ["Todas"] + CATEGORIAS_ACTIVOS, key="ac_fcat")
        f_est = c2.selectbox("Estado",    ["Todos", "Operativo", "En Reparación", "Fuera de Servicio"], key="ac_fest")

        activos_f = activos
        if f_cat != "Todas": activos_f = [a for a in activos_f if a.get("categoria") == f_cat]
        if f_est != "Todos": activos_f = [a for a in activos_f if a.get("estado") == f_est]

        if not activos_f:
            st.info("Sin activos con los filtros seleccionados.")
        else:
            for row_s in range(0, len(activos_f), 2):
                cols = st.columns(2)
                for j, a in enumerate(activos_f[row_s:row_s+2]):
                    with cols[j]:
                        aid      = a["id"]
                        area_n   = a.get("areas",{}).get("nombre","-") if isinstance(a.get("areas"),dict) else "-"
                        ind_mant = _indicador_mant(a.get("proximo_mantenimiento"))
                        est_c    = {"Operativo":"#38a169","En Reparación":"#d69e2e","Fuera de Servicio":"#e53e3e"}.get(a.get("estado","Operativo"),"#4a90e2")

                        st.markdown(f"""
                        <div class="card" style="border-top:3px solid {est_c};margin-bottom:12px;">
                            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                                <div>
                                    <div style="font-weight:800;font-size:0.98rem;color:#e2e8f0;">{a['nombre']}</div>
                                    <div style="font-size:0.78rem;color:#94a3b8;margin-top:2px;">
                                        {a.get('marca','-')} {a.get('modelo','-')} · S/N: {a.get('serial','-')}
                                    </div>
                                </div>
                                {badge_estado(a.get('estado','Operativo'))}
                            </div>
                            <div style="margin:10px 0;display:flex;gap:12px;flex-wrap:wrap;font-size:0.8rem;color:#94a3b8;">
                                <span>📍 {area_n}</span>
                                <span>🏷️ {a.get('categoria','-')}</span>
                                <span>{ind_mant} Próx. mant: {a.get('proximo_mantenimiento','-') or '-'}</span>
                            </div>
                            <div style="font-size:0.78rem;color:#94a3b8;">
                                Último mant: {a.get('ultimo_mantenimiento','-') or '-'}
                                {' · ' + a.get('desc_ultimo_mant','') if a.get('desc_ultimo_mant') else ''}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Acciones
                        ca, cb = st.columns(2)
                        with ca:
                            nuevo_est = st.selectbox(
                                "Estado", ["Operativo","En Reparación","Fuera de Servicio"],
                                index=["Operativo","En Reparación","Fuera de Servicio"].index(a.get("estado","Operativo")),
                                key=f"ac_est_{aid}", label_visibility="collapsed"
                            )
                            if nuevo_est != a.get("estado"):
                                actualizar_activo(sb, aid, {"estado": nuevo_est})
                                st.rerun()
                        with cb:
                            if st.button("📖 Ver historial", key=f"ac_hist_{aid}"):
                                st.session_state["hist_activo_id"]     = aid
                                st.session_state["hist_activo_nombre"] = a["nombre"]
                                st.rerun()

    # ── TAB 2: NUEVO ACTIVO ────────────────────────────────────
    with tab_nuevo:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("form_activo", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nombre   = c1.text_input("Nombre del equipo *", key="na_nom")
            categoria = c2.selectbox("Categoría", CATEGORIAS_ACTIVOS, key="na_cat")
            c3, c4  = st.columns(2)
            marca   = c3.text_input("Marca", key="na_marca")
            modelo  = c4.text_input("Modelo", key="na_modelo")
            c5, c6  = st.columns(2)
            serial  = c5.text_input("N° de Serie", key="na_serial")
            area_sel = c6.selectbox("Área / Ubicación", areas + ["Otra"], key="na_area")
            c7, c8  = st.columns(2)
            f_inst   = c7.date_input("Fecha instalación", value=None, key="na_finst")
            f_prox   = c8.date_input("Próx. mantenimiento", value=None, key="na_fprox")
            estado  = st.selectbox("Estado inicial", ["Operativo","En Reparación","Fuera de Servicio"], key="na_est")
            notas   = st.text_area("Notas", height=60, key="na_notas")
            submit  = st.form_submit_button("💾 Registrar Activo", use_container_width=True)

        if submit:
            if not nombre.strip():
                st.warning("⚠️ El nombre es obligatorio.")
            else:
                # area_id
                try:
                    r = sb.table("areas").select("id").eq("nombre", area_sel).execute()
                    area_id = r.data[0]["id"] if r.data else None
                except Exception:
                    area_id = None

                ok = crear_activo(sb, {
                    "nombre":                nombre.strip(),
                    "categoria":             categoria,
                    "marca":                 marca.strip(),
                    "modelo":                modelo.strip(),
                    "serial":                serial.strip(),
                    "area_id":               area_id,
                    "fecha_instalacion":     f_inst.isoformat() if f_inst else None,
                    "proximo_mantenimiento": f_prox.isoformat() if f_prox else None,
                    "estado":                estado,
                    "notas":                 notas.strip(),
                })
                if ok:
                    st.success("✅ Activo registrado.")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 3: HISTORIAL ─────────────────────────────────────
    with tab_hist:
        aid_sel = st.session_state.get("hist_activo_id")
        nombre_sel = st.session_state.get("hist_activo_nombre","")

        # Selector de activo
        activo_nombres = [a["nombre"] for a in activos]
        if activo_nombres:
            sel = st.selectbox("Seleccionar equipo", activo_nombres,
                               index=activo_nombres.index(nombre_sel) if nombre_sel in activo_nombres else 0,
                               key="ac_hist_sel")
            aid_sel = next((a["id"] for a in activos if a["nombre"] == sel), None)
        
        if aid_sel:
            historial = get_historial_activo(sb, aid_sel)
            
            # Formulario para agregar entrada de historial
            with st.expander("➕ Registrar Mantenimiento"):
                with st.form(f"form_hist_{aid_sel}", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    f_hfecha = c1.date_input("Fecha", value=date.today(), key=f"hf_{aid_sel}")
                    tipo_trab = c2.text_input("Tipo de trabajo", key=f"ht_{aid_sel}")
                    desc_h    = st.text_area("Descripción", height=70, key=f"hd_{aid_sel}")
                    c3, c4   = st.columns(2)
                    realizado = c3.text_input("Realizado por", key=f"hr_{aid_sel}")
                    costo_h   = c4.number_input("Costo (opcional)", min_value=0.0, value=0.0, key=f"hc_{aid_sel}")
                    submit_h  = st.form_submit_button("💾 Guardar")
                if submit_h:
                    ok_h = agregar_historial_activo(sb, {
                        "activo_id":    aid_sel,
                        "fecha":        f_hfecha.isoformat(),
                        "tipo_trabajo": tipo_trab,
                        "descripcion":  desc_h,
                        "realizado_por":realizado,
                        "costo":        costo_h if costo_h > 0 else None,
                    })
                    if ok_h:
                        # Actualizar último mantenimiento en activo
                        actualizar_activo(sb, aid_sel, {
                            "ultimo_mantenimiento": f_hfecha.isoformat(),
                            "desc_ultimo_mant":     desc_h[:120],
                        })
                        st.success("✅ Mantenimiento registrado.")
                        st.rerun()

            # Lista de historial
            if historial:
                for h in historial:
                    st.markdown(f"""
                    <div class="tabla-row" style="background:rgba(255,255,255,0.04);border-radius:8px;margin-bottom:6px;padding:10px 14px;">
                        <div style="font-weight:700;color:#90cdf4;font-size:0.85rem;">
                            📅 {h.get('fecha','-')} &nbsp;·&nbsp; {h.get('tipo_trabajo','-')}
                        </div>
                        <div style="font-size:0.88rem;color:#e2e8f0;margin:4px 0;">{h.get('descripcion','')}</div>
                        <div style="font-size:0.75rem;color:#94a3b8;">
                            👤 {h.get('realizado_por','-')}
                            {' &nbsp;·&nbsp; 💰 $' + f"{h['costo']:,.2f}" if h.get('costo') else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Sin historial de mantenimientos para este equipo.")
        else:
            st.info("Selecciona un equipo para ver su historial.")
