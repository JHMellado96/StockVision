from django.contrib import admin
from .models import Producto, Categoria, Ubicacion, Historial

# Register your models here.
admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(Ubicacion)
admin.site.register(Historial)