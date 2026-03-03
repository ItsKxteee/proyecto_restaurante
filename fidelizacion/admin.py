from django.contrib import admin
from .models import Cliente, EstrategiaFidelizacion, Mesa, Pedido, PedidoItem


class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 1


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email', 'puntos')
    search_fields = ('nombre', 'email')


@admin.register(EstrategiaFidelizacion)
class EstrategiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'mesa', 'nombre_cliente', 'cliente', 'fecha', 'total', 'metodo_pago')
    list_filter = ('tipo', 'metodo_pago', 'fecha')
    search_fields = ('id', 'nombre_cliente', 'direccion_entrega')
    inlines = [PedidoItemInline]


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'activa')
    list_filter = ('activa',)
