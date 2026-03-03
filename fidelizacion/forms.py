from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Pedido


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nombre = forms.CharField(max_length=150)
    telefono = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['tipo', 'total']


class PedidoLocalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].required = False
        self.fields["cliente"].empty_label = "Sin cliente asociado"

    class Meta:
        model = Pedido
        fields = ["mesa", "cliente", "metodo_pago", "observaciones"]


class PedidoDomicilioForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            "nombre_cliente",
            "telefono_contacto",
            "direccion_entrega",
            "metodo_pago",
            "observaciones",
        ]
