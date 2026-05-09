"""
NOVA — modules/configuracion.py  (v2 — completamente reescrito)
Módulo 10: Configuración del sistema (solo admin).
"""
import streamlit as st
import io
from config import seccion_titulo, TIPOS_AREA, PRIORIDADES, separador
from database import (get_config, set_config, get_areas, get_usuarios,
                      crear_area, actualizar_area, crear_usuario, actualizar_usuario,
                      get_preventivo_tareas, get_area_nombres)
from auth import requiere_admin


# ─────────────────────────────────────────────────────────────
# SECCIÓN: HOTEL (nombre, logo con file_uploader)
# ─────────────────────────────────────────────────────────────
def _seccion_hotel(sb):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🏨 Información del Hotel</div>', unsafe_allow_html=True)

    cfg = get_config(sb)

    # Mostrar valores actuales
    nombre_actual = cfg.get("nombre_hotel", "Hotel NOVA")
    slogan_actual = cfg.get("slogan", "")
    jefe_actual   = cfg.get("jefe_ingenieria", "")
    logo_url      = cfg.get("logo_url", "")

    # Preview del logo actual
    if logo_url:
        col_img, col_info = st.columns([1, 3])
        with col_img:
            st.markdown(f"""
            <div style="text-align:center;padding:8px;">
                <img src="{logo_url}" style="max-height:72px;border-radius:10px;
                border:1px solid rgba(255,255,255,0.1);max-width:100%;object-fit:contain;">
                <div style="font-size:0.7rem;color:#64748b;margin-top:4px;">Logo actual</div>
            </div>
            """, unsafe_allow_html=True)
        with col_info:
            st.markdown(f"""
            <div style="padding:12px 0;font-size:0.88rem;color:#94a3b8;">
                <strong style="color:#f1f5f9;">{nombre_actual}</strong><br>
                {slogan_actual}<br>
                {jefe_actual}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);
                    border-radius:10px;padding:12px 16px;margin-bottom:14px;font-size:0.88rem;color:#94a3b8;">
            🏨 <strong style="color:#f1f5f9;">{nombre_actual}</strong>
            {' · ' + slogan_actual if slogan_actual else ''}
            {' · ' + jefe_actual if jefe_actual else ''}
        </div>
        """, unsafe_allow_html=True)

    separador()

    # ── Formulario de información ─────────────────────────────
    with st.form("form_hotel_info"):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre del Hotel *", value=nombre_actual, key="cfg_nom")
        slogan = c2.text_input("Eslogan / Subtítulo", value=slogan_actual, key="cfg_slo")
        jefe   = st.text_input("Jefe de Ingeniería (para reportes)", value=jefe_actual, key="cfg_jef")
        submit_info = st.form_submit_button("💾 Guardar Información", use_container_width=True)

    if submit_info:
        if not nombre.strip():
            st.warning("⚠️ El nombre del hotel es obligatorio.")
        else:
            ok1 = set_config(sb, "nombre_hotel",    nombre.strip())
            ok2 = set_config(sb, "slogan",          slogan.strip())
            ok3 = set_config(sb, "jefe_ingenieria", jefe.strip())
            if ok1 and ok2 and ok3:
                st.success("✅ Información guardada correctamente.")
                st.rerun()

    separador()

    # ── Subida de logo ────────────────────────────────────────
    st.markdown("**🖼️ Logo del Hotel**")
    st.markdown('<span style="font-size:0.8rem;color:#64748b;">Sube un archivo PNG o JPG. Se guardará en Supabase Storage.</span>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Seleccionar imagen",
        type=["png", "jpg", "jpeg"],
        key="cfg_logo_upload",
        label_visibility="collapsed",
    )

    if uploaded is not None:
        # Preview inmediato
        st.image(uploaded, width=160, caption="Vista previa del logo a subir")

        col_sub, col_can = st.columns(2)
        with col_sub:
            st.markdown('<div class="btn-success">', unsafe_allow_html=True)
            if st.button("☁️ Subir Logo a Supabase", key="btn_upload_logo", use_container_width=True):
                try:
                    file_bytes   = uploaded.read()
                    content_type = "image/png" if uploaded.name.endswith(".png") else "image/jpeg"
                    filename     = "hotel-logo.png"

                    # Subir a Supabase Storage (bucket 'logos')
                    sb.storage.from_("logos").upload(
                        filename,
                        file_bytes,
                        {"content-type": content_type, "upsert": "true"},
                    )
                    url_publica = sb.storage.from_("logos").get_public_url(filename)

                    # Guardar URL en configuracion
                    set_config(sb, "logo_url", url_publica)
                    st.success("✅ Logo subido y guardado correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al subir el logo: {e}")
                    st.info("💡 Asegúrate de que existe el bucket 'logos' en Supabase Storage con acceso público.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_can:
            st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
            if st.button("✕ Cancelar", key="btn_cancel_logo"):
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    if logo_url:
        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("🗑️ Eliminar Logo", key="btn_del_logo"):
            set_config(sb, "logo_url", "")
            try:
                sb.storage.from_("logos").remove(["hotel-logo.png"])
            except Exception:
                pass
            st.success("✅ Logo eliminado.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SECCIÓN: HABITACIONES (generador)
# ─────────────────────────────────────────────────────────────
def _seccion_habitaciones(sb):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🛏️ Generador de Habitaciones</div>', unsafe_allow_html=True)
    st.markdown('<span style="font-size:0.82rem;color:#64748b;">Genera automáticamente las habitaciones como áreas del sistema.</span>', unsafe_allow_html=True)

    cfg = get_config(sb)

    with st.form("form_hab"):
        c1, c2 = st.columns(2)
        formato = c1.selectbox(
            "Formato de numeración",
            ["Simple (1, 2, 3...)", "Por piso (101, 102..., 201, 202...)"],
            index=0 if cfg.get("formato_hab", "simple") == "simple" else 1,
            key="hab_fmt",
        )
        num_total = c2.number_input(
            "Número total de habitaciones",
            min_value=1, max_value=500, step=1,
            value=int(cfg.get("num_habitaciones", "50")),
            key="hab_num",
        )
        c3, c4 = st.columns(2)
        piso_ini = c3.number_input(
            "Piso inicial",
            min_value=1, max_value=99, step=1, value=1,
            key="hab_piso",
        )
        prefijo  = c4.text_input("Prefijo (opcional)", placeholder="ej: HAB, Suite, Cabina", key="hab_pre")
        generar  = st.form_submit_button("🏗️ Generar Habitaciones", use_container_width=True)

    if generar:
        fmt_val = "simple" if "Simple" in formato else "piso"
        set_config(sb, "formato_hab",     fmt_val)
        set_config(sb, "num_habitaciones", str(int(num_total)))
        set_config(sb, "piso_inicio",     str(int(piso_ini)))

        nombres_gen = []
        if fmt_val == "simple":
            for n in range(1, int(num_total) + 1):
                nombres_gen.append(f"{prefijo} {n}".strip() if prefijo else f"Habitación {n}")
        else:
            # Por piso: 10 habitaciones por piso como base
            por_piso = 10
            count = 0
            piso  = int(piso_ini)
            while count < int(num_total):
                for n in range(1, por_piso + 1):
                    if count >= int(num_total):
                        break
                    nomb = f"{prefijo} {piso}{n:02d}".strip() if prefijo else f"Habitación {piso}{n:02d}"
                    nombres_gen.append(nomb)
                    count += 1
                piso += 1

        areas_exist = {a["nombre"] for a in get_areas(sb, solo_activas=False)}
        insertados  = 0
        for nh in nombres_gen:
            if nh not in areas_exist:
                crear_area(sb, nh, "habitacion", str(int(piso_ini)))
                insertados += 1

        st.success(f"✅ {insertados} habitaciones nuevas generadas. Total definidas: {len(nombres_gen)}.")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SECCIÓN: ÁREAS
# ─────────────────────────────────────────────────────────────
def _seccion_areas(sb):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📍 Gestión de Áreas</div>', unsafe_allow_html=True)

    areas = get_areas(sb, solo_activas=False)
    total = len(areas)
    activas = sum(1 for a in areas if a.get("activo"))

    st.markdown(f"""
    <div style="display:flex;gap:16px;margin-bottom:16px;font-size:0.82rem;color:#94a3b8;">
        <span>📍 Total: <strong style="color:#f1f5f9;">{total}</strong></span>
        <span>🟢 Activas: <strong style="color:#10b981;">{activas}</strong></span>
        <span>🔴 Inactivas: <strong style="color:#ef4444;">{total - activas}</strong></span>
    </div>
    """, unsafe_allow_html=True)

    # Lista con paginación
    POR_PAG = 15
    total_pags = max(1, (len(areas) + POR_PAG - 1) // POR_PAG)
    pag = st.number_input("Página", min_value=1, max_value=total_pags, value=1, step=1,
                           key="areas_pag", label_visibility="collapsed")
    areas_pag = areas[(pag-1)*POR_PAG : pag*POR_PAG]

    for a in areas_pag:
        aid = a["id"]
        act = a.get("activo", True)
        c_nom, c_tipo, c_ed, c_tog = st.columns([3, 2, 1, 1])

        c_nom.markdown(f"""
        <div style="padding:8px 0;font-size:0.88rem;">
            {'🟢' if act else '🔴'} <strong style="color:#f1f5f9;">{a['nombre']}</strong>
        </div>
        """, unsafe_allow_html=True)
        c_tipo.markdown(f"""
        <div style="padding:8px 0;font-size:0.8rem;color:#64748b;">
            {a.get('tipo','-').replace('_',' ').title()} · Piso {a.get('piso','-') or '-'}
        </div>
        """, unsafe_allow_html=True)

        if c_ed.button("✏️", key=f"ed_a_{aid}", help="Editar"):
            st.session_state[f"edit_area_{aid}"] = not st.session_state.get(f"edit_area_{aid}", False)

        if act:
            if c_tog.button("🚫", key=f"dis_a_{aid}", help="Desactivar"):
                actualizar_area(sb, aid, {"activo": False})
                st.success(f"✅ Área '{a['nombre']}' desactivada.")
                st.rerun()
        else:
            if c_tog.button("✅", key=f"act_a_{aid}", help="Activar"):
                actualizar_area(sb, aid, {"activo": True})
                st.success(f"✅ Área '{a['nombre']}' activada.")
                st.rerun()

        if st.session_state.get(f"edit_area_{aid}"):
            with st.form(f"form_edit_area_{aid}"):
                en = st.text_input("Nombre", value=a["nombre"], key=f"ae_n_{aid}")
                et = st.selectbox("Tipo", TIPOS_AREA,
                                  index=TIPOS_AREA.index(a["tipo"]) if a.get("tipo") in TIPOS_AREA else 0,
                                  key=f"ae_t_{aid}")
                ep = st.text_input("Piso", value=a.get("piso",""), key=f"ae_p_{aid}")
                ok_ed = st.form_submit_button("💾 Guardar cambios")
            if ok_ed:
                actualizar_area(sb, aid, {"nombre": en.strip(), "tipo": et, "piso": ep.strip()})
                st.session_state.pop(f"edit_area_{aid}", None)
                st.success("✅ Área actualizada.")
                st.rerun()

    separador()
    st.markdown("**➕ Nueva Área**")
    with st.form("form_nueva_area", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        na_nom  = c1.text_input("Nombre *", key="na_n")
        na_tipo = c2.selectbox("Tipo", TIPOS_AREA, key="na_t")
        na_piso = c3.text_input("Piso (opcional)", key="na_p")
        crear   = st.form_submit_button("➕ Crear Área", use_container_width=True)
    if crear:
        if not na_nom.strip():
            st.warning("⚠️ El nombre es obligatorio.")
        else:
            if crear_area(sb, na_nom.strip(), na_tipo, na_piso.strip()):
                st.success(f"✅ Área '{na_nom.strip()}' creada correctamente.")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SECCIÓN: USUARIOS
# ─────────────────────────────────────────────────────────────
def _seccion_usuarios(sb):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👥 Gestión de Usuarios</div>', unsafe_allow_html=True)

    usuarios = get_usuarios(sb)

    for u in usuarios:
        uid = u["id"]
        act = u.get("activo", True)

        c_info, c_ed, c_pw, c_tog = st.columns([4, 1, 1, 1])
        rol_badge = '🔑 Admin' if u.get("rol") == "admin" else '🔧 Técnico'
        c_info.markdown(f"""
        <div style="padding:8px 0;font-size:0.88rem;">
            {'🟢' if act else '🔴'} <strong style="color:#f1f5f9;">{u['nombre_completo']}</strong>
            <span style="color:#64748b;"> · @{u['username']} · {rol_badge}</span>
        </div>
        """, unsafe_allow_html=True)

        if c_ed.button("✏️", key=f"ed_u_{uid}", help="Editar datos"):
            st.session_state[f"edit_user_{uid}"] = not st.session_state.get(f"edit_user_{uid}", False)

        if c_pw.button("🔑", key=f"pw_u_{uid}", help="Cambiar contraseña"):
            st.session_state[f"pw_user_{uid}"] = not st.session_state.get(f"pw_user_{uid}", False)

        tog_lbl = "🚫" if act else "✅"
        tog_tip  = "Desactivar" if act else "Activar"
        if c_tog.button(tog_lbl, key=f"tog_u_{uid}", help=tog_tip):
            actualizar_usuario(sb, uid, {"activo": not act})
            st.success(f"✅ Usuario {'desactivado' if act else 'activado'}.")
            st.rerun()

        # Panel de edición
        if st.session_state.get(f"edit_user_{uid}"):
            with st.form(f"form_edit_u_{uid}"):
                new_nom = st.text_input("Nombre completo", value=u["nombre_completo"], key=f"ue_n_{uid}")
                new_rol = st.selectbox("Rol", ["tecnico","admin"],
                                       index=0 if u.get("rol")=="tecnico" else 1, key=f"ue_r_{uid}")
                ok_ed_u = st.form_submit_button("💾 Guardar cambios")
            if ok_ed_u:
                actualizar_usuario(sb, uid, {"nombre_completo": new_nom.strip(), "rol": new_rol})
                st.session_state.pop(f"edit_user_{uid}", None)
                st.success("✅ Usuario actualizado.")
                st.rerun()

        # Panel de cambio de contraseña (NO muestra la actual)
        if st.session_state.get(f"pw_user_{uid}"):
            with st.form(f"form_pw_u_{uid}"):
                st.markdown('<span style="font-size:0.82rem;color:#94a3b8;">Ingresa la nueva contraseña:</span>', unsafe_allow_html=True)
                new_pw1 = st.text_input("Nueva contraseña", type="password", key=f"pw1_{uid}")
                new_pw2 = st.text_input("Confirmar contraseña", type="password", key=f"pw2_{uid}")
                ok_pw   = st.form_submit_button("🔑 Cambiar Contraseña")
            if ok_pw:
                if not new_pw1.strip():
                    st.warning("⚠️ La contraseña no puede estar vacía.")
                elif new_pw1 != new_pw2:
                    st.error("❌ Las contraseñas no coinciden.")
                else:
                    actualizar_usuario(sb, uid, {"password_plain": new_pw1})
                    st.session_state.pop(f"pw_user_{uid}", None)
                    st.success("✅ Contraseña actualizada correctamente.")
                    st.rerun()

    separador()
    st.markdown("**➕ Nuevo Usuario**")
    with st.form("form_nuevo_user", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nu_nom  = c1.text_input("Nombre completo *", key="nu_n")
        nu_usr  = c2.text_input("Username * (sin espacios)", key="nu_u")
        c3, c4  = st.columns(2)
        nu_pw   = c3.text_input("Contraseña *", type="password", key="nu_p")
        nu_rol  = c4.selectbox("Rol", ["tecnico","admin"], key="nu_r")
        crear_u = st.form_submit_button("➕ Crear Usuario", use_container_width=True)
    if crear_u:
        if not all([nu_nom.strip(), nu_usr.strip(), nu_pw.strip()]):
            st.warning("⚠️ Completa todos los campos obligatorios.")
        elif " " in nu_usr.strip():
            st.warning("⚠️ El username no puede contener espacios.")
        else:
            if crear_usuario(sb, {
                "username":       nu_usr.strip().lower(),
                "nombre_completo":nu_nom.strip(),
                "password_plain": nu_pw,
                "rol":            nu_rol,
                "activo":         True,
            }):
                st.success(f"✅ Usuario '@{nu_usr.strip().lower()}' creado correctamente.")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SECCIÓN: PREVENTIVO (tareas programadas)
# ─────────────────────────────────────────────────────────────
def _seccion_preventivo(sb):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">✅ Tareas de Mantenimiento Preventivo</div>', unsafe_allow_html=True)

    tareas = get_preventivo_tareas(sb)
    areas  = get_area_nombres(sb)
    freq_icon = {"diaria":"📅","semanal":"📆","mensual":"🗓️"}

    for t in tareas:
        tid = t["id"]
        c_lbl, c_ed, c_del = st.columns([5, 1, 1])
        c_lbl.markdown(f"""
        <div style="padding:7px 0;font-size:0.87rem;">
            {freq_icon.get(t['frecuencia'],'🔲')}
            <strong style="color:#f1f5f9;">{t['nombre']}</strong>
            <span style="color:#64748b;"> · {t['frecuencia'].title()}</span>
        </div>
        """, unsafe_allow_html=True)

        if c_ed.button("✏️", key=f"pe_{tid}", help="Editar"):
            st.session_state[f"edit_prev_{tid}"] = not st.session_state.get(f"edit_prev_{tid}", False)

        if c_del.button("🗑️", key=f"pd_{tid}", help="Eliminar"):
            st.session_state[f"confirm_del_prev_{tid}"] = True

        # Confirmación de borrado
        if st.session_state.get(f"confirm_del_prev_{tid}"):
            st.warning(f"⚠️ ¿Eliminar la tarea '{t['nombre']}'?")
            ca, cb = st.columns(2)
            with ca:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("✅ Sí, eliminar", key=f"del_conf_{tid}"):
                    try:
                        sb.table("preventivo_tareas").update({"activo": False}).eq("id", tid).execute()
                        get_preventivo_tareas.clear()
                        st.session_state.pop(f"confirm_del_prev_{tid}", None)
                        st.success("✅ Tarea desactivada.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")
                st.markdown('</div>', unsafe_allow_html=True)
            with cb:
                st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
                if st.button("Cancelar", key=f"del_cancel_{tid}"):
                    st.session_state.pop(f"confirm_del_prev_{tid}", None)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.get(f"edit_prev_{tid}"):
            with st.form(f"form_edit_prev_{tid}"):
                pn = st.text_input("Nombre", value=t["nombre"], key=f"pe_n_{tid}")
                pd = st.text_area("Descripción", value=t.get("descripcion",""), height=60, key=f"pe_d_{tid}")
                pf = st.selectbox("Frecuencia", ["diaria","semanal","mensual"],
                                  index=["diaria","semanal","mensual"].index(t["frecuencia"])
                                        if t["frecuencia"] in ["diaria","semanal","mensual"] else 0,
                                  key=f"pe_f_{tid}")
                ok_pe = st.form_submit_button("💾 Guardar")
            if ok_pe:
                try:
                    sb.table("preventivo_tareas").update({
                        "nombre": pn.strip(), "descripcion": pd.strip(), "frecuencia": pf
                    }).eq("id", tid).execute()
                    get_preventivo_tareas.clear()
                    st.session_state.pop(f"edit_prev_{tid}", None)
                    st.success("✅ Tarea actualizada.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")

    separador()
    st.markdown("**➕ Nueva Tarea Preventiva**")
    with st.form("form_nueva_prev", clear_on_submit=True):
        c1, c2 = st.columns(2)
        np_nom  = c1.text_input("Nombre *", key="np_n")
        np_frec = c2.selectbox("Frecuencia", ["diaria","semanal","mensual"], key="np_f")
        np_desc = st.text_area("Descripción (opcional)", height=60, key="np_d")
        np_area = st.selectbox("Área asignada (opcional)", ["Sin área"] + areas, key="np_a")
        crear_p = st.form_submit_button("➕ Agregar Tarea", use_container_width=True)

    if crear_p:
        if not np_nom.strip():
            st.warning("⚠️ El nombre es obligatorio.")
        else:
            area_id = None
            if np_area != "Sin área":
                try:
                    r = sb.table("areas").select("id").eq("nombre", np_area).execute()
                    area_id = r.data[0]["id"] if r.data else None
                except Exception:
                    pass
            try:
                sb.table("preventivo_tareas").insert({
                    "nombre": np_nom.strip(), "descripcion": np_desc.strip(),
                    "frecuencia": np_frec, "area_id": area_id, "activo": True,
                }).execute()
                get_preventivo_tareas.clear()
                st.success(f"✅ Tarea '{np_nom.strip()}' creada correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# RENDER PRINCIPAL
# ─────────────────────────────────────────────────────────────
def render(sb):
    requiere_admin()
    seccion_titulo("⚙️", "Configuración", "Administración del sistema · Solo administradores")

    tab_hotel, tab_hab, tab_areas, tab_users, tab_prev = st.tabs([
        "🏨 Hotel & Logo",
        "🛏️ Habitaciones",
        "📍 Áreas",
        "👥 Usuarios",
        "✅ Preventivo",
    ])

    with tab_hotel:  _seccion_hotel(sb)
    with tab_hab:    _seccion_habitaciones(sb)
    with tab_areas:  _seccion_areas(sb)
    with tab_users:  _seccion_usuarios(sb)
    with tab_prev:   _seccion_preventivo(sb)
