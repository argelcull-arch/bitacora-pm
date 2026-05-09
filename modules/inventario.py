"""
NOVA — modules/inventario.py  (v2)
Módulo 4: Gestión de inventario. Fixes: enteros, step=1, CSS v2.
"""
import streamlit as st
from config import (seccion_titulo, stock_bar, badge_prioridad,
                    CATEGORIAS_INVENTARIO, separador)
from database import (get_inventario_items, get_movimientos,  # noqa
                      crear_item_inventario, actualizar_stock)
from auth import es_admin


def render(sb):
    seccion_titulo("📦", "Inventario", "Control de materiales, repuestos y herramientas")

    usuario = st.session_state.get("usuario","")
    items   = get_inventario_items(sb)

    # ── BANNER DE ALERTAS ──────────────────────────────────────
    criticos = [i for i in items if i["stock_actual"] < i["stock_minimo"]]
    if criticos:
        ping_html = '<span class="ping ping-red" style="display:inline-block;margin-right:6px;"></span>'
        st.markdown(f"""
        <div style="background:rgba(229,62,62,0.15);border:1px solid rgba(229,62,62,0.4);
                    border-radius:12px;padding:14px 18px;margin-bottom:16px;">
            <div style="font-weight:700;color:#fc8181;margin-bottom:6px;">
                {ping_html} ⚠️ {int(len(criticos))} ítem(s) bajo el stock mínimo
            </div>
            {" ".join(f'<span style="font-size:0.82rem;color:#f1f5f9;margin-right:14px;">• {i["nombre"]} ({int(i["stock_actual"])}/{int(i["stock_minimo"])} {i["unidad"]})</span>' for i in criticos)}
        </div>
        """, unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────
    tab_cat, tab_mov, tab_nuevo = st.tabs(["📦 Catálogo", "📑 Movimientos", "➕ Nuevo Ítem"])

    # ── TAB 1: CATÁLOGO ──────────────────────────────────────
    with tab_cat:
        if not items:
            st.info("Sin ítems de inventario registrados.")
        else:
            f_cat = st.selectbox("Filtrar por categoría", ["Todas"] + CATEGORIAS_INVENTARIO, key="inv_fcat")
            items_f = [i for i in items if f_cat == "Todas" or i["categoria"] == f_cat]

            # Grid de cards (3 columnas)
            for row_start in range(0, len(items_f), 3):
                cols = st.columns(3)
                for j, item in enumerate(items_f[row_start:row_start+3]):
                    with cols[j]:
                        iid  = item["id"]
                        pct  = (item["stock_actual"] / item["stock_minimo"] * 100) if item["stock_minimo"] > 0 else 100
                        nivel_color = "#38a169" if pct >= 100 else ("#d69e2e" if pct >= 50 else "#e53e3e")
                        st.markdown(f"""
                        <div class="card" style="margin-bottom:12px;border-top:3px solid {nivel_color};">
                            <div style="font-weight:700;font-size:0.95rem;color:#e2e8f0;margin-bottom:4px;">
                                {item['nombre']}
                            </div>
                            <div style="font-size:0.75rem;color:#94a3b8;margin-bottom:8px;">
                                {item['categoria']} &nbsp;·&nbsp; 📍 {item.get('ubicacion','-')}
                            </div>
                            {stock_bar(item['stock_actual'], item['stock_minimo'])}
                        </div>
                        """, unsafe_allow_html=True)

                        # Botones entrada/salida
                        c_e, c_s = st.columns(2)
                        with c_e:
                            st.markdown('<div class="btn-success">', unsafe_allow_html=True)
                            if st.button("＋ Entrada", key=f"ent_{iid}", use_container_width=True):
                                st.session_state[f"mov_tipo_{iid}"] = "entrada"
                                st.session_state[f"mov_open_{iid}"] = True
                            st.markdown('</div>', unsafe_allow_html=True)
                        with c_s:
                            st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                            if st.button("－ Salida", key=f"sal_{iid}", use_container_width=True):
                                st.session_state[f"mov_tipo_{iid}"] = "salida"
                                st.session_state[f"mov_open_{iid}"] = True
                            st.markdown('</div>', unsafe_allow_html=True)

                        # Formulario de movimiento inline
                        if st.session_state.get(f"mov_open_{iid}"):
                            tipo_mov = st.session_state.get(f"mov_tipo_{iid}", "entrada")
                            with st.form(f"form_mov_{iid}"):
                                cant  = st.number_input("Cantidad", min_value=1, value=1, step=1, format="%d", key=f"cant_{iid}")
                                motiv = st.text_input("Motivo", key=f"motiv_{iid}")
                                ok_m  = st.form_submit_button("✅ Confirmar")
                            if ok_m:
                                nuevo = item["stock_actual"] + cant if tipo_mov == "entrada" else item["stock_actual"] - cant
                                if nuevo < 0:
                                    st.error("❌ Stock insuficiente.")
                                else:
                                    actualizar_stock(sb, iid, nuevo, tipo_mov, cant, usuario, motiv)
                                    st.session_state.pop(f"mov_open_{iid}", None)
                                    st.success("✅ Movimiento registrado.")
                                    st.rerun()

    # ── TAB 2: MOVIMIENTOS ────────────────────────────────────
    with tab_mov:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📑 Historial de Movimientos</div>', unsafe_allow_html=True)

        nombres_items = {i["id"]: i["nombre"] for i in items}
        sel_item = st.selectbox("Filtrar por ítem", ["Todos"] + [i["nombre"] for i in items], key="inv_sel_item")
        item_id_f = next((i["id"] for i in items if i["nombre"] == sel_item), None) if sel_item != "Todos" else None

        movs = get_movimientos(sb, item_id=item_id_f)
        if not movs:
            st.info("Sin movimientos registrados.")
        else:
            for m in movs[:50]:
                iname = m.get("inventario_items",{}).get("nombre","-") if isinstance(m.get("inventario_items"),dict) else "-"
                tipo_color = "#68d391" if m["tipo"] == "entrada" else "#fc8181"
                signo = "+" if m["tipo"] == "entrada" else "-"
                st.markdown(f"""
                <div class="tabla-row">
                    <span style="color:{tipo_color};font-weight:700;">{signo}{m['cantidad']:.0f}</span>
                    &nbsp;·&nbsp; <strong>{iname}</strong>
                    &nbsp;·&nbsp; <span style="color:#94a3b8;">{m.get('motivo','-')}</span>
                    &nbsp;·&nbsp; <span style="color:#94a3b8;font-size:0.78rem;">👤 {m.get('usuario','-')} &nbsp; {m.get('created_at','')[:16].replace('T',' ')}</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 3: NUEVO ÍTEM ─────────────────────────────────────
    with tab_nuevo:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">➕ Agregar Ítem al Inventario</div>', unsafe_allow_html=True)
        with st.form("form_new_item", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nombre   = c1.text_input("Nombre del ítem", key="ni_nom")
            cat      = c2.selectbox("Categoría", CATEGORIAS_INVENTARIO, key="ni_cat")
            c3, c4   = st.columns(2)
            ubicacion = c3.text_input("Ubicación física", key="ni_ubic")
            unidad   = c4.text_input("Unidad de medida", value="unidad", key="ni_uni")
            c5, c6   = st.columns(2)
            stock_ini = c5.number_input("Stock inicial", min_value=0, value=0, step=1, format="%d", key="ni_stk")
            stock_min = c6.number_input("Stock mínimo", min_value=0, value=5, step=1, format="%d", key="ni_min")
            desc     = st.text_area("Descripción (opcional)", height=60, key="ni_desc")
            submit   = st.form_submit_button("💾 Crear Ítem", use_container_width=True)

        if submit:
            if not nombre.strip():
                st.warning("⚠️ El nombre es obligatorio.")
            else:
                ok = crear_item_inventario(sb, {
                    "nombre":       nombre.strip(),
                    "categoria":    cat,
                    "descripcion":  desc.strip(),
                    "ubicacion":    ubicacion.strip(),
                    "stock_actual": stock_ini,
                    "stock_minimo": stock_min,
                    "unidad":       unidad.strip() or "unidad",
                    "activo":       True,
                })
                if ok:
                    st.success("✅ Ítem creado.")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
