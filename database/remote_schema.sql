CREATE TABLE IF NOT EXISTS v_lineas_facturadas_analiticas (
    cliente TEXT,
    nombre_cliente TEXT,
    codigo_pt TEXT,
    descripcion TEXT,
    marca TEXT,
    nombre_marca TEXT,
    linea TEXT,
    pais TEXT,
    moneda TEXT,
    fecha_ingreso DATE,
    anio INTEGER,
    mes INTEGER,
    venta_neta_asignada_linea NUMERIC,
    venta_bruta_linea NUMERIC,
    costo_estimado_linea NUMERIC,
    margen_estimado_linea NUMERIC,
    cantidad_convertida NUMERIC,
    serie TEXT,
    correlativo TEXT
);

CREATE TABLE IF NOT EXISTS pt_marcas (
    marca TEXT PRIMARY KEY,
    nombre TEXT
);

CREATE TABLE IF NOT EXISTS pt_clientes (
    cliente TEXT PRIMARY KEY,
    nombre_cliente TEXT
);

CREATE INDEX IF NOT EXISTS ix_remote_sales_date
    ON v_lineas_facturadas_analiticas (fecha_ingreso);
CREATE INDEX IF NOT EXISTS ix_remote_sales_product
    ON v_lineas_facturadas_analiticas (codigo_pt);
CREATE INDEX IF NOT EXISTS ix_remote_sales_client
    ON v_lineas_facturadas_analiticas (cliente);
