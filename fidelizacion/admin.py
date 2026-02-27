from django.contrib import admin
from .models import Cliente, EstrategiaFidelizacion, Pedido


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email', 'puntos')
    search_fields = ('nombre', 'email')


@admin.register(EstrategiaFidelizacion)
class EstrategiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'total')
    list_filter = ('fecha',)