-- Creación de la base de datos
CREATE DATABASE IF NOT EXISTS sistema_pagos_mp;
USE sistema_pagos_mp;

-- Tabla: pagos_mp
-- Registro del Movimiento de Mercado Pago
-- Se crea primero sin la FK a clientes_pedidos para evitar errores de referencia circular inicial (o se usa ALTER TABLE después).
CREATE TABLE IF NOT EXISTS pagos_mp (
    id_pago_mp BIGINT NOT NULL, -- ID Único de MP (normalmente numérico largo)
    fecha_cobro DATETIME NOT NULL,
    monto_neto DECIMAL(10, 2) NOT NULL,
    nombre_pagador VARCHAR(255),
    fk_cliente_id INT, -- Enlace al Cliente Conciliado (se permite NULL inicialmente)
    estado_conciliacion ENUM('PENDIENTE', 'CONCILIADO', 'IGNORAR') DEFAULT 'PENDIENTE',
    PRIMARY KEY (id_pago_mp),
    UNIQUE KEY idx_fk_cliente_unique (fk_cliente_id) -- Garantiza relación 1:1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: clientes_pedidos
-- Registro de la Clienta y Pedido
CREATE TABLE IF NOT EXISTS clientes_pedidos (
    cliente_id INT AUTO_INCREMENT NOT NULL, -- PK interna
    orden INT, -- Nuevo campo
    reparto INT, -- Nuevo campo
    cuenta BIGINT, -- Nuevo campo para ID externo
    nombre_clienta VARCHAR(255) NOT NULL,
    localidad VARCHAR(255),
    campana VARCHAR(100),
    monto_pedido DECIMAL(10, 2) NOT NULL,
    fk_pago_mp_id BIGINT, -- Enlace al Pago Conciliado
    fecha_liquidacion DATETIME DEFAULT NULL,
    estado_liquidacion ENUM('PENDIENTE', 'LIQUIDADO') DEFAULT 'PENDIENTE',
    PRIMARY KEY (cliente_id),
    UNIQUE KEY idx_fk_pago_mp_unique (fk_pago_mp_id), -- Garantiza relación 1:1
    CONSTRAINT fk_pedido_pago FOREIGN KEY (fk_pago_mp_id) REFERENCES pagos_mp(id_pago_mp) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Agregar la FK faltante en pagos_mp ahora que clientes_pedidos existe
ALTER TABLE pagos_mp
ADD CONSTRAINT fk_pago_cliente
FOREIGN KEY (fk_cliente_id) REFERENCES clientes_pedidos(cliente_id) ON DELETE SET NULL ON UPDATE CASCADE;

-- Crear índices adicionales si son necesarios para búsquedas rápidas (ej. búsquedas AJAX)
CREATE INDEX idx_nombre_clienta ON clientes_pedidos(nombre_clienta);
CREATE INDEX idx_fecha_cobro ON pagos_mp(fecha_cobro);
