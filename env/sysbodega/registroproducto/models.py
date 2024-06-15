from django.db import models

from django.db import models
from django.db import connection
from django.db.backends.utils import truncate_name

# UBICACIÓN
class Ubicacion(models.Model):
    id_ubicacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=100)

    class Meta:
        db_table = "Ubicacion"
        verbose_name = "Ubicacion"

# CATEGORÍA
class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=100)

    class Meta:
        db_table = "Categoria"
        verbose_name = "Categoria"

# HISTORIAL
class Historial(models.Model):
    id_historial = models.AutoField(primary_key=True)
    sku = models.CharField(max_length=20)
    movimiento = models.CharField(max_length=20)
    ingreso = models.DateField()
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    categoria_nombre = models.CharField(max_length=30)
    ubicacion_nombre = models.CharField(max_length=30)

    class Meta:
        db_table = "Historial"
        verbose_name = "Historial"

# PRODUCTO
class Producto(models.Model):
    sku = models.CharField(max_length=20, primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField()
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE) # FK Categoria
    id_ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE) # FK Ubicacion

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "Producto"
        verbose_name = "Producto"