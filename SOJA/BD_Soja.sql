USE bs4lgmqg2rgcpzv1f809;

DROP TABLE IF EXISTS labores;
DROP TABLE IF EXISTS insumos;
DROP TABLE IF EXISTS contratistas;
DROP TABLE IF EXISTS lotes;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    rol VARCHAR(50) DEFAULT 'Operador de Monitoreo'
);

CREATE TABLE lotes (
    id_lote INT AUTO_INCREMENT PRIMARY KEY,
    codigo_lote VARCHAR(20) NOT NULL UNIQUE,
    superficie_ha DECIMAL(6,2) NOT NULL,
    tipo_suelo VARCHAR(80) NOT NULL,
    coordenadas VARCHAR(80) NOT NULL,
    rendimiento_esperado_tn_ha VARCHAR(40) NOT NULL
);

CREATE TABLE contratistas (
    id_contratista INT AUTO_INCREMENT PRIMARY KEY,
    razon_social VARCHAR(120) NOT NULL,
    maquinaria_principal VARCHAR(120) NOT NULL
);

CREATE TABLE insumos (
    id_insumo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_insumo VARCHAR(100) NOT NULL,
    categoria VARCHAR(60) NOT NULL,
    dosis_referencia VARCHAR(60) NOT NULL
);

CREATE TABLE labores (
    id_labor INT AUTO_INCREMENT PRIMARY KEY,
    id_lote INT NOT NULL,
    id_insumo INT NULL,
    id_contratista INT NOT NULL,
    tipo_labor VARCHAR(60) NOT NULL,
    fecha_limite DATE NOT NULL,
    estado_labor VARCHAR(40) NOT NULL,
    color_semaforo ENUM('VERDE', 'AMARILLO', 'ROJO') NOT NULL,
    alerta_corta VARCHAR(60) NOT NULL,
    causa_alerta_detalle VARCHAR(255) NOT NULL,
    es_labor_actual BOOLEAN DEFAULT FALSE,
    ultima_actualizacion DATETIME NOT NULL,
    CONSTRAINT fk_labor_lote FOREIGN KEY (id_lote) REFERENCES lotes(id_lote),
    CONSTRAINT fk_labor_insumo FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo),
    CONSTRAINT fk_labor_contratista FOREIGN KEY (id_contratista) REFERENCES contratistas(id_contratista)
);

INSERT INTO usuarios (username, password_hash, nombre_completo, rol) VALUES
('olivia', SHA2('1234', 256), 'Olivia Frias', 'Administradora');

INSERT INTO lotes (id_lote, codigo_lote, superficie_ha, tipo_suelo, coordenadas, rendimiento_esperado_tn_ha) VALUES
(1, 'L-14', 50.00, 'Argiudol Típico', 'Lat -33.85, Lon -60.51', '3.8 a 4.2 Tn/ha'),
(2, 'L-15', 75.00, 'Hapludol Éntico', 'Lat -33.87, Lon -60.53', '3.2 a 3.6 Tn/ha'),
(3, 'L-16', 120.00, 'Argiudol', 'Lat -33.89, Lon -60.55', '3.5 a 4.0 Tn/ha'),
(4, 'L-17', 40.00, 'Argiudol Vértico', 'Lat -33.91, Lon -60.58', '3.6 a 4.1 Tn/ha');

INSERT INTO contratistas (id_contratista, razon_social, maquinaria_principal) VALUES
(1, 'AgroServicios del Litoral S.R.L.', 'Sembradora de Directa 24 surcos'),
(2, 'Fumigaciones Pampa Húmeda', 'Pulverizadora Autopropulsada 3000L'),
(3, 'Transporte y Cosecha El Triunfo S.A.', 'Cosechadora Axial Clase 7');

INSERT INTO insumos (id_insumo, nombre_insumo, categoria, dosis_referencia) VALUES
(1, 'Semilla Soja Intacta', 'Semilla Certificada', '75 kg / hectárea'),
(2, 'Glifosato Premium 66%', 'Herbicida Sistémico', '2.5 litros / hectárea'),
(3, 'Inoculante Bradyrhizobium', 'Biológico / Tratamiento', '200 ml / 100 kg de semilla'),
(4, 'Sin insumo (Labor mecánica)', 'Cosecha / Trilla', 'No aplica');

-- Fechas coherentes con "hoy" = 15/11/2026 y con el ciclo de la soja (siembra nov, cosecha abr-may).
-- Regla del semáforo:
--   VERDE    = finalizada, o pendiente con plazo holgado
--   AMARILLO = pendiente y próxima a vencer
--   ROJO     = atrasada o frenada por riesgo agronómico
INSERT INTO labores (id_lote, id_insumo, id_contratista, tipo_labor, fecha_limite, estado_labor, color_semaforo, alerta_corta, causa_alerta_detalle, es_labor_actual, ultima_actualizacion) VALUES
-- L-14
(1, 1, 1, 'Siembra', '2026-11-15', 'Finalizado', 'VERDE', 'Sin alertas', 'Implantación completada con humedad óptima en perfil.', TRUE, '2026-11-01 09:15:00'),
-- L-15
(2, 1, 1, 'Siembra', '2026-11-05', 'Finalizado', 'VERDE', 'Sin alertas', 'Emergencia pareja de plántulas sin novedades.', FALSE, '2026-11-05 18:00:00'),
(2, 2, 2, 'Pulverización', '2026-11-25', 'Pendiente', 'AMARILLO', 'Próximo a vencer', 'Ventana de aplicación sujeta a pronóstico de vientos menores a 15 km/h.', TRUE, '2026-11-12 10:00:00'),
-- L-16
(3, 1, 1, 'Siembra', '2026-11-10', 'Finalizado', 'VERDE', 'Sin alertas', 'Siembra directa finalizada según planificación anual.', FALSE, '2026-11-10 17:30:00'),
(3, 2, 2, 'Pulverización', '2026-11-12', 'Atrasado', 'ROJO', 'Riesgo', 'Exceso de humedad en suelo. Sin piso para ingreso de la pulverizadora.', TRUE, '2026-11-13 08:30:00'),
(3, 4, 3, 'Cosecha', '2027-04-25', 'Pendiente', 'VERDE', 'En fecha', 'Cosecha programada según el ciclo del cultivo.', FALSE, '2026-11-10 17:30:00'),
-- L-17
(4, 1, 1, 'Siembra', '2026-11-20', 'En fecha', 'VERDE', 'Humedad óptima', 'Lote barbechado listo y en fecha programada de siembra.', TRUE, '2026-11-12 08:00:00');