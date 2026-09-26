from django.test import TestCase
from django.urls import reverse

from .models import RegistroAuditoria, Usuario


class CrearSedeTests(TestCase):
	def setUp(self):
		self.admin = Usuario.objects.create_user(
			username='admin_sedes',
			password='una-clave-segura',
			rol='ADMIN',
		)
		self.cajero = Usuario.objects.create_user(
			username='cajero_sedes',
			password='una-clave-segura',
			rol='CAJERO',
		)

	def test_admin_puede_crear_sede_y_se_audita(self):
		self.client.force_login(self.admin)
		response = self.client.post(reverse('crear_sede'), {
			'nombre': 'Sede Principal',
			'direccion': 'Calle 1',
			'activa': 'on',
		})

		self.assertRedirects(response, reverse('lista_usuarios'))
		self.assertTrue(self.admin.registroauditoria_set.filter(
			modulo='Usuarios',
			accion='Creó la sede: Sede Principal',
		).exists())

	def test_usuario_no_admin_no_puede_crear_sede(self):
		self.client.force_login(self.cajero)
		response = self.client.get(reverse('crear_sede'))

		self.assertEqual(response.status_code, 403)
