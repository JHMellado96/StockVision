from django.db import models
from registroproducto.models import Producto, Categoria, Ubicacion, Historial
from registroinventario.models import Inventario

# INGRESO
class Ingreso(models.Model):
    sku = models.CharField(max_length=20, primary_key=True)
    cantidad = models.IntegerField()
    stock_sys = models.IntegerField()

    class Meta:
        db_table = "Ingreso"
        verbose_name = "Ingreso"

# INGRESO_REG
class IngresoHistorico(models.Model):
    id_ingreso = models.AutoField(primary_key=True)
    boleta = models.CharField(max_length=30)
    cantidad = models.IntegerField()
    usuario = models.CharField(max_length=20)
    fecha = models.DateField()

    class Meta:
        db_table = "Ingreso Historico"
        verbose_name = "Ingreso Historico"