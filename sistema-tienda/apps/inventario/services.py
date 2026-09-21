from django.db import transaction

from apps.usuarios.models import RegistroAuditoria

from .models import ProductoInventario


class StockActivoError(ValueError):
    """Raised when a product with stock is requested for deletion."""


def _registrar_auditoria(usuario, accion, request=None):
    ip_origen = None
    if request:
        ip_origen = request.META.get('REMOTE_ADDR')

    RegistroAuditoria.objects.create(
        usuario=usuario,
        accion=accion[:255],
        modulo='Inventario',
        ip_origen=ip_origen,
    )


@transaction.atomic
def crear_producto(*, datos, usuario, request=None):
    producto = ProductoInventario.objects.create(**datos)
    _registrar_auditoria(
        usuario,
        f'Creó el producto de inventario: {producto.nombre} (Stock: {producto.cantidad})',
        request,
    )
    return producto


@transaction.atomic
def actualizar_producto(*, producto, datos, usuario, request=None):
    for campo, valor in datos.items():
        setattr(producto, campo, valor)
    producto.save()
    _registrar_auditoria(
        usuario,
        f'Editó el producto de inventario: {producto.nombre} (Stock: {producto.cantidad})',
        request,
    )
    return producto


@transaction.atomic
def eliminar_producto(*, producto, usuario, request=None):
    producto = ProductoInventario.objects.select_for_update().get(pk=producto.pk)
    if producto.cantidad > 0:
        raise StockActivoError('No se puede eliminar un producto con stock activo')

    nombre = producto.nombre
    producto.delete()
    _registrar_auditoria(usuario, f'Eliminó el producto de inventario: {nombre}', request)
