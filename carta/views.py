from django.shortcuts import render
from .models import Producto, Categoria

def ver_carta(request):
    categoria_id = request.GET.get('categoria')
    busqueda = request.GET.get('buscar')

    productos = Producto.objects.filter(disponible=True)

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    categorias = Categoria.objects.filter(activa=True)

    return render(request, 'carta/ver_carta.html', {
        'productos': productos,
        'categorias': categorias
    })