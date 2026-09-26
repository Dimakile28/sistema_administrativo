from django.core.validators import MinValueValidator
from django.db import models

from apps.usuarios.models import Sede


class Categoria(models.Model):
	nombre = models.CharField(max_length=50, unique=True)

	class Meta:
		ordering = ['nombre']
		verbose_name = 'categoría'
		verbose_name_plural = 'categorías'

	def __str__(self):
		return self.nombre


class ProductoInventario(models.Model):
	nombre = models.CharField(max_length=150)
	categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
	cantidad = models.PositiveIntegerField(default=0)
	precio = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		validators=[MinValueValidator(0)],
	)
	foto = models.ImageField(upload_to='inventario_fotos/', null=True, blank=True)
	fecha_actualizacion = models.DateTimeField(auto_now=True)
	sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='inventario')

	class Meta:
		ordering = ['nombre', 'id']
		indexes = [
			models.Index(fields=['sede', 'categoria'], name='inventario_sede_cat_idx'),
			models.Index(fields=['fecha_actualizacion'], name='inventario_fecha_idx'),
		]

	def __str__(self):
		return f'{self.nombre} - Sede: {self.sede.nombre}'
