# Conciliador de Pagos - Zona 127b

Sistema web para la conciliación de cobros de Mercado Pago con pedidos de clientas, gestión de rendimientos y control de transferencias.

## 📋 Características

### Módulo 1: Importación de Datos
- **Carga de Pedidos (Clientes)**: Importación desde CSV (`clientes.csv`).
    - Detección inteligente de duplicados (Orden + Cuenta + Campaña).
    - Asignación de campaña (ej: `2025-01`).
- **Carga de Pagos (Mercado Pago)**: Importación de extractos (`account_statement.csv`).
    - Conversión automática de formatos de moneda europeos.
    - Ignora transacciones ya registradas.

### Módulo 2: Conciliación y Finanzas
- **Conciliación de Pagos**:
    - Interfaz para vincular pagos entrantes (`monto > 0`) con clientes pendientes.
    - Búsqueda en tiempo real (AJAX) por nombre o cuenta.
    - Filtros por fecha, pagador y ordenamiento.
- **Rendimientos**: Visualización separada de ganancias financieras de Mercado Pago.
- **Transferencias**: Listado de egresos y transferencias enviadas.

### Módulo 3: Liquidación (Próximamente)
- Gestión de pagos a proveedores y liquidación de pedidos cobrados.

## 🛠 Tecnologías

- **Backend**: Python 3.11 + Flask
- **Base de Datos**: MySQL 8.0
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Infraestructura**: Docker & Docker Compose

## 🚀 Instalación y Despliegue

### Requisitos
- Docker y Docker Compose instalados.

### Pasos
1. **Clonar el repositorio**:
   ```bash
   git clone <repo-url>
   cd conciliador-zona127b
   ```

2. **Configurar Variables de Entorno**:
   Crear un archivo `.env` en la raíz (basado en el ejemplo):
   ```ini
   DB_HOST=db
   DB_USER=user
   DB_PASSWORD=password
   DB_NAME=sistema_pagos_mp
   SECRET_KEY=mi_super_secreto
   ```

3. **Iniciar la Aplicación**:
   ```bash
   cd compose
   docker compose up --build -d
   ```
   La base de datos se inicializará automáticamente con el esquema definido en `schema.sql`.

4. **Acceder**:
   - Web: http://localhost:5000

## 📖 Uso

### 1. Importar Datos
Navegar a **Importar Datos**.
- Subir `clientes.csv` seleccionando la campaña correspondiente.
- Subir el extracto de Mercado Pago.

### 2. Conciliar
Navegar a **Conciliación**.
- Verás la lista de pagos pendientes de asignación.
- Usa los filtros para buscar pagos específicos.
- Haz clic en **Vincular** y busca al cliente por nombre o cuenta.
- El sistema sugerirá coincidencias y resaltará montos exactos.

### 3. Consultar Finanzas
- **Rendimientos**: Para ver ingresos pasivos.
- **Transferencias**: Para controlar salidas de dinero.

## 📂 Estructura del Proyecto

```
.
├── app.py                 # Aplicación Flask principal y rutas
├── db.py                  # Conexión a Base de Datos
├── importer.py            # Lógica de procesamiento de CSVs
├── schema.sql             # Esquema de Base de Datos
├── templates/             # Vistas HTML (Jinja2)
│   ├── base.html
│   ├── conciliacion.html
│   ├── importar.html
│   ├── index.html
│   ├── rendimientos.html
│   └── transferencias.html
├── compose/
│   └── docker-compose.yml # Orquestación de contenedores
└── Dockerfile             # Definición de imagen Python/Flask
```

## ⚠️ Notas Importantes
- **Duplicados**: El importador de clientes evita duplicar pedidos si coinciden Orden, Cuenta y Campaña.
- **Formatos CSV**: Se espera formato con punto y coma (`;`) como separador y montos con coma (`,`) como decimal (formato estándar de exportación local).