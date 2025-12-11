# 📝 Historias de Usuario del Sistema de Control de Pagos

## Módulo 1: Importación y Carga de Datos
> Funcionalidad: Preparación de la Base de Datos

| ID | Prioridad | Historia de Usuario | Aceptación |
| :---: | :---: | :--- | :--- |
| **HU-I.1** | ALTA | Como **Administrador**, quiero **subir el archivo CSV/Excel de movimientos de Mercado Pago**, para cargar los nuevos pagos de forma masiva en el sistema. | El sistema debe mostrar un resumen de cuántos pagos se importaron y cuántos se ignoraron (por duplicidad). |
| **HU-I.2** | MEDIA | Como **Administrador**, quiero que el sistema **detecte automáticamente pagos duplicados** usando el `ID de Transacción MP`, para evitar procesar dos veces el mismo cobro. | Si se intenta subir un pago con un `ID de Transacción MP` ya existente, el sistema debe omitir la fila o actualizar solo los campos modificables. |
| **HU-I.3** | ALTA | Como **Administrador**, quiero **cargar o actualizar la base de datos de mis clientas** (NRO de Clienta, Nombre, Localidad, Campaña), para tener el listado de pedidos pendientes de cobro. | El sistema debe permitir subir un CSV inicial y tener una interfaz para crear y modificar registros de clientas individualmente. |

---

## Módulo 2: Conciliación de Pagos (Core del Sistema)
> Funcionalidad: Vinculación Pago-Cliente

| ID | Prioridad | Historia de Usuario | Aceptación |
| :---: | :---: | :--- | :--- |
| **HU-C.1** | ALTA | Como **Administrador**, quiero una **interfaz de conciliación** que liste todos los pagos con `Estado Conciliación = PENDIENTE`, para enfocarse solo en el trabajo pendiente. | La interfaz debe mostrar el `ID de Transacción MP`, `Monto Neto` y `Nombre del Pagador`. |
| **HU-C.2** | ALTA | Como **Administrador**, quiero poder **buscar rápidamente por `NRO de Clienta` o `Nombre`** en la interfaz de conciliación, para encontrar el pedido correspondiente al pago que estoy viendo. | El sistema debe usar una búsqueda dinámica (AJAX/JS) que filtre la lista de clientas con pedidos pendientes mientras escribo. |
| **HU-C.3** | ALTA | Como **Administrador**, quiero **vincular un pago de MP a un `NRO de Clienta`** con un solo clic/acción, para cambiar el `Estado del Pedido` a **COBRADO (A Entregar)**. | Al vincular, el sistema debe actualizar las dos tablas: `pagos_mp.fk_cliente_id` y `clientes_pedidos.fk_pago_mp_id`. |
| **HU-C.4** | MEDIA | Como **Administrador**, quiero una **alerta visual** si el `Monto Neto Recibido` (de MP) **no coincide** con el `Monto a Cobrar` (del Pedido), para revisar posibles errores o descuentos aplicados. | La interfaz debe marcar la fila con un color o icono si `Monto MP != Monto Pedido`. |

---

## Módulo 3: Liquidación y Seguimiento
> Funcionalidad: Cierre de Ciclo y Reportes

| ID | Prioridad | Historia de Usuario | Aceptación |
| :---: | :---: | :--- | :--- |
| **HU-L.1** | ALTA | Como **Administrador**, quiero ver un listado de todos los pedidos con `Estado del Pedido = COBRADO` y `Estado de Liquidación = PENDIENTE DE PAGO`, para saber qué pedidos debo liquidar. | La vista debe mostrar los pedidos listos para el pago a la empresa. |
| **HU-L.2** | ALTA | Como **Administrador**, quiero **seleccionar múltiples pedidos** de la lista de pendientes de pago y **registrar una única `Fecha de Liquidación`** para todos ellos, para procesar la transferencia masiva de forma eficiente. | El sistema debe aplicar la misma fecha a todos los pedidos seleccionados y cambiar su `Estado de Liquidación` a **LIQUIDADO**. |
| **HU-L.3** | MEDIA | Como **Administrador**, quiero un **Reporte de Liquidación** filtrable por `Fecha de Liquidación` y `Campaña`, para rendir cuentas a la empresa y analizar el volumen de trabajo por período. | El reporte debe sumar el total de `Monto a Liquidar` y listar los NROs de Clienta incluidos en el pago. |