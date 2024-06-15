from django.shortcuts import render, redirect
from datetime import datetime
from .models import Ubicacion, Categoria, Producto, Historial
from django.contrib.auth.decorators import login_required


@login_required
def RegView(request):

    # Obtener categorías y ubicaciones para mostrar
    categorias = Categoria.objects.all()
    ubicaciones = Ubicacion.objects.all()
    usr = request.user
    usuario = usr.username
    contexto = {'categorias': categorias,
                'ubicaciones': ubicaciones,
                'usuario': usuario}

    return render(request, "registroproducto.html", contexto)


@login_required
def ProdGuardar(request):
    if request.method == 'POST':

        # Obtener los datos del formulario
        sku = request.POST.get('sku')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio_costo = request.POST.get('precio_costo')
        precio_venta = request.POST.get('precio_venta')
        cantidad = request.POST.get('cantidad')
        # Obtener la fecha actual
        datetime_ingreso = datetime.now()

        # VERIFICACIÓN DE CATEGORÍA
        if 'check-categoria' in request.POST and request.POST.get('nueva_categoria_nombre') and request.POST.get('nueva_categoria_descripcion'):
            nombre_categoria = request.POST.get('nueva_categoria_nombre')
            descripcion_categoria = request.POST.get('nueva_categoria_descripcion')
            # Crear la nueva categoría
            categoria = Categoria.objects.create(nombre=nombre_categoria,
                                                descripcion=descripcion_categoria)
            # Obtener el ID de la nueva categoría creada
            idcategoria = categoria.id_categoria
        else:
            idcategoria = request.POST.get('categoria_id')

        # VERIFICACION DE UBICACIÓN
        if 'check-ubicacion' in request.POST and request.POST.get('nueva_ubicacion_nombre') and request.POST.get('nueva_ubicacion_descripcion'):
            nombre_ubicacion = request.POST.get('nueva_ubicacion_nombre')
            descripcion_ubicacion = request.POST.get('nueva_ubicacion_descripcion')
            # Crear la nueva categoría
            ubicacion = Ubicacion.objects.create(nombre=nombre_ubicacion,
                                                descripcion=descripcion_ubicacion)
            # Obtener el ID de la nueva categoría creada
            idubicacion = ubicacion.id_ubicacion
        else:
            idubicacion = request.POST.get('ubicacion_id')

        try:
            if Producto.objects.get(sku=sku):
                return render(request, 'registroproducto.html', {'mensaje': "PRODUCTO YA EXISTE!"})
        except Producto.DoesNotExist:
            # GUARDAR DATOS EN LA TABLA "PRODUCTOS"
            producto = Producto.objects.create(sku=sku, nombre=nombre,
                descripcion=descripcion, precio_costo=precio_costo,
                precio_venta=precio_venta, cantidad=cantidad,
                id_categoria_id=idcategoria, id_ubicacion_id=idubicacion)
            producto.save()

        # Categoría y Ubicación usadas
        categoria_guardada = Categoria.objects.get(id_categoria=idcategoria)
        ubicacion_guardada = Ubicacion.objects.get(id_ubicacion=idubicacion)

        # GUARDAR DATOS EN LA TABLA "HISTORIAL"
        historial = Historial.objects.create(ingreso=datetime_ingreso,
                                            movimiento='Registro',
                                            precio_costo=precio_costo,
                                            precio_venta=precio_venta,
                                            stock=cantidad,
                                            categoria_nombre=categoria_guardada.nombre,
                                            ubicacion_nombre=ubicacion_guardada.nombre,
                                            sku=sku)
        historial.save()

        # Obtener los datos del producto registrado previamente
        producto_guardado = Producto.objects.get(sku=sku)

        # Obtener la categoría y ubicación del producto
        categoria_producto = producto_guardado.id_categoria.nombre
        ubicacion_producto = producto_guardado.id_ubicacion.nombre

        # Renderizar el HTML de guardado exitoso con los datos del producto
        usr = request.user
        usuario = usr.username
        contexto = {
            'sku': producto_guardado.sku,
            'nombre': producto_guardado.nombre,
            'descripcion': producto_guardado.descripcion,
            'precio_costo': producto_guardado.precio_costo,
            'precio_venta': producto_guardado.precio_venta,
            'cantidad': producto_guardado.cantidad,
            'categoria': categoria_producto,
            'ubicacion': ubicacion_producto,
            'ingreso': datetime_ingreso,
            'usuario': usuario}

        # Redirigir a una página de éxito o renderizar una plantilla de éxito
        return render(request, 'guardar_producto.html', contexto)
    else:
        # Si la solicitud no es POST, redirigir a la página de registro de producto
        return redirect('registroproducto.html')
    

@login_required
def CategoriasYUbicaciones(request):
    categorias = Categoria.objects.all()
    ubicaciones = Ubicacion.objects.all()
    usr = request.user
    usuario = usr.username
    contexto = {'categorias': categorias,
                 'ubicaciones': ubicaciones,
                 'usuario': usuario}
    return render(request, 'categoriasyubicaciones.html', contexto)


@login_required
def RegistrarCategoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombrecat')
        descripcion = request.POST.get('descripcioncat')
        categoria = Categoria.objects.create(nombre=nombre, descripcion=descripcion)
        categoria.save()

    categorias = Categoria.objects.all()
    ubicaciones = Ubicacion.objects.all()
    usr = request.user
    usuario = usr.username
    contexto = {'categorias': categorias,
                 'ubicaciones': ubicaciones,
                 'usuario': usuario}
    return render(request, 'categoriasyubicaciones.html', contexto)


@login_required
def ModificarCategoria(request):
    if request.method == 'GET':
        id = request.GET.get('idcat')
        nombre = request.GET.get('nombrecat')
        descripcion = request.GET.get('descripcioncat')
        mensaje = request.GET.get('mensaje')
        usr = request.user
        usuario = usr.username
        contexto = {'id': id,
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'mensaje': mensaje,
                    'usuario': usuario}
        return render(request, 'modificarcatoubi.html', contexto)
    
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        categoria = Categoria.objects.get(id_categoria=id)
        categoria.nombre = nombre
        categoria.descripcion = descripcion
        categoria.save()

    categorias = Categoria.objects.all()
    ubicaciones = Ubicacion.objects.all()
    usr = request.user
    usuario = usr.username
    contexto = {'categorias': categorias,
                 'ubicaciones': ubicaciones,
                 'usuario': usuario}
    return render(request, 'categoriasyubicaciones.html', contexto)


@login_required
def RegistrarUbicacion(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombreubi')
        descripcion = request.POST.get('descripcionubi')
        ubicacion = Ubicacion.objects.create(nombre=nombre, descripcion=descripcion)
        ubicacion.save()

    categorias = Categoria.objects.all()
    ubicaciones = Ubicacion.objects.all()
    usr = request.user
    usuario = usr.username
    contexto = {'categorias': categorias,
                 'ubicaciones': ubicaciones,
                 'usuario': usuario}
    return render(request, 'categoriasyubicaciones.html', contexto)


@login_required
def ModificarUbicacion(request):
    if request.method == 'GET':
        id = request.GET.get('idubi')
        nombre = request.GET.get('nombreubi')
        descripcion = request.GET.get('descripcionubi')
        mensaje = request.GET.get('mensaje')
        usr = request.user
        usuario = usr.username
        contexto = {'id': id,
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'mensaje': mensaje,
                    'usuario': usuario}
        return render(request, 'modificarcatoubi.html', contexto)
    
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        ubicacion = Ubicacion.objects.get(id_ubicacion=id)
        ubicacion.nombre = nombre
        ubicacion.descripcion = descripcion
        ubicacion.save()

    categorias = Categoria.objects.all()
    ubicaciones = Ubicacion.objects.all()
    usr = request.user
    usuario = usr.username
    contexto = {'categorias': categorias,
                 'ubicaciones': ubicaciones,
                 'usuario': usuario}
    return render(request, 'categoriasyubicaciones.html', contexto)