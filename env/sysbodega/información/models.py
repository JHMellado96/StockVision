from django.db import models

# Empresa
class Empresa(models.Model):
    rut = models.IntegerField(primary_key=True)
    dv = models.CharField(max_length=1)
    nombre = models.CharField(max_length=30)
    direccion = models.CharField(max_length=30)
    modificación = models.DateField()
    inventario = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "Empresa"
        verbose_name = "Empresa"