from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    NIVEL_CHOICES = [
        ('Bronce', 'Bronce'),
        ('Plata', 'Plata'),
        ('Oro', 'Oro'),
    ]

    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    puntos = models.IntegerField(default=0)
    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES, default='Bronce')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class EstrategiaFidelizacion(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    puntos_requeridos = models.IntegerField()
    descuento = models.DecimalField(max_digits=5, decimal_places=2)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    TIPO_CHOICES = [
        ('Sitio', 'En el sitio'),
        ('Domicilio', 'A domicilio'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    puntos_generados = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # 1 punto por cada 10 unidades monetarias
        self.puntos_generados = int(self.total // 10)

        super().save(*args, **kwargs)

        # sumar puntos al cliente
        self.cliente.puntos += self.puntos_generados
        self.cliente.save()

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente.nombre}"