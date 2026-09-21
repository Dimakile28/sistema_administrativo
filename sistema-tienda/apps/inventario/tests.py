from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.usuarios.models import RegistroAuditoria, Sede, Usuario

from apps.inventario.models import Categoria, ProductoInventario
from apps.inventario.services import StockActivoError, eliminar_producto


class InventarioBusinessTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.sede = Sede.objects.create(nombre='Sede Centro')
		cls.categoria = Categoria.objects.create(nombre='Bebidas')
		cls.usuario = Usuario.objects.create_user(
			username='cajero',
			password='una-clave-segura',
			rol='CAJERO',
			sede=cls.sede,
		)

	def test_no_permite_eliminar_producto_con_stock(self):
		producto = ProductoInventario.objects.create(
			nombre='Cafe', categoria=self.categoria, cantidad=2,
			precio=Decimal('4.50'), sede=self.sede,
		)

		with self.assertRaises(StockActivoError):
			eliminar_producto(producto=producto, usuario=self.usuario)

		self.assertTrue(ProductoInventario.objects.filter(pk=producto.pk).exists())
		self.assertFalse(RegistroAuditoria.objects.filter(modulo='Inventario').exists())

	def test_elimina_producto_sin_stock_y_audita(self):
		producto = ProductoInventario.objects.create(
			nombre='Cafe', categoria=self.categoria, cantidad=0,
			precio=Decimal('4.50'), sede=self.sede,
		)

		eliminar_producto(producto=producto, usuario=self.usuario)

		self.assertFalse(ProductoInventario.objects.filter(pk=producto.pk).exists())
		self.assertTrue(RegistroAuditoria.objects.filter(
			usuario=self.usuario,
			modulo='Inventario',
			accion__startswith='Eliminó el producto',
		).exists())

	def test_cajero_solo_ve_productos_de_su_sede(self):
		otra_sede = Sede.objects.create(nombre='Sede Norte')
		ProductoInventario.objects.create(
			nombre='Visible', categoria=self.categoria, cantidad=0,
			precio=Decimal('1.00'), sede=self.sede,
		)
		ProductoInventario.objects.create(
			nombre='ProductoOtraSede', categoria=self.categoria, cantidad=0,
			precio=Decimal('1.00'), sede=otra_sede,
		)

		self.client.force_login(self.usuario)
		response = self.client.get(reverse('inventario:lista_productos'))

		self.assertContains(response, 'Visible')
		self.assertNotContains(response, 'ProductoOtraSede')

	def test_admin_crea_categoria_y_regresa_al_producto(self):
		self.client.force_login(self.usuario)
		self.usuario.rol = 'ADMIN'
		self.usuario.save(update_fields=['rol'])

		response = self.client.post(reverse('inventario:crear_categoria'), {
			'nombre': 'Limpieza',
		})

		self.assertRedirects(response, reverse('inventario:crear_producto'))
		self.assertTrue(Categoria.objects.filter(nombre='Limpieza').exists())

	def test_cajero_no_puede_crear_categoria(self):
		self.client.force_login(self.usuario)

		response = self.client.get(reverse('inventario:crear_categoria'))

		self.assertEqual(response.status_code, 403)
