from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Sede, Usuario

class CustomUserAdmin(UserAdmin):
    model = Usuario
    # Añadir los campos nuevos a la vista de edición del panel
    fieldsets = UserAdmin.fieldsets + (
        ('Asignación de Tienda y Permisos', {'fields': ('rol', 'sede')}),
    )
    # Mostrar las columnas en la lista principal
    list_display = ['username', 'first_name', 'last_name', 'rol', 'sede', 'is_active']

admin.site.register(Sede)
admin.site.register(Usuario, CustomUserAdmin)