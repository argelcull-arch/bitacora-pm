# 🚀 GUÍA DE MIGRACIÓN — Bitácora PM → NOVA

## Pasos para activar NOVA en Supabase + Streamlit Cloud

---

## PASO 1: Ejecutar el SQL en Supabase

1. Abre tu proyecto en [supabase.com](https://supabase.com)
2. Ve a **SQL Editor → New Query**
3. Copia y pega el contenido completo de `supabase_schema.sql`
4. Haz clic en **Run**

> Esto crea todas las tablas nuevas y **amplía** la tabla `tareas` existente  
> con las columnas `area_id`, `categoria`, `prioridad` y `estado`.  
> **Tus datos existentes NO se borran.**

---

## PASO 2: Verificar permisos en Supabase

En Supabase → **Authentication → Policies**, asegúrate de que las tablas  
nuevas tienen RLS (Row Level Security) desactivado, o agrega políticas permisivas  
para `anon` key. El SQL ya incluye los `GRANT` necesarios.

---

## PASO 3: Actualizar Streamlit Cloud

En tu app de Streamlit Community Cloud:

1. **Secrets**: Los mismos `SUPABASE_URL` y `SUPABASE_KEY` siguen funcionando.  
   No hay que cambiar nada.

2. **requirements.txt**: Actualiza el archivo en tu repositorio (ya está modificado).  
   Las nuevas dependencias son:
   - `openpyxl` — para reportes Excel  
   - `reportlab` — para reportes PDF  
   - `pandas` — para análisis de datos  
   - `plotly` — para gráficos  
   - `kaleido` — para exportar gráficos a imagen  
   - `Pillow` — para manejo de imágenes

3. **Archivos nuevos**: Sube al repositorio:
   - `config.py`
   - `auth.py`  
   - `database.py`
   - `modules/__init__.py`
   - `modules/dashboard.py`
   - `modules/requerimientos.py`
   - `modules/pendientes.py`
   - `modules/inventario.py`
   - `modules/activos.py`
   - `modules/preventivo.py`
   - `modules/energia.py`
   - `modules/estadisticas.py`
   - `modules/reportes.py`
   - `modules/configuracion.py`

4. Haz **Reboot** de la app en Streamlit Cloud.

---

## PASO 4: Primer inicio de sesión

Usuarios disponibles desde el inicio:

| Usuario   | Contraseña | Rol     |
|-----------|------------|---------|
| admin     | admin2024  | Admin   |
| tecnico1  | mant2024   | Técnico |
| tecnico2  | mant2024   | Técnico |
| tecnico3  | mant2024   | Técnico |

> Desde **⚙️ Configuración → Usuarios** puedes agregar nuevos usuarios y  
> cambiar contraseñas a nombres reales.

---

## PASO 5: Configurar el hotel

1. Inicia sesión como `admin`
2. Ve a **⚙️ Configuración → 🏨 Hotel**
3. Agrega el nombre real del hotel, eslogan y jefe de ingeniería
4. Para el logo: sube tu imagen PNG/JPG a **Supabase Storage → New Bucket (público)**,  
   copia la URL pública y pégala en el campo "URL del Logo"
5. Ve a **🛏️ Habitaciones** y genera las habitaciones con el formato que prefieras

---

## PASO 6: Cargar datos iniciales (recomendado)

1. **Áreas**: En Configuración → Áreas, agrega las áreas reales del hotel  
   (además de las habitaciones auto-generadas)
2. **Inventario**: En 📦 Inventario → Nuevo Ítem, registra los materiales y herramientas
3. **Activos**: En 🔧 Activos → Nuevo Activo, registra los equipos principales
4. **Preventivo**: Las tareas predefinidas ya están cargadas (revisa en ✅ Preventivo)

---

## Estructura de archivos resultante

```
bitacora-pm/
├── app.py                ← Entry point (reemplaza el anterior)
├── config.py             ← CSS + constantes + helpers UI
├── auth.py               ← Sistema de autenticación
├── database.py           ← Funciones Supabase
├── requirements.txt      ← Dependencias actualizadas
├── supabase_schema.sql   ← SQL para ejecutar en Supabase
├── MIGRACION.md          ← Este archivo
└── modules/
    ├── __init__.py
    ├── dashboard.py      ← Módulo 1
    ├── requerimientos.py ← Módulo 2
    ├── pendientes.py     ← Módulo 3
    ├── inventario.py     ← Módulo 4
    ├── activos.py        ← Módulo 5
    ├── preventivo.py     ← Módulo 6
    ├── energia.py        ← Módulo 7
    ├── estadisticas.py   ← Módulo 8
    ├── reportes.py       ← Módulo 9
    └── configuracion.py  ← Módulo 10
```

---

## Compatibilidad con datos existentes

Los datos de la tabla `tareas` original se mantienen intactos.  
Las nuevas columnas (`area_id`, `categoria`, `prioridad`, `estado`) tendrán  
valores por defecto: `NULL`, `'General'`, `'Media'`, `'Abierto'` respectivamente.

Las tareas existentes aparecerán en **📋 Requerimientos** filtradas por el  
usuario que las creó, con estado `Abierto` y prioridad `Media`.

---

---

## Actualización v3 — Categorías dinámicas + Fixes

### SQL adicional a ejecutar en Supabase:

```sql
CREATE TABLE IF NOT EXISTS categorias (
    id         SERIAL PRIMARY KEY,
    nombre     TEXT NOT NULL,
    modulo     TEXT NOT NULL DEFAULT 'requerimientos',
    activo     BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO categorias (nombre, modulo) VALUES
    ('Eléctrico','requerimientos'),('Plomería','requerimientos'),
    ('AC/Climatización','requerimientos'),('Equipos AV','requerimientos'),
    ('Carpintería','requerimientos'),('Pintura','requerimientos'),
    ('Equipos de Cocina','requerimientos'),('Piscina','requerimientos'),
    ('General','requerimientos')
ON CONFLICT DO NOTHING;

GRANT ALL ON categorias TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE categorias_id_seq TO anon, authenticated;
```

### Cambios v3:
- **Requerimientos → Área**: campo de texto libre (sin dropdown)
- **Requerimientos → Categoría**: cargada desde tabla `categorias` en Supabase
- **Configuración → 🏷️ Categorías**: nuevo tab para agregar/desactivar/eliminar categorías
- **Energía**: todos los valores son enteros (`step=1, format="%d"`)

*NOVA v3*

