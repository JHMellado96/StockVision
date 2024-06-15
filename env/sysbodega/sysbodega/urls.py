from django.contrib import admin
from django.urls import path, include

from registroproducto.views import RegView, ProdGuardar, CategoriasYUbicaciones, RegistrarCategoria, ModificarCategoria, RegistrarUbicacion, ModificarUbicacion
from buscadorsku.views import BuscarSKU, ResultadosSKU, ModificarSKU, EliminarSKU, BuscadorView
from registroinventario.views import RegistrarInventario, GuardarInventario, InventView, LimpiarInventario, ResumenInventario, FinalizarInventario
from historial.views import VistaHistorial, VistaMovimiento
from ingreso.views import IngresoProd, RegistrarIngreso, AceptarIngreso, LimpiarRegistros
from salida.views import SalidaProd, RegistrarSalida, AceptarSalida, LimpiarSalidas
from home.views import home, register, RegInicial, EliminarUsuario
from información.views import InfoCuenta, InfoEmpresa
from informes.views import ProductosTotales, GananciasEInversion, PerdidasMensuales, MovimientosMensuales, IngresosYSalidas, Informes

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', register, name='register'),
    path('', home, name='home'),
    path('registroinicial/', RegInicial, name='RegInicial'),
    path('registro/', EliminarUsuario, name='EliminarUsuario'),

    path('informacioncuenta/', InfoCuenta, name='InfoCuenta'),
    path('informacionempresa/', InfoEmpresa, name='InfoEmpresa'),

    path('registroproducto/', RegView, name='RegView'),
    path('guardar_producto/', ProdGuardar, name='ProdGuardar'),
    path('categoriasyubicaciones/', CategoriasYUbicaciones, name='CategoriasYUbicaciones'),
    path('registrodecategoria/', RegistrarCategoria, name='RegistrarCategoria'),
    path('modificaciondecategoria/', ModificarCategoria, name='ModificarCategoria'),
    path('registrodeubicacion/', RegistrarUbicacion, name='RegistrarUbicacion'),
    path('modificaciondeubicacion/', ModificarUbicacion, name='ModificarUbicacion'),

    path('buscadorsku/', BuscadorView, name='BuscadorView'),
    path('buscadorsku/<int:id_sku>', BuscarSKU, name='BuscarSKU'),
    path('resultadobusqueda/', ResultadosSKU, name='ResultadosSKU'),
    path('modificarresultado/', ModificarSKU, name='ModificarSKU'),
    path('productoeliminado/', EliminarSKU, name='EliminarSKU'),
    
    path('registroinventario/', RegistrarInventario, name='RegistrarInventario'),
    path('resumeninventario/', ResumenInventario, name='ResumenInventario'),
    path('guardarinventario/', GuardarInventario, name='GuardarInventario'),
    path('inventariofinalizado', FinalizarInventario, name='FinalizarInventario'),
    path('registroinventario/', InventView, name='InventView'),
    path('inventariolimpio/', LimpiarInventario, name='LimpiarInventario'),

    path('movimientos/', VistaHistorial, name='VistaHistorial'),
    path('registromovimiento/<int:id_h>/', VistaMovimiento, name='VistaMovimiento'),

    path('ingreso/', IngresoProd, name='IngresoProd'),
    path('registraringreso/', RegistrarIngreso, name='RegistrarIngreso'),
    path('ingresosrealizados/', AceptarIngreso, name='AceptarIngreso'),
    path('ingresoslimpios/', LimpiarRegistros, name='LimpiarRegistros'),

    path('salida/', SalidaProd, name='SalidaProd'),
    path('registrarsalida/', RegistrarSalida, name='RegistrarSalida'),
    path('salidasrealizados/', AceptarSalida, name='AceptarSalida'),
    path('salidaslimpios/', LimpiarSalidas, name='LimpiarSalidas'),

    path('productostotales/', ProductosTotales, name='ProductosTotales'),
    path('gananciaseinversion/', GananciasEInversion, name='GananciasEInversion'),
    path('perdidasmensuales/', PerdidasMensuales, name='PerdidasMensuales'),
    path('movimientosmensuales/', MovimientosMensuales, name='MovimientosMensuales'),
    path('ingresosysalidas/', IngresosYSalidas, name='IngresosYSalidas'),
    path('informes/', Informes, name='Informes'),
]
