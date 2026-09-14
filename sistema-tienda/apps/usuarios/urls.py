# apps/usuarios/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.dashboard, name='dashboard'),

    # Nuevas rutas del Módulo de Seguridad
    path('seguridad/usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('seguridad/usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('seguridad/usuarios/editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('seguridad/auditoria/', views.lista_auditoria, name='lista_auditoria'),
]