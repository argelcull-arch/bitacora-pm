"""
NOVA — modules/configuracion.py
Módulo 10: Configuración del sistema (solo admin).
Gestión de hotel, áreas, usuarios y categorías.
"""
import streamlit as st
import requests, io
from datetime import date
from config import seccion_titulo, CATEGORIAS_TAREA, CATEGORIAS_INVENTARIO, CATEGORIAS_ACTIVOS, TIPOS_AREA
from database import (get_areas, get_usuarios, get_config_hotel, set_config_hotel,
                      crear_area, actualizar_area, crear_usuario, actualizar_usuario,
                      get_preventivo_tareas, get_area_nombres)
from auth import requiere_admin


def _seccion_hotel(sb):
    """Configuración general del hotel y logo."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🏨 Información del Hotel</div>', unsafe_allow_html=True)

    cfg = get_config_hotel(sb)

    with st.form("form_hotel"):
        c1, c2 = st.columns(2)
        nombre   = c1.text_input("Nombre del Hotel",     value=cfg.get("nombre_hotel","Hotel NOVA"),   key="cfg_nom")
        slogan   = c2.text_input("Eslogan / Subtítulo",  value=cfg.get("slogan",""),                   key="cfg_slo")
        jefe     = c1.text_input("Jefe de Ingeniería",   value=cfg.get("jefe_ingenieria",""),          key="cfg_jef")
        logo_url = c2.text_input("URL del Logo (imagen pública)", value=cfg.get("logo_url",""),        key="cfg_logo",
                                  help="Sube tu logo a Supabase Storage o usa un link público directo (PNG/JPG).")
        submit = st.form_submit_button("💾 Guardar Configuración", use_container_width=True)

    if submit:
        for clave, valor in [
            ("nombre_hotel",    nombre),
            ("slogan",          slogan),
            ("jefe_ingenieria", jefe),
            ("logo_url",        logo_url),
        ]:
            set_config_hotel(sb, clave, valor)
        st.success("✅ Configuración guardada.")
        st.rerun()

    # Preview del logo
    if cfg.get("logo_url"):
        st.markdown(f"""
        <div style="margin-top:12px;text-align:center;">
            <div style="font-size:0.78rem;color:#94a3b8;margin-bottom:6px;">Vista previa del logo:</div>
            <img src="{cfg['logo_url']}" style="max-height:80px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);">
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def _seccion_habitaciones(sb):
    """Generador automático de habitaciones."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🛏️ Generador de Habitaciones</div>', unsafe_allow_html=True)
    cfg = get_config_hotel(sb)

    with st.form("form_hab"):
        c1, c2, c3 = st.columns(3)
        formato   = c1.selectbox("Formato", ["simple (1,2,3...)", "por piso (101,102...)"],
                                  index=0 if cfg.get("formato_hab","simple")=="simple" else 1,
                                  key="hab_fmt")
        num_total = c2.number_input("Número de habitaciones", min_value=1, max_value=999,
                                     value=int(cfg.get("num_habitaciones","50")), key="hab_num")
        piso_ini  = c3.number_input("Piso inicial (solo para formato por piso)", min_value=1, value=1, key="hab_piso")

        prefix    = st.text_input("Prefijo (opcional)", placeholder="ej. HAB, Suite, Room...", key="hab_pre")
        generar   = st.form_submit_button("🏗️ Generar Habitaciones (sobreescribe existentes del tipo 'habitacion')", use_container_width=True)

    if generar:
        fmt_val = "simple" if "simple" in formato else "piso"
        set_config_hotel(sb, "formato_hab",     fmt_val)
        set_config_hotel(sb, "num_habitaciones", str(num_total))
        set_config_hotel(sb, "piso_inicio",     str(piso_ini))

        # Generar nombres de habitaciones
        nombres_gen = []
        if fmt_val == "simple":
            for n in range(1, num_total + 1):
                nombres_gen.append(f"{prefix} {n}".strip() if prefix else f"Habitación {n}")
        else:
            hab_por_piso = max(1, num_total // max(1, piso_ini))
            count = 0
            piso  = piso_ini
            while count < num_total:
                for n in range(1, hab_por_piso + 1):
                    if count >= num_total:
                        break
                    nombre_h = f"{prefix} {piso}{n:02d}".strip() if prefix else f"Habitación {piso}{n:02d}"
                    nombres_gen.append(nombre_h)
                    count += 1
                piso += 1

        # Insertar en areas (si no existen)
        areas_exist = {a["nombre"] for a in get_areas(sb, solo_activas=False)}
        insertados  = 0
        for nh in nombres_gen:
            if nh not in areas_exist:
                crear_area(sb, nh, "habitacion", str(piso_ini))
                insertados += 1
        st.success(f"✅ {insertados} habitaciones generadas ({len(nombres_gen)} total definidas).")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def _seccion_areas(sb):
    """CRUD de áreas del hotel."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📍 Gestión de Áreas</div>', unsafe_allow_html=True)

    areas = get_areas(sb, solo_activas=False)

    # Lista existente
    if areas:
        for a in areas[:40]:
            ca, cb, cc = st.columns([4, 1, 1])
            activo_lbl = "🟢" if a["activo"] else "🔴"
            ca.markdown(f"""
            <div style="padding:8px 0;font-size:0.88rem;">
                {activo_lbl} <strong>{a['nombre']}</strong>
                <span style="color:#94a3b8;font-size:0.78rem;"> · {a.get('tipo','-')} · Piso {a.get('piso','-')}</span>
            </div>
            """, unsafe_allow_html=True)
            if cb.button("✏️", key=f"ared_{a['id']}", help="Editar"):
                st.session_state[f"edit_area_{a['id']}"] = True
            if a["activo"]:
                if cc.button("🚫", key=f"adis_{a['id']}", help="Desactivar"):
                    actualizar_area(sb, a["id"], {"activo": False})
                    st.rerun()
            else:
                if cc.button("✅", key=f"aact_{a['id']}", help="Activar"):
                    actualizar_area(sb, a["id"], {"activo": True})
                    st.rerun()

            if st.session_state.get(f"edit_area_{a['id']}"):
                with st.form(f"edit_area_form_{a['id']}"):
                    new_nom  = st.text_input("Nombre", value=a["nombre"], key=f"ae_nom_{a['id']}")
                    new_tipo = st.selectbox("Tipo", TIPOS_AREA,
                                           index=TIPOS_AREA.index(a["tipo"]) if a["tipo"] in TIPOS_AREA else 0,
                                           key=f"ae_tipo_{a['id']}")
                    new_piso = st.text_input("Piso", value=a.get("piso",""), key=f"ae_piso_{a['id']}")
                    okk = st.form_submit_button("💾 Guardar cambios")
                if okk:
                    actualizar_area(sb, a["id"], {"nombre": new_nom, "tipo": new_tipo, "piso": new_piso})
                    st.session_state.pop(f"edit_area_{a['id']}", None)
                    st.success("✅ Área actualizada.")
                    st.rerun()

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown("**➕ Nueva Área**")
    with st.form("form_nueva_area", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        na_nom  = c1.text_input("Nombre *", key="na_nom2")
        na_tipo = c2.selectbox("Tipo", TIPOS_AREA, key="na_tipo2")
        na_piso = c3.text_input("Piso", key="na_piso2")
        crear_a = st.form_submit_button("➕ Crear Área", use_container_width=True)
    if crear_a:
        if not na_nom.strip():
            st.warning("⚠️ El nombre es obligatorio.")
        else:
            crear_area(sb, na_nom.strip(), na_tipo, na_piso.strip())
            st.success(f"✅ Área '{na_nom}' creada.")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def _seccion_usuarios(sb):
    """CRUD de usuarios del sistema."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👥 Gestión de Usuarios</div>', unsafe_allow_html=True)

    usuarios = get_usuarios(sb)

    for u in usuarios:
        uid = u["id"]
        act_lbl = "🟢" if u.get("activo") else "🔴"
        cu, ca, cb = st.columns([5, 1, 1])
        cu.markdown(f"""
        <div style="padding:8px 0;font-size:0.88rem;">
            {act_lbl} <strong>{u['nombre_completo']}</strong>
            <span style="color:#94a3b8;"> · @{u['username']} · {u.get('rol','tecnico').upper()}</span>
        </div>
        """, unsafe_allow_html=True)
        if ca.button("✏️", key=f"ued_{uid}"):
            st.session_state[f"edit_user_{uid}"] = True
        tog_lbl = "🚫" if u.get("activo") else "✅"
        if cb.button(tog_lbl, key=f"utog_{uid}"):
            actualizar_usuario(sb, uid, {"activo": not u.get("activo", True)})
            st.rerun()

        if st.session_state.get(f"edit_user_{uid}"):
            with st.form(f"edit_user_form_{uid}"):
                en  = st.text_input("Nombre completo", value=u["nombre_completo"], key=f"ue_nom_{uid}")
                ep  = st.text_input("Nueva contraseña (dejar vacío para no cambiar)", type="password", key=f"ue_pw_{uid}")
                er  = st.selectbox("Rol", ["tecnico","admin"],
                                   index=0 if u.get("rol")=="tecnico" else 1, key=f"ue_rol_{uid}")
                okk = st.form_submit_button("💾 Guardar")
            if okk:
                datos = {"nombre_completo": en, "rol": er}
                if ep.strip():
                    datos["password_plain"] = ep.strip()
                actualizar_usuario(sb, uid, datos)
                st.session_state.pop(f"edit_user_{uid}", None)
                st.success("✅ Usuario actualizado.")
                st.rerun()

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown("**➕ Nuevo Usuario**")
    with st.form("form_nuevo_user", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nu_nom  = c1.text_input("Nombre completo *", key="nu_nom")
        nu_user = c2.text_input("Username *",        key="nu_user")
        c3, c4  = st.columns(2)
        nu_pw   = c3.text_input("Contraseña *", type="password", key="nu_pw")
        nu_rol  = c4.selectbox("Rol", ["tecnico","admin"], key="nu_rol")
        crear_u = st.form_submit_button("➕ Crear Usuario", use_container_width=True)
    if crear_u:
        if not all([nu_nom.strip(), nu_user.strip(), nu_pw.strip()]):
            st.warning("⚠️ Completa todos los campos.")
        else:
            crear_usuario(sb, {
                "username":       nu_user.strip().lower(),
                "nombre_completo":nu_nom.strip(),
                "password_plain": nu_pw,
                "rol":            nu_rol,
                "activo":         True,
            })
            st.success(f"✅ Usuario '{nu_user}' creado.")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def _seccion_preventivo(sb):
    """CRUD de tareas preventivas programadas."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">✅ Tareas de Mantenimiento Preventivo</div>', unsafe_allow_html=True)

    tareas = get_preventivo_tareas(sb)
    areas  = get_area_nombres(sb)

    for t in tareas:
        tid  = t["id"]
        ct, cb = st.columns([5, 1])
        freq_icon = {"diaria":"📅","semanal":"📆","mensual":"🗓️"}.get(t["frecuencia"],"🔲")
        ct.markdown(f"""
        <div style="padding:7px 0;font-size:0.88rem;">
            {freq_icon} <strong>{t['nombre']}</strong>
            <span style="color:#94a3b8;"> · {t['frecuencia'].title()}</span>
        </div>
        """, unsafe_allow_html=True)
        if cb.button("✏️", key=f"prev_ed_{tid}"):
            st.session_state[f"edit_prev_{tid}"] = True

        if st.session_state.get(f"edit_prev_{tid}"):
            with st.form(f"edit_prev_form_{tid}"):
                pn = st.text_input("Nombre", value=t["nombre"], key=f"pe_nom_{tid}")
                pd = st.text_area("Descripción", value=t.get("descripcion",""), height=60, key=f"pe_desc_{tid}")
                pf = st.selectbox("Frecuencia", ["diaria","semanal","mensual"],
                                  index=["diaria","semanal","mensual"].index(t["frecuencia"]) if t["frecuencia"] in ["diaria","semanal","mensual"] else 0,
                                  key=f"pe_frec_{tid}")
                okk = st.form_submit_button("💾 Guardar")
            if okk:
                try:
                    sb.table("preventivo_tareas").update({"nombre":pn,"descripcion":pd,"frecuencia":pf}).eq("id",tid).execute()
                    from database import get_preventivo_tareas as gpt
                    gpt.clear()
                    st.session_state.pop(f"edit_prev_{tid}", None)
                    st.success("✅ Tarea actualizada.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown("**➕ Nueva Tarea Preventiva**")
    with st.form("form_nueva_prev", clear_on_submit=True):
        c1, c2 = st.columns(2)
        np_nom  = c1.text_input("Nombre *", key="np_nom")
        np_frec = c2.selectbox("Frecuencia", ["diaria","semanal","mensual"], key="np_frec")
        np_desc = st.text_area("Descripción", height=60, key="np_desc")
        np_area = st.selectbox("Área (opcional)", ["Sin área"] + areas, key="np_area")
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
                    "nombre":np_nom.strip(),"descripcion":np_desc.strip(),
                    "frecuencia":np_frec,"area_id":area_id,"activo":True,
                }).execute()
                from database import get_preventivo_tareas as gpt
                gpt.clear()
                st.success(f"✅ Tarea '{np_nom}' agregada.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

    st.markdown('</div>', unsafe_allow_html=True)


def render(sb):
    requiere_admin()
    seccion_titulo("⚙️", "Configuración", "Administración del sistema · Solo administradores")

    tab_hotel, tab_hab, tab_areas, tab_users, tab_prev = st.tabs([
        "🏨 Hotel", "🛏️ Habitaciones", "📍 Áreas", "👥 Usuarios", "✅ Preventivo"
    ])

    with tab_hotel: _seccion_hotel(sb)
    with tab_hab:   _seccion_habitaciones(sb)
    with tab_areas: _seccion_areas(sb)
    with tab_users: _seccion_usuarios(sb)
    with tab_prev:  _seccion_preventivo(sb)
