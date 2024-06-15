from django.db import models
from registroproducto.models import Producto, Categoria, Ubicacion, Historial
from registroinventario.models import Inventario

# SALIDA
class Salida(models.Model):
    sku = models.CharField(max_length=20, primary_key=True)
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=20)
    stock_sys = models.IntegerField()

    class Meta:
        db_table = "Salida"
        verbose_name = "Salida"

# SALIDA_REG
class SalidaHistorico(models.Model):
    id_salida = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    usuario = models.CharField(max_length=20)
    fecha = models.DateField()

    class Meta:
        db_table = "Salida Historico"
        verbose_name = "Salida Historico"