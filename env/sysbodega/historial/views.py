from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from .models import Producto, Categoria, Ubicacion, Historial
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def VistaHistorial(request):
    historial = Historial.objects.all()
    meses = set()

    for registro in historial:
        mes = registro.ingreso.strftime("%B, %Y")
        meses.add(mes)

    # Ordenar los meses para que se muestren en orden cronológico
    meses = sorted(meses, key=lambda x: datetime.strptime(x, "%B, %Y"))

    # Filtrar los registros si se selecciona un mes
    if request.method == 'POST':
        mes_seleccionado = request.POST.get('id_mes')
        if mes_seleccionado:
            mes, year = mes_seleccionado.split(", ")
            historial = historial.filter(ingreso__month=datetime.strptime(mes, "%B").month,
                                         ingreso__year=int(year))

    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(historial, 20)
    try:
        historial_paginado = paginator.page(page)
    except PageNotAnInteger:
        historial_paginado = paginator.page(1)
    except EmptyPage:
        historial_paginado = paginator.page(paginator.num_pages)

    usr = request.user
    usuario = usr.username
    contexto = {'historial': historial_paginado,
                'meses': meses,
                'usuario': usuario}
    return render(request, 'movimientos.html', contexto)


@login_required
def VistaMovimiento(request, id_h):
    registro = get_object_or_404(Historial, id_historial=id_h)
    sku = registro.sku
    movimiento = registro.movimiento
    precio_costo = registro.precio_costo
    precio_venta = registro.precio_venta
    stock = registro.stock
    categoria = registro.categoria_nombre
    ubicacion = registro.ubicacion_nombre
    ingreso = registro.ingreso

    usr = request.user
    usuario = usr.username
    contexto = {'sku': sku,
                'movimiento': movimiento,
                'precio_costo': precio_costo,
                'precio_venta': precio_venta,
                'stock': stock,
                'categoria': categoria,
                'ubicacion': ubicacion,
                'ingreso': ingreso,
                'usuario': usuario}
    return render(request, 'registromovimiento.html', contexto)