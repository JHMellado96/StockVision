from django.shortcuts import render, redirect
from datetime import datetime
from .models import Producto, Categoria, Ubicacion, Historial, Ingreso, IngresoHistorico
from django.contrib.auth.decorators import login_required


@login_required
def IngresoProd(request):
    # Obtener registros para mostrar
    ingresos = Ingreso.objects.all()
    usr = request.user
    usuario = usr.username
    contexto = {'ingresos': ingresos,
                'usuario': usuario}
    return render(request, "ingreso.html", contexto)
    

@login_required
def RegistrarIngreso(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        stock = request.POST.get('stock')
        if sku and stock:
            stock = int(stock)
            # Calcular stock de sistema
            try:
                producto = Producto.objects.get(sku=sku)
                stock_sys = producto.cantidad
            except Producto.DoesNotExist:
                stock_sys = 0
            # Ingresar datos a Ingreso
            try:
                ingreso = Ingreso.objects.get(sku=sku)
                ingreso.cantidad += stock
                ingreso.save()
            except Ingreso.DoesNotExist:
                Ingreso.objects.create(sku=sku, cantidad=stock, stock_sys=stock_sys)

        return redirect('IngresoProd')
    return render(request, "ingreso.html")


@login_required
def AceptarIngreso(request):
    if request.method == 'POST':

        boleta = request.POST.get('boleta')
        ingresos = Ingreso.objects.all()
        actualizaciones = 0
        creaciones = 0
        omisiones = 0
        total = 0
        datetime_ingreso = datetime.now()

        for ing in ingresos:
            try:
                if ing.cantidad > 0:
                    producto = Producto.objects.get(sku=ing.sku)
                    producto.cantidad += ing.cantidad
                    producto.save()
                    historial = Historial.objects.create(ingreso=datetime_ingreso, movimiento='Ingreso',
                        precio_costo=producto.precio_costo, precio_venta=producto.precio_venta,
                        stock=ing.cantidad, categoria_nombre=producto.id_categoria.nombre,
                        ubicacion_nombre=producto.id_ubicacion.nombre, sku=producto.sku)
                    historial.save()
                    actualizaciones += 1
                    total += ing.cantidad
                else:
                    omisiones += 1
            except Producto.DoesNotExist:
                if ing.cantidad > 0:
                    producto = Producto.objects.create(sku=ing.sku, nombre='PENDIENTE',
                        descripcion='PENDIENTE', precio_costo=0, precio_venta=0,
                        cantidad=ing.cantidad, id_categoria_id=1, id_ubicacion_id=1)
                    producto.save()
                    historial = Historial.objects.create(ingreso=datetime_ingreso,
                        movimiento='Registro Incompleto', precio_costo=0, precio_venta=0,
                        stock=ing.cantidad, categoria_nombre=producto.id_categoria.nombre,
                        ubicacion_nombre=producto.id_ubicacion.nombre, sku=producto.sku)
                    historial.save()
                    creaciones += 1
                    total += ing.cantidad
                else:
                    omisiones += 1
        usr = request.user
        usuario = usr.username
        ing_hist = IngresoHistorico.objects.create(boleta=boleta,
            cantidad=total, usuario=usuario, fecha=datetime_ingreso)
        ing_hist.save()

        contexto = {'actualizaciones': actualizaciones,
                    'creaciones': creaciones,
                    'omisiones': omisiones,
                    'usuario': usuario}
        Ingreso.objects.all().delete()
        return render(request, "resumen.html", contexto)
    return render(request, "ingreso.html")


@login_required
def LimpiarRegistros(request):
    Ingreso.objects.all().delete()
    return redirect('IngresoProd')