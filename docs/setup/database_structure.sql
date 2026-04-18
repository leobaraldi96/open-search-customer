-- --------------------------------------------------------
-- Estructura de Base de Datos para Busca Clientes
-- Generado para la versión pública
-- --------------------------------------------------------

CREATE DATABASE IF NOT EXISTS `buscaclientes` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `buscaclientes`;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `prospectos`
-- --------------------------------------------------------

CREATE TABLE IF NOT EXISTS `prospectos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `empresa` varchar(255) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `telefono` varchar(100) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `contacto_clave` varchar(255) DEFAULT NULL,
  `direccion` text DEFAULT NULL,
  `ciudad` varchar(100) DEFAULT NULL,
  `provincia` varchar(100) DEFAULT NULL,
  `codigo_postal` varchar(20) DEFAULT NULL,
  `pais` varchar(50) DEFAULT NULL,
  `nombre_dueno` varchar(255) DEFAULT NULL,
  `cargo_dueno` varchar(100) DEFAULT NULL,
  `email_dueno` varchar(255) DEFAULT NULL,
  `telefono_dueno` varchar(100) DEFAULT NULL,
  `fuente_contacto` varchar(100) DEFAULT NULL,
  `redes_sociales` json DEFAULT NULL,
  `falla_detectada` varchar(255) DEFAULT NULL,
  `emails_hallados` varchar(500) DEFAULT NULL,
  `telefonos_hallados` varchar(500) DEFAULT NULL,
  `auditoria_texto` text DEFAULT NULL,
  `informe_detallado` json DEFAULT NULL,
  `puntos_de_dolor` text DEFAULT NULL,
  `pitch_ia` text DEFAULT NULL,
  `pitch_curado` text DEFAULT NULL,
  `audit_tecnico` json DEFAULT NULL,
  `tecnologias_detectadas` json DEFAULT NULL,
  `paginas_auditadas` int(11) DEFAULT 0,
  `whois_data` json DEFAULT NULL,
  `dominio_creado` datetime DEFAULT NULL,
  `dominio_expira` datetime DEFAULT NULL,
  `antiguedad_dominio` int(11) DEFAULT NULL,
  `urls_visitadas` json DEFAULT NULL,
  `observaciones_humanas` text DEFAULT NULL,
  `estado` varchar(50) DEFAULT 'nuevo',
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_prospectos_empresa` (`empresa`),
  KEY `ix_prospectos_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Volcado de datos de ejemplo
-- --------------------------------------------------------

INSERT INTO `prospectos` (`empresa`, `url`, `telefono`, `email`, `nombre_dueno`, `estado`, `puntos_de_dolor`, `audit_tecnico`, `pitch_ia`) VALUES
(
  'Restaurante El Faro', 
  'https://elfaromardelplata.com.ar', 
  '+54 223 444-5555', 
  'contacto@elfaro.com', 
  'Juan Pérez', 
  'nuevo', 
  NULL, 
  NULL, 
  NULL
),
(
  'Estudio Jurídico Global', 
  'https://ejglobal-test.com', 
  '+54 11 9999-8888', 
  'info@ejglobal.com', 
  'Dra. Martha Gómez', 
  'analizado', 
  'El sitio web tarda más de 8 segundos en cargar (LCP: 8.2s). No tiene certificado SSL activo, lo que genera desconfianza. La navegación en móviles es difícil debido a botones muy pequeños.', 
  '{
    "performance": {"score": 42, "lcp": 8200, "cls": 0.15, "inp": 250, "data_origin": "lab"},
    "seo": {"title": "Estudio Jurídico - Inicio", "h1Count": 0, "description": "Servicios legales."},
    "ux": {"smallOnesCount": 12, "hasHScroll": true},
    "security": {"hasSSL": false, "sslIssuer": "N/A"},
    "tech_stack": ["WordPress", "Apache", "PHP"]
  }', 
  'Hola Dra. Martha, estuve revisando el sitio de Estudio Jurídico Global y noté que tienen una gran oportunidad de mejora en la velocidad de carga. Actualmente el sitio tarda 8.2 segundos, lo que podría estar haciendo que pierdan clientes potenciales que buscan inmediatez...'
);
