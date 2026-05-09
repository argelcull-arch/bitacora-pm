"""
NOVA — modules/requerimientos.py  (v2)
Fixes: selectbox_con_otro, números enteros, CSS v2.
"""
import streamlit as st
import re
from datetime import datetime
from spellchecker import SpellChecker
from config import (seccion_titulo, badge_estado, badge_prioridad,
                    CATEGORIAS_TAREA, ESTADOS_TAREA, PRIORIDADES,
                    separador, selectbox_con_otro)
from database import get_tareas, get_area_nombres, crear_tarea, actualizar_tarea, borrar_tarea
from auth import es_admin


@st.cache_resource
def _spell():
    return SpellChecker(language="es")


def corregir(texto: str):
    spell  = _spell()
    cambios, corregidas = [], []
    for p in texto.split():
        if (p.isupper() and len(p) > 1) or re.search(r'\d', p):
            corregidas.append(p); continue
        limpia = re.sub(r'[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ]', '', p).lower()
        if not limpia:
            corregidas.append(p); continue
        c = spell.correction(limpia)
        if c and c != limpia:
            corregidas.append(c.capitalize() if p[0].isupper() else c)
            cambios.append(f"'{p}'→'{c}'")
        else:
            corregidas.append(p)
    return ' '.join(corregidas), cambios


def render(sb):
    seccion_titulo("📋", "Requerimientos", "Registro y seguimiento de trabajos de mantenimiento")

    usuario = st.session_state.get("usuario", "")
    areas   = get_area_nombres(sb)

    # ── FORMULARIO ───────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">➕ Registrar Requerimiento</div>', unsafe_allow_html=True)

    with st.form("form_req", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            area_opts = areas + ["📝 Otra (escribir)"]
            area_sel  = st.selectbox("📍 Área / Lugar *", area_opts, key="req_area")
        with c2:
            cat_opts   = CATEGORIAS_TAREA  # último elemento es "Otro"
            categoria  = st.selectbox("🏷️ Categoría", cat_opts, key="req_cat")

        # Área personalizada si elige "Otra"
        area_custom = ""
        if area_sel == "📝 Otra (escribir)":
            area_custom = st.text_input("✍️ Escribe el área / lugar", placeholder="ej: Sala de eventos, Terraza...", key="req_area_txt")

        # Categoría personalizada si elige "Otro"
        cat_custom = ""
        if categoria == "Otro":
            cat_custom = st.text_input("✍️ Especifica la categoría", placeholder="ej: Cerrajería, Fumigación...", key="req_cat_txt")

        detalle   = st.text_area("🔧 Detalle de la actividad *", height=90,
                                  placeholder="Describe claramente el problema o trabajo a realizar...",
                                  key="req_det")
        prioridad = st.radio("⚡ Prioridad", PRIORIDADES, horizontal=True, key="req_prio", index=1)
        enviado   = st.form_submit_button("💾 Guardar Requerimiento", use_container_width=True)

    if enviado:
        lugar_final = area_custom.strip() if area_sel == "📝 Otra (escribir)" else area_sel
        cat_final   = cat_custom.strip() if categoria == "Otro" else categoria

        if not lugar_final or not detalle.strip():
            st.warning("⚠️ Área y detalle son obligatorios.")
        elif categoria == "Otro" and not cat_final:
            st.warning("⚠️ Especifica la categoría.")
        else:
            det_ok, cambios = corregir(detalle)
            ok = crear_tarea(sb, {
                "usuario":   usuario,
                "lugar":     lugar_final,
                "detalle":   det_ok,
                "categoria": cat_final,
                "prioridad": prioridad,
            })
            if ok:
                msg = "✅ Requerimiento guardado correctamente."
                if cambios:
                    msg += f" Correcciones ortográficas: {', '.join(cambios[:3])}"
                st.success(msg)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── FILTROS ──────────────────────────────────────────────────
    with st.expander("🔍 Filtros de búsqueda", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        f_area = fc1.selectbox("Área", ["Todas"] + areas, key="f_area")
        f_cat  = fc2.selectbox("Categoría", ["Todas"] + CATEGORIAS_TAREA[:-1], key="f_cat")
        f_prio = fc3.selectbox("Prioridad", ["Todas"] + PRIORIDADES, key="f_prio")
        f_est  = fc4.selectbox("Estado", ["Todos"] + ESTADOS_TAREA, key="f_est")

    # ── LISTA ────────────────────────────────────────────────────
    filtros = {} if es_admin() else {"usuario": usuario}
    tareas  = get_tareas(sb, filtros)

    if f_area != "Todas":  tareas = [t for t in tareas if t.get("lugar") == f_area]
    if f_cat  != "Todas":  tareas = [t for t in tareas if t.get("categoria") == f_cat]
    if f_prio != "Todas":  tareas = [t for t in tareas if t.get("prioridad") == f_prio]
    if f_est  != "Todos":  tareas = [t for t in tareas if t.get("estado") == f_est]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">📋 Lista de Requerimientos &nbsp;<span class="badge badge-azul">{int(len(tareas))}</span></div>',
                unsafe_allow_html=True)

    if not tareas:
        st.info("Sin requerimientos con los filtros seleccionados.")
    else:
        POR_PAG = 20
        total_p = max(1, (len(tareas) + POR_PAG - 1) // POR_PAG)
        pag = st.number_input("Página", min_value=1, max_value=total_p, value=1, step=1,
                               key="req_pag", label_visibility="collapsed")
        tareas_p = tareas[(pag-1)*POR_PAG : pag*POR_PAG]

        for t in tareas_p:
            hora = t.get("created_at","")[:16].replace("T"," ")
            tid  = t.get("id")
            prio = t.get("prioridad","Media")
            borde_c = {"Alta":"#ef4444","Media":"#f59e0b","Baja":"#10b981"}.get(prio,"#3b82f6")

            col_info, col_est, col_del = st.columns([6, 2, 1])
            with col_info:
                st.markdown(f"""
                <div class="tabla-row" style="border-left:3px solid {borde_c};">
                    <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:5px;">
                        <span style="font-weight:700;color:#93c5fd;font-size:0.88rem;">📍 {t.get('lugar','-')}</span>
                        {badge_prioridad(prio)} {badge_estado(t.get('estado','Abierto'))}
                        <span class="badge badge-purpura">{t.get('categoria','General')}</span>
                    </div>
                    <div style="font-size:0.9rem;color:#f1f5f9;line-height:1.4;">{t.get('detalle','')}</div>
                    <div style="font-size:0.72rem;color:#64748b;margin-top:5px;">
                        👤 {t.get('usuario','-')} &nbsp;·&nbsp; 🕐 {hora}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_est:
                nuevo_est = st.selectbox(
                    "Estado", ESTADOS_TAREA,
                    index=ESTADOS_TAREA.index(t.get("estado","Abierto")) if t.get("estado") in ESTADOS_TAREA else 0,
                    key=f"est_{tid}", label_visibility="collapsed",
                )
                if nuevo_est != t.get("estado"):
                    if actualizar_tarea(sb, tid, {"estado": nuevo_est}):
                        st.rerun()
            with col_del:
                if es_admin():
                    st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                    if st.button("🗑", key=f"del_{tid}", help="Eliminar"):
                        if borrar_tarea(sb, tid):
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        separador()
        st.caption(f"Página {int(pag)} de {int(total_p)} · {int(len(tareas))} requerimientos en total")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── RESUMEN COPIABLE ─────────────────────────────────────────
    tareas_usuario = get_tareas(sb, {} if es_admin() else {"usuario": usuario})
    if tareas_usuario:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 Resumen del Día para Copiar</div>', unsafe_allow_html=True)
        resumen = " / ".join(f"{t['lugar']}: {t['detalle']}" for t in tareas_usuario[:30])
        st.markdown(f"""
        <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);
                    border-radius:10px;padding:14px;color:#6ee7b7;font-size:0.9rem;
                    line-height:1.6;margin-bottom:12px;">{resumen}</div>
        <textarea id="rsm_txt" style="position:absolute;left:-9999px;opacity:0;" readonly>{resumen}</textarea>
        <button onclick="
            navigator.clipboard.writeText(document.getElementById('rsm_txt').value)
            .then(()=>{{var b=document.getElementById('cpbtn');b.innerText='✅ ¡Copiado!';
                b.style.background='linear-gradient(135deg,#10b981,#059669)';
                setTimeout(()=>{{b.innerText='📋 Copiar Resumen';
                    b.style.background='linear-gradient(135deg,#3b82f6,#2563eb)';}},2500);}})
            .catch(()=>{{var t=document.getElementById('rsm_txt');t.style.position='static';
                t.select();document.execCommand('copy');t.style.position='absolute';}});
        " id="cpbtn" style="width:100%;padding:11px;font-size:0.92rem;font-weight:700;
            font-family:'Inter',sans-serif;cursor:pointer;border:none;border-radius:10px;
            background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;
            box-shadow:0 4px 14px rgba(59,130,246,0.35);transition:all .2s ease;">
            📋 Copiar Resumen
        </button>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
