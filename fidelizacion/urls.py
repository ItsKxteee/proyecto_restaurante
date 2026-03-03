from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('pedido/', views.crear_pedido, name='crear_pedido'),
    path('pedidos/local/', views.pedidos_local_lista, name='pedidos_local_lista'),
    path('pedidos/local/nuevo/', views.pedido_local_crear, name='pedido_local_crear'),
    path('pedidos/local/<int:pedido_id>/editar/', views.pedido_local_editar, name='pedido_local_editar'),
    path('pedidos/local/<int:pedido_id>/eliminar/', views.pedido_local_eliminar, name='pedido_local_eliminar'),
    path('pedidos/domicilio/nuevo/', views.pedido_domicilio_crear, name='pedido_domicilio_crear'),
    path('pedidos/domicilio/exito/<int:pedido_id>/', views.pedido_domicilio_exito, name='pedido_domicilio_exito'),
]
