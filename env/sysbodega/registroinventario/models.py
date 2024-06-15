from django.db import models
from registroproducto.models import Producto, Categoria, Ubicacion, Historial

# BODEGA
class Inventario(models.Model):
    sku = models.CharField(max_length=20, primary_key=True)
    cantidad = models.IntegerField()
    estado = models.CharField(max_length=20)

    class Meta:
        db_table = "Inventario"
        verbose_name = "Inventario"