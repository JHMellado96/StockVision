from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from .models import Producto, Categoria, Ubicacion, Historial
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def BuscadorView(request):
    productos = Producto.objects.all()
    categorias = set()
    ubicaciones = set()

    # Obtener categorias para listar
    for cat in productos:
        categoria = cat.id_categoria
        categorias.add(categoria)
    
    # Obtener ubicaciones para listar
    for ubi in productos:
        ubicacion = ubi.id_ubicacion
        ubicaciones.add(ubicacion)

    # Filtrar los registros
    if request.method == 'POST':
        nombre_orden = request.POST.get('id_nombre')
        categoria_seleccionada = request.POST.get('id_categoria')
        ubicacion_seleccionada = request.POST.get('id_ubicacion')
        precio_orden = request.POST.get('id_precio')

        if nombre_orden == 'Ascendente':
            productos = productos.order_by('nombre')
        elif nombre_orden == 'Descendente':
            productos = productos.order_by('-nombre')

        if categoria_seleccionada != 'No Usar':
            productos = productos.filter(id_categoria=categoria_seleccionada)

        if ubicacion_seleccionada != 'No Usar':
            productos = productos.filter(id_ubicacion=ubicacion_seleccionada)

        if precio_orden == 'Ascendente':
            productos = productos.order_by('precio_venta')
        elif precio_orden == 'Descendente':
            productos = productos.order_by('-precio_venta')
            
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(productos, 20)

    try:
        productos_paginados = paginator.page(page)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)

    usr = request.user
    usuario = usr.username
    contexto = {
        'categorias': categorias,
        'ubicaciones': ubicaciones,
        'productos': productos_paginados,
        'usuario': usuario
    }
    
    return render(request, "buscadorsku.html", contexto)


@login_required
def BuscarSKU(request, id_sku):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        producto = Producto.objects.filter(sku=sku).first()
        if producto:
            producto_encontrado = Producto.objects.get(sku=sku)
            usr = request.user
            usuario = usr.username
            contexto = {
            'sku': producto_encontrado.sku,
            'nombre': producto_encontrado.nombre,
            'descripcion': producto_encontrado.descripcion,
            'precio_costo': producto_encontrado.precio_costo,
            'precio_venta': producto_encontrado.precio_venta,
            'cantidad': producto_encontrado.cantidad,
            'categoria': producto_encontrado.id_categoria.nombre,
            'descripcion_cat': producto_encontrado.id_categoria.descripcion,
            'ubicacion': producto_encontrado.id_ubicacion.nombre,
            'descripcion_ub': producto_encontrado.id_ubicacion.descripcion,
            'usuario': usuario}
            return render(request, 'resultadobusqueda.html', contexto)
        else:
            messages.error(request, "Producto no encontrado")
            return redirect('BuscadorView')
    
    if request.method == 'GET':
        producto_encontrado = Producto.objects.get(sku=id_sku)
        usr = request.user
        usuario = usr.username
        contexto = {
            'sku': producto_encontrado.sku,
            'nombre': producto_encontrado.nombre,
            'descripcion': producto_encontrado.descripcion,
            'precio_costo': producto_encontrado.precio_costo,
            'precio_venta': producto_encontrado.precio_venta,
            'cantidad': producto_encontrado.cantidad,
            'categoria': producto_encontrado.id_categoria.nombre,
            'descripcion_cat': producto_encontrado.id_categoria.descripcion,
            'ubicacion': producto_encontrado.id_ubicacion.nombre,
            'descripcion_ub': producto_encontrado.id_ubicacion.descripcion,
            'usuario': usuario}
        return render(request, 'resultadobusqueda.html', contexto)
    return render(request, 'buscadorsku.html', {'mensaje': " "})


@login_required
def ResultadosSKU(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        producto = Producto.objects.filter(sku=sku).first()
        categorias = Categoria.objects.all()
        ubicaciones = Ubicacion.objects.all()
        usr = request.user
        usuario = usr.username
        contexto = {
            'sku_ant': producto.sku,
            'nombre_ant': producto.nombre,
            'descripcion_ant': producto.descripcion,
            'precio_costo_ant': producto.precio_costo,
            'precio_venta_ant': producto.precio_venta,
            'cantidad_ant': producto.cantidad,
            'categoria_ant': producto.id_categoria.nombre,
            'categorias': categorias,
            'ubicacion_ant': producto.id_ubicacion.nombre,
            'ubicaciones': ubicaciones,
            'usuario': usuario}
        return render(request, 'modificarresultado.html', contexto)
    else:
        return render(request, 'resultadobusqueda.html')


@login_required
def ModificarSKU(request):
    if request.method == 'POST':
        sku = request.POST.get('sku_ant')
        producto = Producto.objects.get(sku=sku)
        # Obtener datos
        nombre_nv = request.POST.get('nombre')
        descripcion_nv = request.POST.get('descripcion')
        precio_costo_nv = request.POST.get('precio_costo')
        precio_venta_nv = request.POST.get('precio_venta')
        cantidad_nv = request.POST.get('cantidad')
        idcategoria = request.POST.get('categoria_id')
        idubicacion = request.POST.get('ubicacion_id')

        categoria = Categoria.objects.get(id_categoria=idcategoria)
        ubicacion = Ubicacion.objects.get(id_ubicacion=idubicacion)

        # Actualizar tabla
        producto.sku = sku
        producto.nombre = nombre_nv
        producto.descripcion = descripcion_nv
        producto.precio_costo = precio_costo_nv
        producto.precio_venta = precio_venta_nv
        producto.cantidad = cantidad_nv
        producto.id_categoria = categoria
        producto.id_ubicacion = ubicacion
        # Guarda los cambios en la base de datos
        producto.save()

        # Fecha de ingreso
        datetime_modificacion = datetime.now()
        # Categoría y Ubicación usadas
        categoria_usada = Categoria.objects.get(id_categoria=idcategoria)
        ubicacion_usada = Ubicacion.objects.get(id_ubicacion=idubicacion)

        # Registro de Historial
        historial = Historial.objects.create(ingreso=datetime_modificacion,
                                            movimiento='Modificación',
                                            precio_costo=precio_costo_nv,
                                            precio_venta=precio_venta_nv,
                                            stock=cantidad_nv,
                                            categoria_nombre=categoria_usada.nombre,
                                            ubicacion_nombre=ubicacion_usada.nombre,
                                            sku=sku)
        historial.save()

        usr = request.user
        usuario = usr.username
        contexto = {
            'sku': producto.sku,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio_costo': producto.precio_costo,
            'precio_venta': producto.precio_venta,
            'cantidad': producto.cantidad,
            'categoria': producto.id_categoria.nombre,
            'descripcion_cat': producto.id_categoria.descripcion,
            'ubicacion': producto.id_ubicacion.nombre,
            'descripcion_ub': producto.id_ubicacion.descripcion,
            'usuario': usuario}
        
        return render(request, 'resultadobusqueda.html', contexto)
    else:
        return redirect(request, 'modificarresultado.html')


@login_required    
def EliminarSKU(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        # Fecha actual
        datetime_actual = datetime.now()

        # Información de producto
        producto = Producto.objects.filter(sku=sku).first()
        pcosto = producto.precio_costo
        pventa = producto.precio_venta
        stock = producto.cantidad

        #Información de categoría y ubicación
        categoria = Categoria.objects.get(id_categoria=producto.id_categoria_id)
        cnombre = categoria.nombre
        ubicacion = Ubicacion.objects.get(id_ubicacion=producto.id_ubicacion_id)
        unombre = ubicacion.nombre

        # Registro de Historial
        historial = Historial.objects.create(ingreso=datetime_actual,
                                            movimiento='Eliminación',
                                            precio_costo=pcosto,
                                            precio_venta=pventa,
                                            stock=stock,
                                            categoria_nombre=cnombre,
                                            ubicacion_nombre=unombre,
                                            sku=sku)
        historial.save()

        producto.delete()

        messages.error(request, "Producto eliminado correctamente")
        return redirect('BuscadorView')
    else:
        return render('resultadobusqueda')