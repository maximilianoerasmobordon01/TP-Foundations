
-- =======================================
-- Script Idempotente para Esquema EV
-- =======================================

-- Eliminar tablas en orden inverso de dependencias
DROP TABLE IF EXISTS electric_vehicles CASCADE;
DROP TABLE IF EXISTS models CASCADE;
DROP TABLE IF EXISTS makes CASCADE;
DROP TABLE IF EXISTS regions CASCADE;
DROP TABLE IF EXISTS vehicle_types CASCADE;

-- Tabla de fabricantes
CREATE TABLE IF NOT EXISTS makes (
    make_id SERIAL PRIMARY KEY,
    make_name VARCHAR(100) UNIQUE NOT NULL
);

-- Tabla de modelos
CREATE TABLE IF NOT EXISTS models (
    model_id SERIAL PRIMARY KEY,
    make_id INT NOT NULL REFERENCES makes(make_id),
    model_name VARCHAR(100) NOT NULL,
    UNIQUE (make_id, model_name)
);

-- Tabla de regiones (ciudad, condado, ZIP, estado)
CREATE TABLE IF NOT EXISTS regions (
    region_id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    county VARCHAR(100),
    zipcode CHAR(5),
    state VARCHAR(50)
);

-- Tabla de tipos de vehículo
CREATE TABLE IF NOT EXISTS vehicle_types (
    type_id SERIAL PRIMARY KEY,
    fuel_type VARCHAR(50),       -- BEV, PHEV, etc.
    vehicle_class VARCHAR(50)    -- SUV, Sedan, etc.
);

-- Tabla principal de vehículos eléctricos
CREATE TABLE IF NOT EXISTS electric_vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    vin VARCHAR(50) UNIQUE,          -- Número de identificación del vehículo
    model_year INT NOT NULL,
    electric_range INT,              -- Rango eléctrico estimado
    registration_date DATE,          -- Si existe en dataset
    electric_utility VARCHAR(150),   -- Compañía eléctrica si está disponible
    make_id INT NOT NULL REFERENCES makes(make_id),
    model_id INT NOT NULL REFERENCES models(model_id),
    region_id INT REFERENCES regions(region_id),
    type_id INT REFERENCES vehicle_types(type_id)
);

