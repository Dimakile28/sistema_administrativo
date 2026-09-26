from django.urls import path

from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('nuevo/', views.crear_producto_view, name='crear_producto'),
    path('categorias/nueva/', views.crear_categoria_view, name='crear_categoria'),
    path('<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('<int:pk>/eliminar/', views.eliminar_producto_view, name='eliminar_producto'),
]
