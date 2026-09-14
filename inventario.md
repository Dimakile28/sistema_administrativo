# Especificaciones Técnicas: Módulo de Inventario (POS Django)

Esta es la guía de requerimientos, estructura de base de datos y reglas de negocio para el desarrollo del **Módulo de Inventario** de nuestro sistema POS.

## 1. Estructura de la Aplicación
El módulo debe desarrollarse dentro de la carpeta `apps/` como una aplicación independiente de Django:
```bash
python manage.py startapp inventario

```

*No olvides registrar `'apps.inventario',` en el archivo `core/settings.py` dentro de `INSTALLED_APPS`.*

---

## 2. Modelos de Base de Datos (`apps/inventario/models.py`)

Las tablas deben construirse en PostgreSQL vinculando los productos a las sedes existentes (`apps.usuarios.models.Sede`) y respetando los campos especificados en el planteamiento inicial:

```python
from django.db import models
from apps.usuarios.models import Sede

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class ProductoInventario(models.Model):
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Requiere instalar Pillow: pip install Pillow
    foto = models.ImageField(upload_to='inventario_fotos/', null=True, blank=True)
    
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='inventario')

    def __str__(self):
        return f"{self.nombre} - Sede: {self.sede.nombre}"

```

---

## 3. Reglas de Negocio Obligatorias

1. **Restricción de Eliminación:**
* En la vista encargada de eliminar un producto, se debe validar estrictamente que el stock sea cero. Si `cantidad > 0`, el sistema debe denegar la acción y mostrar un mensaje de error (*"No se puede eliminar un producto con stock activo"*).


2. **Integración con Auditoría:**
* Cada vez que un usuario cree, edite o elimine un producto/insumo, se debe registrar automáticamente una acción en la tabla de auditoría global del sistema para mantener la trazabilidad de seguridad:


```python
from apps.usuarios.models import RegistroAuditoria

# Ejemplo al crear un producto:
RegistroAuditoria.objects.create(
    usuario=request.user,
    accion=f"Creó el producto de inventario: {producto.nombre} (Stock: {producto.cantidad})",
    modulo="Inventario"
)

```


3. **Filtros de Búsqueda:**
* La interfaz de inventario debe incluir filtros cruzados obligatorios para optimizar las consultas:
* Filtrar por **Categoría**.
* Filtrar por **Rango de fechas de actualización**.
* Filtrar por **Sede**.





---

## 4. Lineamientos de UI / UX (Diseño)

Para mantener la uniformidad visual en todo el sistema desarrollado hasta ahora:

* **Tipografía:** Utilizar **Roboto** (importada desde Google Fonts).
* **Paleta de Colores:**
* Fondo principal: `#E8E9F3`
* Elementos oscuros / Barras: `#272635`
* Bordes y grises: `#CECECE` / `#A6A6A8`
* Acentos visuales: `#B1E5F2`


* **Iconografía:** Utilizar exclusivamente íconos de **FontAwesome** (evitar el uso de emojis).
* **Responsividad:** Todas las tablas y formularios deben ser adaptables mediante `overflow-x: auto` y CSS Grid/Flexbox para garantizar su correcta visualización en computadoras y tablets.

```

```