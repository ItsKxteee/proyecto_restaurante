from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum

from carta.models import Producto

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


class Mesa(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["numero"]

    def __str__(self):
        return f"Mesa {self.numero}"


class EstrategiaFidelizacion(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    puntos_requeridos = models.IntegerField()
    descuento = models.DecimalField(max_digits=5, decimal_places=2)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    TIPO_LOCAL = "LOCAL"
    TIPO_DOMICILIO = "DOMICILIO"
    TIPO_CHOICES = [
        (TIPO_LOCAL, "En el local"),
        (TIPO_DOMICILIO, "A domicilio"),
    ]

    PAGO_CHOICES = [
        ("EFECTIVO", "Efectivo"),
        ("TARJETA", "Tarjeta"),
        ("TRANSFERENCIA", "Transferencia"),
        ("CONTRAENTREGA", "Contraentrega"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos_creados",
    )
    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT, null=True, blank=True)
    nombre_cliente = models.CharField(max_length=150, blank=True)
    telefono_contacto = models.CharField(max_length=20, blank=True)
    direccion_entrega = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    metodo_pago = models.CharField(max_length=20, choices=PAGO_CHOICES, default="EFECTIVO")
    observaciones = models.TextField(blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    puntos_generados = models.IntegerField(default=0)
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ["-fecha"]

    def recalcular_totales(self):
        total = sum(
            (item.precio_unitario * item.cantidad for item in self.items.all()),
            Decimal("0.00"),
        )
        puntos = int(total // Decimal("10"))
        Pedido.objects.filter(pk=self.pk).update(total=total, puntos_generados=puntos)
        self.total = total
        self.puntos_generados = puntos
        self.actualizar_puntos_cliente()

    def actualizar_puntos_cliente(self):
        if not self.cliente_id:
            return
        puntos_cliente = (
            Pedido.objects.filter(cliente_id=self.cliente_id).aggregate(total=Sum("puntos_generados"))["total"]
            or 0
        )
        Cliente.objects.filter(pk=self.cliente_id).update(puntos=puntos_cliente)

    def __str__(self):
        if self.tipo == self.TIPO_LOCAL:
            return f"Pedido local #{self.id}"
        return f"Pedido domicilio #{self.id}"


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        verbose_name = "item de pedido"
        verbose_name_plural = "items de pedido"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.precio_unitario = self.producto.precio
        super().save(*args, **kwargs)
        self.pedido.recalcular_totales()

    def delete(self, *args, **kwargs):
        pedido = self.pedido
        super().delete(*args, **kwargs)
        pedido.recalcular_totales()

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
