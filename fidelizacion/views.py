from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import Cliente
from .forms import RegistroForm, PedidoForm


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
    cliente = Cliente.objects.get(user=request.user)

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.cliente = cliente
            pedido.save()
            return redirect('inicio')
    else:
        form = PedidoForm()

    return render(request, 'fidelizacion/crear_pedido.html', {'form': form})