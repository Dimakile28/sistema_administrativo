from django.contrib import admin

from .models import Categoria, ProductoInventario


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
	search_fields = ['nombre']


@admin.register(ProductoInventario)
class ProductoInventarioAdmin(admin.ModelAdmin):
	list_display = ['nombre', 'categoria', 'sede', 'cantidad', 'precio', 'fecha_actualizacion']
	list_filter = ['categoria', 'sede']
	search_fields = ['nombre']
from django.contrib import admin

# Register your models here.
