from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from apps.usuarios.models import Sede

from .forms import CategoriaForm, ProductoInventarioForm
from .models import Categoria, ProductoInventario
from .services import StockActivoError, actualizar_producto, crear_producto, eliminar_producto


def _es_admin(usuario):
	return usuario.rol == 'ADMIN'


def _sedes_disponibles(usuario):
	if _es_admin(usuario):
		return Sede.objects.filter(activa=True).order_by('nombre')
	if usuario.sede_id:
		return Sede.objects.filter(pk=usuario.sede_id, activa=True)
	return Sede.objects.none()


def _productos_visibles(usuario):
	productos = ProductoInventario.objects.select_related('categoria', 'sede')
	if not _es_admin(usuario):
		productos = productos.filter(sede_id=usuario.sede_id) if usuario.sede_id else productos.none()
	return productos


def _fecha_valida(valor):
	if not valor:
		return None
	try:
		return datetime.strptime(valor, '%Y-%m-%d').date()
	except ValueError:
		return None


@login_required
def lista_productos(request):
	productos = _productos_visibles(request.user)
	categorias = Categoria.objects.order_by('nombre')
	sedes = _sedes_disponibles(request.user)

	categoria_id = request.GET.get('categoria', '')
	sede_id = request.GET.get('sede', '')
	fecha_inicio_texto = request.GET.get('fecha_inicio', '')
	fecha_fin_texto = request.GET.get('fecha_fin', '')
	fecha_inicio = _fecha_valida(fecha_inicio_texto)
	fecha_fin = _fecha_valida(fecha_fin_texto)

	if categoria_id.isdigit():
		productos = productos.filter(categoria_id=categoria_id)
	if _es_admin(request.user) and sede_id.isdigit():
		productos = productos.filter(sede_id=sede_id)
	if fecha_inicio:
		productos = productos.filter(fecha_actualizacion__date__gte=fecha_inicio)
	if fecha_fin:
		productos = productos.filter(fecha_actualizacion__date__lte=fecha_fin)

	contexto = {
		'productos': productos,
		'categorias': categorias,
		'sedes': sedes,
		'filtros': {
			'categoria': categoria_id,
			'sede': sede_id,
			'fecha_inicio': fecha_inicio_texto,
			'fecha_fin': fecha_fin_texto,
		},
	}
	return render(request, 'inventario/lista_productos.html', contexto)


@login_required
def crear_producto_view(request):
	sedes = _sedes_disponibles(request.user)
	if not sedes.exists():
		messages.warning(
			request,
			'No puedes crear productos todavía: primero debes crear y activar una sede desde el panel de administración.',
		)
		return redirect('inventario:lista_productos')

	if request.method == 'POST':
		form = ProductoInventarioForm(request.POST, request.FILES, sedes=sedes)
		if form.is_valid():
			crear_producto(datos=form.cleaned_data, usuario=request.user, request=request)
			messages.success(request, 'Producto creado correctamente.')
			return redirect('inventario:lista_productos')
	else:
		initial = {'sede': request.user.sede_id} if not _es_admin(request.user) else None
		form = ProductoInventarioForm(initial=initial, sedes=sedes)

	return render(request, 'inventario/form_producto.html', {
		'form': form,
		'titulo': 'Nuevo producto',
		'accion': 'Crear producto',
	})


@login_required
def crear_categoria_view(request):
	if request.user.rol != 'ADMIN':
		raise PermissionDenied('Solo un administrador puede crear categorías.')

	if request.method == 'POST':
		form = CategoriaForm(request.POST)
		if form.is_valid():
			categoria = form.save()
			messages.success(request, f'Categoría "{categoria.nombre}" creada correctamente.')
			return redirect('inventario:crear_producto')
	else:
		form = CategoriaForm()

	return render(request, 'inventario/form_categoria.html', {'form': form})


@login_required
def editar_producto(request, pk):
	producto = get_object_or_404(_productos_visibles(request.user), pk=pk)
	sedes = _sedes_disponibles(request.user)

	if request.method == 'POST':
		form = ProductoInventarioForm(request.POST, request.FILES, instance=producto, sedes=sedes)
		if form.is_valid():
			actualizar_producto(producto=producto, datos=form.cleaned_data, usuario=request.user, request=request)
			messages.success(request, 'Producto actualizado correctamente.')
			return redirect('inventario:lista_productos')
	else:
		form = ProductoInventarioForm(instance=producto, sedes=sedes)

	return render(request, 'inventario/form_producto.html', {
		'form': form,
		'producto': producto,
		'titulo': 'Editar producto',
		'accion': 'Guardar cambios',
	})


@login_required
def eliminar_producto_view(request, pk):
	producto = get_object_or_404(_productos_visibles(request.user), pk=pk)
	if request.method != 'POST':
		return render(request, 'inventario/confirmar_eliminacion.html', {'producto': producto})

	try:
		eliminar_producto(producto=producto, usuario=request.user, request=request)
	except StockActivoError as error:
		messages.error(request, str(error))
		return redirect('inventario:lista_productos')

	messages.success(request, 'Producto eliminado correctamente.')
	return redirect('inventario:lista_productos')
