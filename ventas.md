# Especificaciones Técnicas: Módulo de Ventas y Cuentas por Cobrar (POS Django)

Este documento define la estructura, modelos de base de datos y reglas de negocio para el desarrollo del **Módulo de Ventas**. Este módulo es el núcleo transaccional del sistema y debe gestionar la facturación (al contado), los créditos (fiados) y la integración con el inventario y la auditoría.

## 1. Estructura de la Aplicación
El módulo debe desarrollarse como una aplicación independiente para mantener la modularidad:

    python manage.py startapp ventas

*Asegúrate de registrar `'apps.ventas',` en `core/settings.py`.*

---

## 2. Modelos de Base de Datos (`apps/ventas/models.py`)

Para cumplir con la regla de **clientes globales compartidos entre sedes** y el **submódulo de deudas (fiados)**, la estructura relacional debe ser la siguiente:

    from django.db import models
    from apps.usuarios.models import Sede, Usuario
    from apps.inventario.models import ProductoInventario

    class Cliente(models.Model):
        # Los clientes NO tienen ForeignKey a Sede, por lo que son globales.
        cedula_o_rif = models.CharField(max_length=20, unique=True)
        nombre_completo = models.CharField(max_length=150)
        telefono = models.CharField(max_length=20, blank=True, null=True)
        direccion = models.TextField(blank=True, null=True)
        fecha_registro = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"{self.nombre_completo} - {self.cedula_o_rif}"

    class Venta(models.Model):
        TIPOS_PAGO = (
            ('CONTADO', 'Pago al Contado'),
            ('FIADO', 'Crédito / Fiado'),
        )
        ESTADOS = (
            ('PAGADA', 'Pagada Totalmente'),
            ('PENDIENTE', 'Pendiente por Pagar'), # Permite seguir agregando artículos si es fiado
        )
        
        cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
        vendedor = models.ForeignKey(Usuario, on_delete=models.PROTECT)
        sede = models.ForeignKey(Sede, on_delete=models.PROTECT)
        
        tipo_pago = models.CharField(max_length=10, choices=TIPOS_PAGO, default='CONTADO')
        estado = models.CharField(max_length=15, choices=ESTADOS, default='PAGADA')
        
        fecha_apertura = models.DateTimeField(auto_now_add=True)
        fecha_actualizacion = models.DateTimeField(auto_now=True)

        def calcular_total(self):
            # Suma todos los detalles de venta asociados
            return sum(detalle.subtotal for detalle in self.detalles.all())
            
        def calcular_saldo_deudor(self):
            # Total de la venta menos todos los abonos realizados
            total_abonos = sum(abono.monto for abono in self.abonos.all())
            return self.calcular_total() - total_abonos

        def __str__(self):
            return f"Venta #{self.id} - {self.cliente.nombre_completo} ({self.tipo_pago})"

    class DetalleVenta(models.Model):
        venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
        producto = models.ForeignKey(ProductoInventario, on_delete=models.PROTECT)
        cantidad = models.IntegerField()
        precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
        subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Abono(models.Model):
        venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='abonos')
        monto = models.DecimalField(max_digits=10, decimal_places=2)
        fecha = models.DateTimeField(auto_now_add=True)
        metodo_pago = models.CharField(max_length=50) # Ej: Efectivo, Pago Móvil, Transferencia
        cajero = models.ForeignKey(Usuario, on_delete=models.PROTECT)
        sede_donde_paga = models.ForeignKey(Sede, on_delete=models.PROTECT) # Permite pagar una deuda en otra sede

---

## 3. Reglas de Negocio y Lógica Operativa

### A. Clientes Globales y Deudas Compartidas
* El modelo `Cliente` es independiente de las sedes. Si un cliente deja una deuda (Venta tipo `FIADO` en estado `PENDIENTE`) en la Sede A, al visitar la Sede B el cajero podrá buscar su número de cédula, ver su saldo deudor y registrar un `Abono`.

### B. Lógica del Submódulo de "Fiados" (Créditos)
* **Acumulación de artículos:** Si una venta está marcada como `FIADO` y su estado es `PENDIENTE`, el sistema debe permitir crear nuevos registros en `DetalleVenta` vinculados a esa misma `Venta`. Esto cumple con el requisito de *"fiar más artículos al cliente en la misma venta"*.
* **Control de Abonos:** Cada vez que el cliente hace un pago parcial, se registra un `Abono`. Si la suma de los abonos alcanza el total de la Venta (calculado dinámicamente con `calcular_saldo_deudor() == 0`), el sistema debe cambiar automáticamente el estado de la Venta a `PAGADA`.

### C. Descuento Automático de Inventario
* Al guardar un `DetalleVenta` (ya sea al contado o fiado), se debe restar obligatoriamente la cantidad vendida del modelo `ProductoInventario`.
* **Validación Crítica:** La vista debe verificar que `producto.cantidad >= cantidad_solicitada`. Si no hay stock suficiente, se debe cancelar la operación y mostrar un error.

### D. Trazabilidad y Auditoría Estricta
Toda transacción monetaria debe registrarse en el módulo de auditoría.

    from apps.usuarios.models import RegistroAuditoria

    # Evento: Nueva Venta
    RegistroAuditoria.objects.create(
        usuario=request.user,
        accion=f"Registró venta al {venta.tipo_pago} por {venta.calcular_total()}$ (Cliente: {cliente.nombre_completo})",
        modulo="Ventas"
    )

    # Evento: Abono a deuda
    RegistroAuditoria.objects.create(
        usuario=request.user,
        accion=f"Registró abono de {abono.monto}$ a Venta #{venta.id} (Cliente: {cliente.nombre_completo})",
        modulo="Ventas"
    )

---

### E. Consulta, Filtros y Exportación de Reportes
* **Buscador y Filtros Dinámicos:** El panel principal del historial de ventas debe incluir una barra de búsqueda general (para ubicar ventas por nombre de cliente, cédula o ID de factura), además de filtros específicos por **rango de fechas** y por **sede**.
* **Generación de Reportes:** Utilizando las librerías `openpyxl` y `reportlab` (ya integradas en el proyecto), el sistema debe permitir exportar los resultados filtrados en formatos **Excel (.xlsx)** y **PDF**. Los reportes deben reflejar con precisión los filtros aplicados en pantalla y mostrar el total facturado, el estado de la deuda y el tipo de pago.

---

## 4. Lineamientos de Interfaz y Experiencia (UI/UX)
El submódulo de ventas es el más utilizado, por lo que su diseño debe ser sumamente ágil:
* **Tipografía y Colores:** Mantener tipografía **Roboto**. Usar `#2ecc71` (Verde) para ventas al contado/pagadas y `#e74c3c` (Rojo) para resaltar deudas y saldos pendientes.
* **Buscador de Clientes:** Implementar un buscador en tiempo real (por cédula o nombre) en la pantalla de facturación para evitar duplicar clientes.
* **Barra de Herramientas de Reportes:** El panel de consulta debe tener una estructura visual similar a la de auditoría, colocando los filtros (búsqueda, fechas, sede) y los botones de exportación (PDF y Excel) en la parte superior de la tabla de registros.
* **Iconos:** Utilizar íconos FontAwesome (ej. `<i class="fa-solid fa-hand-holding-dollar"></i>` para abonos, `<i class="fa-solid fa-cart-plus"></i>` para agregar productos).