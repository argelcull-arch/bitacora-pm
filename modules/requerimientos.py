"""
NOVA — modules/requerimientos.py
Módulo 2: Registro y gestión de requerimientos de mantenimiento.
"""
import streamlit as st
import re
from datetime import datetime
from spellchecker import SpellChecker
from config import (seccion_titulo, badge_estado, badge_prioridad,
                    CATEGORIAS_TAREA, ESTADOS_TAREA, PRIORIDADES, separador)
from database import get_tareas, get_area_nombres, crear_tarea, actualizar_tarea, borrar_tarea
from auth import es_admin


# ── Corrector ortográfico ──────────────────────────────────────
@st.cache_resource
def _spell():
    return SpellChecker(language="es")


def corregir(texto: str):
    spell = _spell()
    palabras, cambios, corregidas = texto.split(), [], []
    for p in palabras:
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
    nombre  = st.session_state.get("nombre", "")
    areas   = get_area_nombres(sb)

    # ── FORMULARIO ───────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">➕ Registrar Requerimiento</div>', unsafe_allow_html=True)

    with st.form("form_req", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            area_opts = areas + ["📝 Otra (escribir)"]
            area_sel  = st.selectbox("📍 Área / Lugar", area_opts, key="req_area")
        with c2:
            categoria = st.selectbox("🏷️ Categoría", CATEGORIAS_TAREA, key="req_cat")

        if area_sel == "📝 Otra (escribir)":
            area_manual = st.text_input("✍️ Escribe el área", key="req_area_manual")
        else:
            area_manual = ""

        detalle  = st.text_area("🔧 Detalle de la actividad", height=90,
                                placeholder="Describe claramente el problema o trabajo...", key="req_det")
        prioridad = st.radio("⚡ Prioridad", PRIORIDADES, horizontal=True, key="req_prio", index=1)

        enviado = st.form_submit_button("💾 Guardar Requerimiento", use_container_width=True)

    if enviado:
        lugar_final = area_manual.strip() if area_sel == "📝 Otra (escribir)" else area_sel
        if not lugar_final or not detalle.strip():
            st.warning("⚠️ Completa todos los campos obligatorios.")
        else:
            det_ok, cambios = corregir(detalle)
            ok = crear_tarea(sb, {
                "usuario":   usuario,
                "lugar":     lugar_final,
                "detalle":   det_ok,
                "categoria": categoria,
                "prioridad": prioridad,
            })
            if ok:
                msg = "✅ Requerimiento guardado."
                if cambios:
                    msg += f" Correcciones: {', '.join(cambios)}"
                st.success(msg)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── FILTROS ──────────────────────────────────────────────────
    with st.expander("🔍 Filtros", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        f_area  = fc1.selectbox("Área", ["Todas"] + areas, key="f_area")
        f_cat   = fc2.selectbox("Categoría", ["Todas"] + CATEGORIAS_TAREA, key="f_cat")
        f_prio  = fc3.selectbox("Prioridad", ["Todas"] + PRIORIDADES, key="f_prio")
        f_est   = fc4.selectbox("Estado", ["Todos"] + ESTADOS_TAREA, key="f_est")

    # ── LISTA ────────────────────────────────────────────────────
    filtros = {}
    if not es_admin():
        filtros["usuario"] = usuario

    tareas = get_tareas(sb, filtros)

    # Aplicar filtros locales
    if f_area  != "Todas":  tareas = [t for t in tareas if t.get("lugar") == f_area]
    if f_cat   != "Todas":  tareas = [t for t in tareas if t.get("categoria") == f_cat]
    if f_prio  != "Todas":  tareas = [t for t in tareas if t.get("prioridad") == f_prio]
    if f_est   != "Todos":  tareas = [t for t in tareas if t.get("estado") == f_est]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">📋 Requerimientos &nbsp;<span class="badge badge-azul">{len(tareas)}</span></div>',
                unsafe_allow_html=True)

    if not tareas:
        st.info("Sin requerimientos con los filtros seleccionados.")
    else:
        # Paginación
        POR_PAG = 20
        total_pags = max(1, (len(tareas) + POR_PAG - 1) // POR_PAG)
        pag = st.number_input("Página", min_value=1, max_value=total_pags, value=1, key="req_pag")
        inicio = (pag - 1) * POR_PAG
        tareas_pag = tareas[inicio:inicio + POR_PAG]

        for t in tareas_pag:
            hora = t.get("created_at", "")[:16].replace("T", " ")
            tid  = t.get("id")
            col_info, col_acc = st.columns([5, 1])
            with col_info:
                st.markdown(f"""
                <div class="kanban-card" style="border-color:{'#e53e3e' if t.get('prioridad')=='Alta' else ('#d69e2e' if t.get('prioridad')=='Media' else '#38a169')};">
                    <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:6px;">
                        <span style="font-weight:700;color:#90cdf4;font-size:0.88rem;">📍 {t.get('lugar','-')}</span>
                        {badge_prioridad(t.get('prioridad','Media'))}
                        {badge_estado(t.get('estado','Abierto'))}
                        <span class="badge badge-purpura">{t.get('categoria','General')}</span>
                    </div>
                    <div style="font-size:0.92rem;color:#e2e8f0;">{t.get('detalle','')}</div>
                    <div style="font-size:0.72rem;color:#94a3b8;margin-top:6px;">
                        👤 {t.get('usuario','-')} &nbsp;·&nbsp; 🕐 {hora}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_acc:
                nuevo_est = st.selectbox(
                    "Estado", ESTADOS_TAREA,
                    index=ESTADOS_TAREA.index(t.get("estado","Abierto")) if t.get("estado") in ESTADOS_TAREA else 0,
                    key=f"est_{tid}", label_visibility="collapsed"
                )
                if nuevo_est != t.get("estado"):
                    if actualizar_tarea(sb, tid, {"estado": nuevo_est}):
                        st.success("✅")
                        st.rerun()
                if es_admin():
                    st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{tid}", help="Eliminar"):
                        if borrar_tarea(sb, tid):
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        separador()
        st.caption(f"Página {pag} de {total_pags} · {len(tareas)} requerimientos en total")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── RESUMEN COPIABLE ─────────────────────────────────────────
    tareas_hoy = get_tareas(sb, {"usuario": usuario} if not es_admin() else {})
    if tareas_hoy:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 Resumen para Copiar</div>', unsafe_allow_html=True)
        resumen = " / ".join(f"{t['lugar']}: {t['detalle']}" for t in tareas_hoy)
        st.markdown(f"""
        <div style="background:rgba(56,161,105,0.1);border:1px solid rgba(56,161,105,0.3);border-radius:10px;
                    padding:14px;color:#68d391;font-size:0.92rem;line-height:1.6;margin-bottom:12px;">
            {resumen}
        </div>
        <textarea id="rsm" style="position:absolute;left:-9999px;opacity:0;" readonly>{resumen}</textarea>
        <button onclick="
            navigator.clipboard.writeText(document.getElementById('rsm').value).then(()=>{{
                var b=document.getElementById('cbtn');b.innerText='✅ ¡Copiado!';
                b.style.background='linear-gradient(135deg,#38a169,#2f855a)';
                setTimeout(()=>{{b.innerText='📋 Copiar Resumen';b.style.background='linear-gradient(135deg,#4a90e2,#357abd)';}},2500);
            }}).catch(()=>{{
                var t=document.getElementById('rsm');t.style.position='';t.select();document.execCommand('copy');
                var b=document.getElementById('cbtn');b.innerText='✅ ¡Copiado!';
                setTimeout(()=>{{b.innerText='📋 Copiar Resumen';}},2500);
            }});
        " id="cbtn" style="width:100%;padding:11px 20px;font-size:0.92rem;font-weight:600;
            font-family:'Inter',sans-serif;cursor:pointer;border:none;border-radius:10px;
            background:linear-gradient(135deg,#4a90e2,#357abd);color:#fff;
            box-shadow:0 4px 15px rgba(74,144,226,0.3);transition:all .2s ease;">
            📋 Copiar Resumen
        </button>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
