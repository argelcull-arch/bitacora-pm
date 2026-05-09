-- ============================================================
-- NOVA — Sistema de Gestión de Ingeniería Hotelera  v2
-- Schema completo para Supabase (PostgreSQL)
-- Ejecutar en: Supabase → SQL Editor → New Query
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- 0. TABLA: configuracion  (nueva — v2)
--    Par clave/valor para configuración del hotel.
--    REEMPLAZA a configuracion_hotel.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS configuracion (
    clave  TEXT PRIMARY KEY,
    valor  TEXT
);

INSERT INTO configuracion (clave, valor) VALUES
    ('nombre_hotel',    'Hotel NOVA'),
    ('slogan',          'Excelencia en Ingeniería'),
    ('logo_url',        ''),
    ('jefe_ingenieria', 'Jefe de Ingeniería'),
    ('formato_hab',     'simple'),
    ('num_habitaciones','50'),
    ('piso_inicio',     '1')
ON CONFLICT (clave) DO NOTHING;


-- ─────────────────────────────────────────────────────────────
-- 1. TABLA: configuracion_hotel
--    Parámetros globales del hotel (nombre, logo, etc.)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS configuracion_hotel (
    id            SERIAL PRIMARY KEY,
    clave         TEXT UNIQUE NOT NULL,
    valor         TEXT,
    descripcion   TEXT,
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Insertar configuración inicial
INSERT INTO configuracion_hotel (clave, valor, descripcion) VALUES
    ('nombre_hotel',    'Hotel NOVA',               'Nombre del hotel'),
    ('slogan',          'Excelencia en Ingeniería',  'Eslogan o subtítulo'),
    ('logo_url',        '',                          'URL pública del logo (Supabase Storage)'),
    ('jefe_ingenieria', 'Jefe de Ingeniería',        'Nombre del responsable para firma en reportes'),
    ('formato_hab',     'simple',                    'Formato habitaciones: simple=1,2,3 / piso=101,102'),
    ('num_habitaciones','50',                        'Número total de habitaciones'),
    ('piso_inicio',     '1',                         'Piso inicial para formato por piso')
ON CONFLICT (clave) DO NOTHING;


-- ─────────────────────────────────────────────────────────────
-- 2. TABLA: areas
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS areas (
    id         SERIAL PRIMARY KEY,
    nombre     TEXT NOT NULL,
    tipo       TEXT NOT NULL DEFAULT 'general',
    -- tipos: habitacion, area_comun, servicio, cocina, bar,
    --        restaurante, piscina, ingenieria, administracion, general
    piso       TEXT,
    activo     BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Áreas iniciales de ejemplo
INSERT INTO areas (nombre, tipo, piso, activo) VALUES
    ('Lobby',            'area_comun',    '1',  TRUE),
    ('Restaurante',      'restaurante',   '1',  TRUE),
    ('Bar',              'bar',           '1',  TRUE),
    ('Piscina',          'piscina',       'EXT',TRUE),
    ('Cuarto de Máquinas','ingenieria',   'B1', TRUE),
    ('Cocina Principal', 'cocina',        '1',  TRUE),
    ('Gimnasio',         'area_comun',    '2',  TRUE),
    ('Recepción',        'administracion','1',  TRUE),
    ('Lavandería',       'servicio',      'B1', TRUE),
    ('Azotea',           'area_comun',    'AZ', TRUE)
ON CONFLICT DO NOTHING;


-- ─────────────────────────────────────────────────────────────
-- 3. TABLA: usuarios_config
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS usuarios_config (
    id              SERIAL PRIMARY KEY,
    username        TEXT UNIQUE NOT NULL,
    nombre_completo TEXT NOT NULL,
    password_plain  TEXT NOT NULL,
    rol             TEXT NOT NULL DEFAULT 'tecnico',
    -- roles: admin, tecnico
    activo          BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Usuarios iniciales (mismos que el diccionario actual)
INSERT INTO usuarios_config (username, nombre_completo, password_plain, rol) VALUES
    ('admin',    'Administrador',  'admin2024', 'admin'),
    ('tecnico1', 'Técnico 1',      'mant2024',  'tecnico'),
    ('tecnico2', 'Técnico 2',      'mant2024',  'tecnico'),
    ('tecnico3', 'Técnico 3',      'mant2024',  'tecnico')
ON CONFLICT (username) DO NOTHING;


-- ─────────────────────────────────────────────────────────────
-- 4. TABLA: tareas (EXISTENTE — ampliar con nuevas columnas)
-- ─────────────────────────────────────────────────────────────
-- Primero crear si no existe
CREATE TABLE IF NOT EXISTS tareas (
    id         SERIAL PRIMARY KEY,
    usuario    TEXT,
    lugar      TEXT,
    detalle    TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agregar columnas nuevas (seguro — no borra datos existentes)
ALTER TABLE tareas ADD COLUMN IF NOT EXISTS area_id    INTEGER REFERENCES areas(id);
ALTER TABLE tareas ADD COLUMN IF NOT EXISTS categoria  TEXT DEFAULT 'General';
ALTER TABLE tareas ADD COLUMN IF NOT EXISTS prioridad  TEXT DEFAULT 'Media';
ALTER TABLE tareas ADD COLUMN IF NOT EXISTS estado     TEXT DEFAULT 'Abierto';
-- estados: Abierto, En Proceso, Resuelto
-- prioridades: Alta, Media, Baja
-- categorias: Eléctrico, Plomería, AC-Climatización, Equipos AV,
--             Carpintería, Pintura, Equipos de Cocina, Piscina, General


-- ─────────────────────────────────────────────────────────────
-- 5. TABLA: pendientes
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pendientes (
    id              SERIAL PRIMARY KEY,
    area_id         INTEGER REFERENCES areas(id),
    descripcion     TEXT NOT NULL,
    prioridad       TEXT NOT NULL DEFAULT 'Media',
    estado          TEXT NOT NULL DEFAULT 'Abierto',
    asignado_a      TEXT,
    usuario_creador TEXT,
    notas           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    resuelto_at     TIMESTAMPTZ
);


-- ─────────────────────────────────────────────────────────────
-- 6. TABLA: inventario_items
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS inventario_items (
    id           SERIAL PRIMARY KEY,
    nombre       TEXT NOT NULL,
    categoria    TEXT NOT NULL DEFAULT 'Otros',
    -- categorias: Focos, Cables, Repuestos AC, Herramientas,
    --             Equipos AV, Materiales Eléctricos, Plomería,
    --             Limpieza, Otros
    descripcion  TEXT,
    ubicacion    TEXT,
    stock_actual NUMERIC(10,2) DEFAULT 0,
    stock_minimo NUMERIC(10,2) DEFAULT 0,
    unidad       TEXT DEFAULT 'unidad',
    activo       BOOLEAN DEFAULT TRUE,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Items de inventario de ejemplo
INSERT INTO inventario_items (nombre, categoria, descripcion, ubicacion, stock_actual, stock_minimo, unidad) VALUES
    ('Focos LED 10W',         'Focos',                 'Focos LED blanco frío',    'Almacén A', 45,  20, 'unidad'),
    ('Cable THW 12',          'Cables',                'Cable calibre 12 AWG',     'Almacén A', 100, 50, 'metros'),
    ('Filtro AC 24BTU',       'Repuestos AC',          'Filtro para split 24000BTU','Almacén B', 8,   5, 'unidad'),
    ('Llaves de tuercas set', 'Herramientas',          'Juego llaves combinadas',   'Taller',    3,   2, 'juego'),
    ('Cinta aislante',        'Materiales Eléctricos', 'Cinta 3M 33+',             'Almacén A', 15,  10, 'rollo'),
    ('Teflón',                'Plomería',              'Cinta teflón 3/4"',        'Almacén A', 20,  10, 'unidad'),
    ('Desinfectante',         'Limpieza',              'Desinfectante multiusos',  'Almacén C', 12,  6,  'litro')
ON CONFLICT DO NOTHING;


-- ─────────────────────────────────────────────────────────────
-- 7. TABLA: inventario_movimientos
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS inventario_movimientos (
    id         SERIAL PRIMARY KEY,
    item_id    INTEGER NOT NULL REFERENCES inventario_items(id) ON DELETE CASCADE,
    tipo       TEXT NOT NULL,
    -- tipos: entrada, salida
    cantidad   NUMERIC(10,2) NOT NULL,
    usuario    TEXT,
    motivo     TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────
-- 8. TABLA: activos
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activos (
    id                     SERIAL PRIMARY KEY,
    nombre                 TEXT NOT NULL,
    categoria              TEXT NOT NULL DEFAULT 'General',
    -- categorias: AC/Climatización, Eléctrico, Plomería, Cocina,
    --             Audio-Visual, Seguridad, Piscina, General
    marca                  TEXT,
    modelo                 TEXT,
    serial                 TEXT,
    area_id                INTEGER REFERENCES areas(id),
    fecha_instalacion      DATE,
    ultimo_mantenimiento   DATE,
    desc_ultimo_mant       TEXT,
    proximo_mantenimiento  DATE,
    estado                 TEXT DEFAULT 'Operativo',
    -- estados: Operativo, En Reparación, Fuera de Servicio
    notas                  TEXT,
    created_at             TIMESTAMPTZ DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────
-- 9. TABLA: activos_historial
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activos_historial (
    id            SERIAL PRIMARY KEY,
    activo_id     INTEGER NOT NULL REFERENCES activos(id) ON DELETE CASCADE,
    fecha         DATE NOT NULL,
    tipo_trabajo  TEXT,
    descripcion   TEXT,
    realizado_por TEXT,
    costo         NUMERIC(10,2),
    created_at    TIMESTAMPTZ DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────
-- 10. TABLA: preventivo_tareas
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS preventivo_tareas (
    id          SERIAL PRIMARY KEY,
    nombre      TEXT NOT NULL,
    descripcion TEXT,
    frecuencia  TEXT NOT NULL DEFAULT 'diaria',
    -- frecuencias: diaria, semanal, mensual
    area_id     INTEGER REFERENCES areas(id),
    activo      BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Tareas preventivas predefinidas
INSERT INTO preventivo_tareas (nombre, descripcion, frecuencia) VALUES
    -- Diarias
    ('Revisión de Piscina',           'Verificar cloro (1-3 ppm), pH (7.2-7.8), turbidez y temperatura',                'diaria'),
    ('Inspección de Ascensores',      'Verificar funcionamiento, puertas, iluminación interna y alarmas',               'diaria'),
    ('Lectura de Medidores Energía',  'Registrar kWh del medidor principal y submmedidores',                            'diaria'),
    ('Revisión de Calderas',          'Verificar presión, temperatura, quemadores y válvulas de seguridad',             'diaria'),
    -- Semanales
    ('Revisión de Filtros AC',        'Limpiar o reemplazar filtros de unidades split y manejadoras',                   'semanal'),
    ('Prueba de Generador',           'Arrancar generador de emergencia, verificar combustible y transferencia',        'semanal'),
    ('Inspección Contra Incendios',   'Verificar extintores, detectores de humo, rociadores y salidas de emergencia',   'semanal'),
    ('Revisión de Cocinas',           'Inspeccionar campanas, filtros de grasa, quemadores y sistemas de gas',          'semanal'),
    -- Mensuales
    ('Mantenimiento de Bombas',       'Lubricar, verificar presión, caudal y empaquetaduras de bombas hidráulicas',     'mensual'),
    ('Revisión Eléctrica General',    'Inspeccionar tableros, breakers, conexiones, tierra física y cableado',          'mensual'),
    ('Limpieza de Cisternas',         'Vaciar, limpiar y desinfectar cisternas y tinacos de agua',                      'mensual'),
    ('Inspección de Extintores',      'Verificar carga, fechas de vencimiento, seguros y accesibilidad de extintores',  'mensual')
ON CONFLICT DO NOTHING;


-- ─────────────────────────────────────────────────────────────
-- 11. TABLA: preventivo_registros
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS preventivo_registros (
    id              SERIAL PRIMARY KEY,
    tarea_id        INTEGER NOT NULL REFERENCES preventivo_tareas(id) ON DELETE CASCADE,
    completado_por  TEXT,
    fecha           DATE NOT NULL DEFAULT CURRENT_DATE,
    cumplido        BOOLEAN DEFAULT FALSE,
    observaciones   TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────
-- 12. TABLA: energia_lecturas
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS energia_lecturas (
    id         SERIAL PRIMARY KEY,
    tipo       TEXT NOT NULL,
    -- tipos: electricidad, agua, gas
    valor      NUMERIC(12,3) NOT NULL,
    unidad     TEXT NOT NULL DEFAULT 'kWh',
    fecha      DATE NOT NULL DEFAULT CURRENT_DATE,
    usuario    TEXT,
    notas      TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────
-- ÍNDICES PARA RENDIMIENTO
-- ─────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_tareas_usuario       ON tareas(usuario);
CREATE INDEX IF NOT EXISTS idx_tareas_created_at    ON tareas(created_at);
CREATE INDEX IF NOT EXISTS idx_tareas_estado        ON tareas(estado);
CREATE INDEX IF NOT EXISTS idx_pendientes_estado    ON pendientes(estado);
CREATE INDEX IF NOT EXISTS idx_pendientes_created   ON pendientes(created_at);
CREATE INDEX IF NOT EXISTS idx_inventario_mov_item  ON inventario_movimientos(item_id);
CREATE INDEX IF NOT EXISTS idx_activos_historial_id ON activos_historial(activo_id);
CREATE INDEX IF NOT EXISTS idx_preventivo_reg_fecha ON preventivo_registros(fecha);
CREATE INDEX IF NOT EXISTS idx_energia_tipo_fecha   ON energia_lecturas(tipo, fecha);


-- ─────────────────────────────────────────────────────────────
-- PERMISOS (necesarios para Supabase con anon key)
-- ─────────────────────────────────────────────────────────────
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ============================================================
-- FIN DEL SCHEMA — NOVA v1.0
-- ============================================================
