"""
NOVA — modules/requerimientos.py (v3)
Fix: área = text_input libre, categorías desde Supabase.
"""
import streamlit as st
import re
from spellchecker import SpellChecker
from config import (seccion_titulo, badge_estado, badge_prioridad,
                    ESTADOS_TAREA, PRIORIDADES, separador)
from database import get_tareas, crear_tarea, actualizar_tarea, borrar_tarea
from auth import es_admin

CATS_DEFAULT = [
    "Eléctrico","Plomería","AC/Climatización","Equipos AV",
    "Carpintería","Pintura","Equipos de Cocina","Piscina","General",
]

@st.cache_resource
def _spell():
    return SpellChecker(language="es")

def corregir(texto: str):
    spell = _spell()
    cambios, corregidas = [], []
    for p in texto.split():
        if (p.isupper() and len(p)>1) or re.search(r'\d',p):
            corregidas.append(p); continue
        limpia = re.sub(r'[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ]','',p).lower()
        if not limpia: corregidas.append(p); continue
        c = _spell().correction(limpia)
        if c and c!=limpia:
            corregidas.append(c.capitalize() if p[0].isupper() else c)
            cambios.append(f"'{p}'→'{c}'")
        else:
            corregidas.append(p)
    return ' '.join(corregidas), cambios

def _get_categorias(sb) -> list:
    """Carga categorías desde Supabase. Fallback a lista por defecto."""
    try:
        resp = sb.table("categorias").select("nombre").eq("modulo","requerimientos").eq("activo",True).order("nombre").execute()
        if resp.data:
            return [r["nombre"] for r in resp.data]
    except Exception:
        pass
    return CATS_DEFAULT

def render(sb):
    seccion_titulo("📋","Requerimientos","Registro y seguimiento de trabajos de mantenimiento")
    usuario = st.session_state.get("usuario","")
    cats    = _get_categorias(sb)

    # ── FORMULARIO ───────────────────────────────────────────────
    st.markdown('<div class="card">',unsafe_allow_html=True)
    st.markdown('<div class="card-title">➕ Registrar Requerimiento</div>',unsafe_allow_html=True)

    with st.form("form_req",clear_on_submit=True):
        # ÁREA: solo text_input libre (sin selectbox)
        lugar = st.text_input(
            "📍 Área / Lugar *",
            placeholder="ej: Habitación 101, Lobby, Piscina, Cocina...",
            key="req_lugar",
        )
        c1, c2 = st.columns(2)
        with c1:
            categoria = c1.selectbox("🏷️ Categoría", cats, key="req_cat")
        with c2:
            prioridad = c2.radio("⚡ Prioridad", PRIORIDADES, horizontal=True,
                                  key="req_prio", index=1)
        detalle = st.text_area(
            "🔧 Detalle de la actividad *",
            height=90,
            placeholder="Describe el problema o trabajo a realizar...",
            key="req_det",
        )
        enviado = st.form_submit_button("💾 Guardar Requerimiento",use_container_width=True)

    if enviado:
        if not lugar.strip():
            st.warning("⚠️ El campo Área / Lugar es obligatorio.")
        elif not detalle.strip():
            st.warning("⚠️ El detalle es obligatorio.")
        else:
            det_ok, cambios = corregir(detalle)
            ok = crear_tarea(sb,{
                "usuario":   usuario,
                "lugar":     lugar.strip(),
                "detalle":   det_ok,
                "categoria": categoria,
                "prioridad": prioridad,
            })
            if ok:
                msg = "✅ Requerimiento guardado."
                if cambios: msg += f" Correcciones: {', '.join(cambios[:3])}"
                st.success(msg)
                st.rerun()

    st.markdown('</div>',unsafe_allow_html=True)

    # ── FILTROS ──────────────────────────────────────────────────
    with st.expander("🔍 Filtros",expanded=False):
        fc1,fc2,fc3 = st.columns(3)
        f_cat  = fc1.selectbox("Categoría",["Todas"]+cats,key="f_cat")
        f_prio = fc2.selectbox("Prioridad",["Todas"]+PRIORIDADES,key="f_prio")
        f_est  = fc3.selectbox("Estado",["Todos"]+ESTADOS_TAREA,key="f_est")

    filtros = {} if es_admin() else {"usuario":usuario}
    tareas  = get_tareas(sb,filtros)
    if f_cat  != "Todas": tareas=[t for t in tareas if t.get("categoria")==f_cat]
    if f_prio != "Todas": tareas=[t for t in tareas if t.get("prioridad")==f_prio]
    if f_est  != "Todos": tareas=[t for t in tareas if t.get("estado")==f_est]

    # ── LISTA ────────────────────────────────────────────────────
    st.markdown('<div class="card">',unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">📋 Requerimientos <span class="badge badge-azul">{int(len(tareas))}</span></div>',unsafe_allow_html=True)

    if not tareas:
        st.info("Sin requerimientos con los filtros seleccionados.")
    else:
        POR_PAG = 20
        total_p = max(1,(len(tareas)+POR_PAG-1)//POR_PAG)
        pag = st.number_input("Página",min_value=1,max_value=total_p,value=1,step=1,key="req_pag",label_visibility="collapsed")
        for t in tareas[(pag-1)*POR_PAG : pag*POR_PAG]:
            hora = t.get("created_at","")[:16].replace("T"," ")
            tid  = t.get("id")
            prio = t.get("prioridad","Media")
            borde = {"Alta":"#ef4444","Media":"#f59e0b","Baja":"#10b981"}.get(prio,"#3b82f6")
            col_i, col_e, col_d = st.columns([6,2,1])
            with col_i:
                st.markdown(f"""
                <div class="tabla-row" style="border-left:3px solid {borde};">
                    <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:5px;">
                        <span style="font-weight:700;color:#93c5fd;">📍 {t.get('lugar','-')}</span>
                        {badge_prioridad(prio)} {badge_estado(t.get('estado','Abierto'))}
                        <span class="badge badge-purpura">{t.get('categoria','General')}</span>
                    </div>
                    <div style="font-size:0.9rem;color:#f1f5f9;">{t.get('detalle','')}</div>
                    <div style="font-size:0.72rem;color:#64748b;margin-top:5px;">👤 {t.get('usuario','-')} · {hora}</div>
                </div>
                """,unsafe_allow_html=True)
            with col_e:
                nuevo = st.selectbox("",ESTADOS_TAREA,
                    index=ESTADOS_TAREA.index(t.get("estado","Abierto")) if t.get("estado") in ESTADOS_TAREA else 0,
                    key=f"est_{tid}",label_visibility="collapsed")
                if nuevo != t.get("estado"):
                    actualizar_tarea(sb,tid,{"estado":nuevo}); st.rerun()
            with col_d:
                if es_admin():
                    st.markdown('<div class="btn-danger">',unsafe_allow_html=True)
                    if st.button("🗑",key=f"del_{tid}"):
                        borrar_tarea(sb,tid); st.rerun()
                    st.markdown('</div>',unsafe_allow_html=True)
        separador()
        st.caption(f"Página {int(pag)} de {int(total_p)} · {int(len(tareas))} total")
    st.markdown('</div>',unsafe_allow_html=True)

    # ── RESUMEN COPIABLE ─────────────────────────────────────────
    tareas_u = get_tareas(sb,{} if es_admin() else {"usuario":usuario})
    if tareas_u:
        st.markdown('<div class="card">',unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 Resumen del Día</div>',unsafe_allow_html=True)
        resumen = " / ".join(f"{t['lugar']}: {t['detalle']}" for t in tareas_u[:30])
        st.markdown(f"""
        <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);
                    border-radius:10px;padding:14px;color:#6ee7b7;font-size:0.9rem;line-height:1.6;margin-bottom:12px;">{resumen}</div>
        <textarea id="rsm_txt" style="position:absolute;left:-9999px;opacity:0;" readonly>{resumen}</textarea>
        <button onclick="navigator.clipboard.writeText(document.getElementById('rsm_txt').value)
            .then(()=>{{var b=document.getElementById('cpbtn');b.innerText='✅ ¡Copiado!';
            b.style.background='linear-gradient(135deg,#10b981,#059669)';
            setTimeout(()=>{{b.innerText='📋 Copiar Resumen';b.style.background='linear-gradient(135deg,#3b82f6,#2563eb)';}},2500);}});"
            id="cpbtn" style="width:100%;padding:11px;font-size:0.92rem;font-weight:700;font-family:'Inter',sans-serif;
            cursor:pointer;border:none;border-radius:10px;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;
            box-shadow:0 4px 14px rgba(59,130,246,0.35);transition:all .2s ease;">📋 Copiar Resumen</button>
        """,unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
