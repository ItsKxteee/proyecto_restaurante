from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from carta.models import Categoria, Producto

from .forms import (
    PedidoDomicilioForm,
    PedidoLocalForm,
    RegistroForm,
)
from .models import Cliente, Pedido, PedidoItem


def inicio(request):
    return render(request, 'fidelizacion/inicio.html')


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()

            Cliente.objects.create(
                user=user,
                nombre=form.cleaned_data['nombre'],
                email=form.cleaned_data['email'],
                telefono=form.cleaned_data['telefono'],
            )

            login(request, user)
            return redirect('crear_pedido')
    else:
        form = RegistroForm()

    return render(request, 'fidelizacion/registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('crear_pedido')
    else:
        form = AuthenticationForm()

    return render(request, 'fidelizacion/login.html', {'form': form})


@login_required
def crear_pedido(request):
    return redirect("pedido_domicilio_crear")


def es_mesero_o_admin(user):
    return user.is_staff or user.is_superuser or user.groups.filter(name="Meseros").exists()


mesero_admin_required = user_passes_test(es_mesero_o_admin)


def _productos_filtrados(request):
    categoria_id = request.GET.get("categoria")
    busqueda = request.GET.get("buscar", "").strip()

    productos = Producto.objects.filter(disponible=True).select_related("categoria")
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    categorias = Categoria.objects.filter(activa=True)
    return productos, categorias


def _cantidades_desde_post(request):
    seleccion = {}
    for key, value in request.POST.items():
        if not key.startswith("cantidad_"):
            continue
        try:
            producto_id = int(key.replace("cantidad_", ""))
            cantidad = int(value or 0)
        except (TypeError, ValueError):
            continue
        if cantidad > 0:
            seleccion[producto_id] = cantidad
    return seleccion


def _guardar_items_pedido(pedido, cantidades_por_producto):
    pedido.items.all().delete()
    productos = Producto.objects.filter(id__in=cantidades_por_producto.keys(), disponible=True)
    nuevos_items = []
    for producto in productos:
        nuevos_items.append(
            PedidoItem(
                pedido=pedido,
                producto=producto,
                cantidad=cantidades_por_producto[producto.id],
                precio_unitario=producto.precio,
            )
        )
    if nuevos_items:
        PedidoItem.objects.bulk_create(nuevos_items)
    pedido.recalcular_totales()


def _cantidades_para_template(request, pedido=None):
    if request.method == "POST":
        return {str(k): v for k, v in _cantidades_desde_post(request).items()}
    if pedido:
        return {str(item.producto_id): item.cantidad for item in pedido.items.all()}
    return {}


@login_required
@mesero_admin_required
def pedidos_local_lista(request):
    pedidos = (
        Pedido.objects.filter(tipo=Pedido.TIPO_LOCAL)
        .select_related("mesa", "cliente", "creado_por")
        .prefetch_related("items__producto")
    )
    return render(request, "fidelizacion/pedidos_local_lista.html", {"pedidos": pedidos})


@login_required
@mesero_admin_required
def pedido_local_crear(request):
    productos, categorias = _productos_filtrados(request)
    if request.method == "POST":
        form = PedidoLocalForm(request.POST)
        cantidades = _cantidades_desde_post(request)
        if form.is_valid() and cantidades:
            pedido = form.save(commit=False)
            pedido.tipo = Pedido.TIPO_LOCAL
            pedido.creado_por = request.user
            pedido.nombre_cliente = pedido.nombre_cliente or (pedido.cliente.nombre if pedido.cliente else "")
            pedido.save()
            _guardar_items_pedido(pedido, cantidades)
            return redirect("pedidos_local_lista")
        if not cantidades:
            form.add_error(None, "Debes seleccionar al menos un producto con cantidad mayor a cero.")
    else:
        form = PedidoLocalForm()

    return render(
        request,
        "fidelizacion/pedido_local_form.html",
        {
            "form": form,
            "modo": "crear",
            "productos": productos,
            "categorias": categorias,
            "cantidades": _cantidades_para_template(request),
        },
    )


@login_required
@mesero_admin_required
def pedido_local_editar(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, tipo=Pedido.TIPO_LOCAL)
    productos, categorias = _productos_filtrados(request)
    if request.method == "POST":
        form = PedidoLocalForm(request.POST, instance=pedido)
        cantidades = _cantidades_desde_post(request)
        if form.is_valid() and cantidades:
            pedido = form.save(commit=False)
            pedido.tipo = Pedido.TIPO_LOCAL
            pedido.creado_por = pedido.creado_por or request.user
            pedido.save()
            _guardar_items_pedido(pedido, cantidades)
            return redirect("pedidos_local_lista")
        if not cantidades:
            form.add_error(None, "Debes seleccionar al menos un producto con cantidad mayor a cero.")
    else:
        form = PedidoLocalForm(instance=pedido)

    return render(
        request,
        "fidelizacion/pedido_local_form.html",
        {
            "form": form,
            "modo": "editar",
            "pedido": pedido,
            "productos": productos,
            "categorias": categorias,
            "cantidades": _cantidades_para_template(request, pedido),
        },
    )


@login_required
@mesero_admin_required
def pedido_local_eliminar(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, tipo=Pedido.TIPO_LOCAL)
    if request.method == "POST":
        pedido.delete()
        return redirect("pedidos_local_lista")
    return render(request, "fidelizacion/pedido_local_eliminar.html", {"pedido": pedido})


def pedido_domicilio_crear(request):
    productos, categorias = _productos_filtrados(request)
    if request.method == "POST":
        form = PedidoDomicilioForm(request.POST)
        cantidades = _cantidades_desde_post(request)
        if form.is_valid() and cantidades:
            pedido = form.save(commit=False)
            pedido.tipo = Pedido.TIPO_DOMICILIO
            pedido.mesa = None
            if request.user.is_authenticated:
                cliente = Cliente.objects.filter(user=request.user).first()
                if cliente:
                    pedido.cliente = cliente
                    if not pedido.nombre_cliente:
                        pedido.nombre_cliente = cliente.nombre
                    if not pedido.telefono_contacto:
                        pedido.telefono_contacto = cliente.telefono
            pedido.save()
            _guardar_items_pedido(pedido, cantidades)
            return redirect("pedido_domicilio_exito", pedido_id=pedido.id)
        if not cantidades:
            form.add_error(None, "Debes seleccionar al menos un producto con cantidad mayor a cero.")
    else:
        initial = {}
        if request.user.is_authenticated:
            cliente = Cliente.objects.filter(user=request.user).first()
            if cliente:
                initial = {
                    "nombre_cliente": cliente.nombre,
                    "telefono_contacto": cliente.telefono,
                }
        form = PedidoDomicilioForm(initial=initial)

    return render(
        request,
        "fidelizacion/pedido_domicilio_form.html",
        {
            "form": form,
            "productos": productos,
            "categorias": categorias,
            "cantidades": _cantidades_para_template(request),
        },
    )


def pedido_domicilio_exito(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, tipo=Pedido.TIPO_DOMICILIO)
    return render(request, "fidelizacion/pedido_domicilio_exito.html", {"pedido": pedido})
