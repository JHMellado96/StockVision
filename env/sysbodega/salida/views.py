from django.shortcuts import render, redirect
from datetime import datetime
from .models import Producto, Categoria, Ubicacion, Historial, Salida, SalidaHistorico
from django.contrib.auth.decorators import login_required


@login_required
def SalidaProd(request):
    # Obtener registros para mostrar
    salidas = Salida.objects.all()
    usr = request.user
    usuario = usr.username
    contexto = {'salidas': salidas,
                'usuario': usuario}
    return render(request, "salida.html", contexto)
    

@login_required
def RegistrarSalida(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        stock = request.POST.get('stock')
        motivo = request.POST.get('motivo_id')
        if sku and stock:
            stock = int(stock)
            # Calcular stock de sistema
            try:
                producto = Producto.objects.get(sku=sku)
                stock_sys = producto.cantidad
            except Producto.DoesNotExist:
                stock_sys = 0
                # Ingresar datos a Salida
            try:
                salida = Salida.objects.get(sku=sku)
                salida.cantidad += stock
                salida.motivo = motivo
                salida.save()
            except Salida.DoesNotExist:
                Salida.objects.create(sku=sku, cantidad=stock, motivo=motivo, stock_sys=stock_sys)
        return redirect('SalidaProd')
    return render(request, "salida.html")


@login_required
def AceptarSalida(request):
    salidas = Salida.objects.all()
    correcto = 0
    incorrecto = 0
    vacio = 0
    omisiones = 0
    total = 0
    datetime_salida = datetime.now()

    for sal in salidas:
        try:
            if sal.cantidad > 0:
                producto = Producto.objects.get(sku=sal.sku)
                producto.cantidad -= sal.cantidad
                if producto.cantidad < 1:
                    vacio += 1
                    producto.cantidad = 0
                producto.save()

                historial = Historial.objects.create(ingreso=datetime_salida, movimiento=sal.motivo,
                    precio_costo=producto.precio_costo, precio_venta=producto.precio_venta,
                    stock=sal.cantidad, categoria_nombre=producto.id_categoria.nombre,
                    ubicacion_nombre=producto.id_ubicacion.nombre, sku=producto.sku)
                historial.save()
                correcto += 1
                total += sal.cantidad
            else:
                omisiones += 1
        except Producto.DoesNotExist:
            if sal.cantidad > 0:
                incorrecto += 1
            else:
                omisiones += 1

    usr = request.user
    usuario = usr.username
    sal_hist = SalidaHistorico.objects.create(cantidad=total,
        usuario=usuario, fecha=datetime_salida)
    sal_hist.save()

    contexto = {'correcto': correcto,
                'incorrecto': incorrecto,
                'omisiones': omisiones,
                'vacio': vacio,
                'usuario': usuario}
    Salida.objects.all().delete()
    return render(request, "resumensalida.html", contexto)


@login_required
def LimpiarSalidas(request):
    Salida.objects.all().delete()
    return redirect('SalidaProd')