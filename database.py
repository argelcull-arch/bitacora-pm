"""
NOVA — database.py
Todas las funciones de acceso a Supabase, organizadas por módulo.
"""
import streamlit as st
from supabase import create_client, Client
import os
from datetime import date, datetime


# ── Conexión ───────────────────────────────────────────────────
@st.cache_resource
def init_supabase() -> Client:
    """Inicializa cliente Supabase usando st.secrets o variables de entorno."""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except (KeyError, FileNotFoundError):
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        st.error("❌ No se encontraron las credenciales de Supabase en st.secrets.")
        st.stop()
    return create_client(url, key)


# ── Configuración del Hotel ────────────────────────────────────
@st.cache_data(ttl=60)
def get_config_hotel(_sb: Client) -> dict:
    try:
        resp = _sb.table("configuracion_hotel").select("clave,valor").execute()
        return {r["clave"]: r["valor"] for r in (resp.data or [])}
    except Exception:
        return {}


def set_config_hotel(sb: Client, clave: str, valor: str) -> bool:
    try:
        sb.table("configuracion_hotel").upsert(
            {"clave": clave, "valor": valor, "updated_at": datetime.utcnow().isoformat()},
            on_conflict="clave"
        ).execute()
        get_config_hotel.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error guardando configuración: {e}")
        return False


# ── Áreas ─────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_areas(_sb: Client, solo_activas: bool = True) -> list:
    try:
        q = _sb.table("areas").select("*").order("nombre")
        if solo_activas:
            q = q.eq("activo", True)
        return q.execute().data or []
    except Exception as e:
        st.error(f"❌ Error cargando áreas: {e}")
        return []


def get_area_nombres(_sb: Client) -> list[str]:
    return [a["nombre"] for a in get_areas(_sb)]


def crear_area(sb: Client, nombre, tipo, piso, activo=True) -> bool:
    try:
        sb.table("areas").insert({"nombre": nombre, "tipo": tipo, "piso": piso, "activo": activo}).execute()
        get_areas.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error creando área: {e}")
        return False


def actualizar_area(sb: Client, id_area: int, datos: dict) -> bool:
    try:
        sb.table("areas").update(datos).eq("id", id_area).execute()
        get_areas.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error actualizando área: {e}")
        return False


# ── Tareas / Requerimientos ────────────────────────────────────
@st.cache_data(ttl=30)
def get_tareas(_sb: Client, filtros: dict = None) -> list:
    try:
        q = _sb.table("tareas").select("*").order("created_at", desc=True)
        if filtros:
            if filtros.get("usuario"):
                q = q.eq("usuario", filtros["usuario"])
            if filtros.get("estado"):
                q = q.eq("estado", filtros["estado"])
            if filtros.get("prioridad"):
                q = q.eq("prioridad", filtros["prioridad"])
            if filtros.get("categoria"):
                q = q.eq("categoria", filtros["categoria"])
            if filtros.get("fecha_desde"):
                q = q.gte("created_at", filtros["fecha_desde"])
            if filtros.get("fecha_hasta"):
                q = q.lte("created_at", filtros["fecha_hasta"])
        return q.execute().data or []
    except Exception as e:
        st.error(f"❌ Error cargando requerimientos: {e}")
        return []


def crear_tarea(sb: Client, datos: dict) -> bool:
    try:
        sb.table("tareas").insert({
            **datos,
            "created_at": datetime.utcnow().isoformat(),
            "estado": "Abierto",
        }).execute()
        get_tareas.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error creando requerimiento: {e}")
        return False


def actualizar_tarea(sb: Client, id_tarea: int, datos: dict) -> bool:
    try:
        sb.table("tareas").update(datos).eq("id", id_tarea).execute()
        get_tareas.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error actualizando requerimiento: {e}")
        return False


def borrar_tarea(sb: Client, id_tarea: int) -> bool:
    try:
        sb.table("tareas").delete().eq("id", id_tarea).execute()
        get_tareas.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error borrando requerimiento: {e}")
        return False


# ── Pendientes ─────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_pendientes(_sb: Client, estado: str = None) -> list:
    try:
        q = _sb.table("pendientes").select("*, areas(nombre)").order("created_at", desc=True)
        if estado:
            q = q.eq("estado", estado)
        return q.execute().data or []
    except Exception as e:
        st.error(f"❌ Error cargando pendientes: {e}")
        return []


def crear_pendiente(sb: Client, datos: dict) -> bool:
    try:
        sb.table("pendientes").insert({**datos, "created_at": datetime.utcnow().isoformat()}).execute()
        get_pendientes.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error creando pendiente: {e}")
        return False


def actualizar_pendiente(sb: Client, id_p: int, datos: dict) -> bool:
    try:
        if datos.get("estado") == "Resuelto" and "resuelto_at" not in datos:
            datos["resuelto_at"] = datetime.utcnow().isoformat()
        sb.table("pendientes").update(datos).eq("id", id_p).execute()
        get_pendientes.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error actualizando pendiente: {e}")
        return False


def borrar_pendiente(sb: Client, id_p: int) -> bool:
    try:
        sb.table("pendientes").delete().eq("id", id_p).execute()
        get_pendientes.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error borrando pendiente: {e}")
        return False


# ── Inventario ─────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_inventario_items(_sb: Client) -> list:
    try:
        return _sb.table("inventario_items").select("*").eq("activo", True).order("nombre").execute().data or []
    except Exception as e:
        st.error(f"❌ Error cargando inventario: {e}")
        return []


def crear_item_inventario(sb: Client, datos: dict) -> bool:
    try:
        sb.table("inventario_items").insert(datos).execute()
        get_inventario_items.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error creando ítem: {e}")
        return False


def actualizar_stock(sb: Client, item_id: int, nuevo_stock: float,
                     tipo: str, cantidad: float, usuario: str, motivo: str) -> bool:
    """Actualiza stock y registra movimiento."""
    try:
        sb.table("inventario_items").update({"stock_actual": nuevo_stock}).eq("id", item_id).execute()
        sb.table("inventario_movimientos").insert({
            "item_id": item_id, "tipo": tipo, "cantidad": cantidad,
            "usuario": usuario, "motivo": motivo,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        get_inventario_items.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error actualizando stock: {e}")
        return False


@st.cache_data(ttl=30)
def get_movimientos(_sb: Client, item_id: int = None) -> list:
    try:
        q = _sb.table("inventario_movimientos").select("*, inventario_items(nombre)").order("created_at", desc=True).limit(200)
        if item_id:
            q = q.eq("item_id", item_id)
        return q.execute().data or []
    except Exception as e:
        st.error(f"❌ Error cargando movimientos: {e}")
        return []


# ── Activos ────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_activos(_sb: Client) -> list:
    try:
        return _sb.table("activos").select("*, areas(nombre)").order("nombre").execute().data or []
    except Exception as e:
        st.error(f"❌ Error cargando activos: {e}")
        return []


def crear_activo(sb: Client, datos: dict) -> bool:
    try:
        sb.table("activos").insert(datos).execute()
        get_activos.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error creando activo: {e}")
        return False


def actualizar_activo(sb: Client, id_a: int, datos: dict) -> bool:
    try:
        sb.table("activos").update(datos).eq("id", id_a).execute()
        get_activos.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error actualizando activo: {e}")
        return False


def agregar_historial_activo(sb: Client, datos: dict) -> bool:
    try:
        sb.table("activos_historial").insert({**datos, "created_at": datetime.utcnow().isoformat()}).execute()
        get_historial_activo.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error agregando historial: {e}")
        return False


@st.cache_data(ttl=30)
def get_historial_activo(_sb: Client, activo_id: int) -> list:
    try:
        return _sb.table("activos_historial").select("*").eq("activo_id", activo_id).order("fecha", desc=True).execute().data or []
    except Exception as e:
        st.error(f"❌ Error cargando historial: {e}")
        return []


# ── Preventivo ─────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_preventivo_tareas(_sb: Client, frecuencia: str = None) -> list:
    try:
        q = _sb.table("preventivo_tareas").select("*, areas(nombre)").eq("activo", True)
        if frecuencia:
            q = q.eq("frecuencia", frecuencia)
        return q.order("nombre").execute().data or []
    except Exception as e:
        st.error(f"❌ Error cargando tareas preventivas: {e}")
        return []


@st.cache_data(ttl=30)
def get_preventivo_registros(_sb: Client, fecha_desde: str = None, fecha_hasta: str = None) -> list:
    try:
        q = _sb.table("preventivo_registros").select("*, preventivo_tareas(nombre,frecuencia)")
        if fecha_desde:
            q = q.gte("fecha", fecha_desde)
        if fecha_hasta:
            q = q.lte("fecha", fecha_hasta)
        return q.order("created_at", desc=True).execute().data or []
    except Exception as e:
        st.error(f"❌ Error cargando registros preventivos: {e}")
        return []


def registrar_preventivo(sb: Client, datos: dict) -> bool:
    try:
        sb.table("preventivo_registros").insert({**datos, "created_at": datetime.utcnow().isoformat()}).execute()
        get_preventivo_registros.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error registrando preventivo: {e}")
        return False


# ── Energía ────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_energia_lecturas(_sb: Client, tipo: str = None, dias: int = 90) -> list:
    try:
        desde = (datetime.utcnow().date().__class__.today() -
                 __import__("datetime").timedelta(days=dias)).isoformat()
        q = _sb.table("energia_lecturas").select("*").gte("fecha", desde).order("fecha")
        if tipo:
            q = q.eq("tipo", tipo)
        return q.execute().data or []
    except Exception as e:
        st.error(f"❌ Error cargando lecturas de energía: {e}")
        return []


def registrar_lectura_energia(sb: Client, datos: dict) -> bool:
    try:
        sb.table("energia_lecturas").insert({**datos, "created_at": datetime.utcnow().isoformat()}).execute()
        get_energia_lecturas.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error registrando lectura: {e}")
        return False


# ── Usuarios ───────────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_usuarios(_sb: Client) -> list:
    try:
        return _sb.table("usuarios_config").select("*").order("nombre_completo").execute().data or []
    except Exception as e:
        st.error(f"❌ Error cargando usuarios: {e}")
        return []


def crear_usuario(sb: Client, datos: dict) -> bool:
    try:
        sb.table("usuarios_config").insert(datos).execute()
        get_usuarios.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error creando usuario: {e}")
        return False


def actualizar_usuario(sb: Client, id_u: int, datos: dict) -> bool:
    try:
        sb.table("usuarios_config").update(datos).eq("id", id_u).execute()
        get_usuarios.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error actualizando usuario: {e}")
        return False
