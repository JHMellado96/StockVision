from django.shortcuts import render, redirect
from datetime import datetime
from .models import Producto, Categoria, Ubicacion, Historial, Inventario
from información.models import Empresa
from django.contrib.auth.models import User

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required


@login_required
def InventView(request):
    # Obtener registros para mostrar
    inventario = Inventario.objects.all()
    usr = request.user
    usuario = usr.username
    contexto = {'inventario': inventario,
                'usuario': usuario}
    return render(request, "registroinventario.html", contexto)


@login_required
def RegistrarInventario(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        cantidad = int(request.POST.get('cantidad'))
        if sku is None or cantidad is None:
            return render(request, "registroinventario.html")
        else:
            try:
                registro = Inventario.objects.get(sku=sku)
                registro.cantidad += cantidad
                registro.save()
            except Inventario.DoesNotExist:
                registro = Inventario.objects.create(sku=sku, cantidad=cantidad)
                registro.save()
        inventario = Inventario.objects.all()
        usr = request.user
        usuario = usr.username
        contexto = {'inventario': inventario,
                    'usuario': usuario}
        return render(request, "registroinventario.html", contexto)
    else:
        inventario = Inventario.objects.all()
        usr = request.user
        usuario = usr.username
        contexto = {'inventario': inventario,
                    'usuario': usuario}
        return render(request, "registroinventario.html", contexto)


@login_required
def LimpiarInventario(request):

    if request.method == 'POST':
        Inventario.objects.all().delete()
        inventario = Inventario.objects.all()
        usr = request.user
        usuario = usr.username
        contexto = {'inventario': inventario,
                    'usuario': usuario}
        return render(request, "registroinventario.html", contexto)
    else:
        return render(request, "inventariolimpio.html")


@login_required
def ResumenInventario(request):
    # Limpiar los registros en 0
    Inventario.objects.filter(cantidad__lte=0).delete()

    # Utilizar ambos registros
    inventario = Inventario.objects.all()
    productos = Producto.objects.all()

    # Crear conjuntos de SKU
    inventario_skus = set(inventario.values_list('sku', flat=True))
    productos_skus = set(productos.values_list('sku', flat=True))
    
    # Encontrar SKUs que están en Inventario pero no en Producto
    skus_sobrantes = inventario_skus - productos_skus
    # Encontrar SKUs que están en Producto pero no en Inventario
    skus_faltantes = productos_skus - inventario_skus
    # Encontrar SKUs que coinciden
    skus_coincidentes = productos_skus - skus_faltantes

    # Preparar los datos para el contexto
    productos_sobrantes = Inventario.objects.filter(sku__in=skus_sobrantes)
    productos_faltantes = Producto.objects.filter(sku__in=skus_faltantes)
    productos_coincidentes = Producto.objects.filter(sku__in=skus_coincidentes)

    # Calcular pérdidas
    ganancia_perdida = 0
    inversion_perdida = 0
    profal = 0
    # Cantidades diferentes en productos coincidentes
    for co in productos_coincidentes:
        inv = Inventario.objects.get(sku=co.sku)
        if inv.cantidad < co.cantidad:
            ganancia_perdida += (co.cantidad - inv.cantidad) * (co.precio_venta - co.precio_costo)
            inversion_perdida += (co.cantidad - inv.cantidad) * co.precio_costo
            co.cantidad -= inv.cantidad
        else:
            co.cantidad = 0
        profal += co.cantidad
    
    for producto in productos_faltantes:
        ganancia_perdida += (producto.precio_venta - producto.precio_costo) * producto.cantidad
        inversion_perdida += producto.precio_costo * producto.cantidad

    # Conteo de Registros de sistema
    regsys = 0
    cantsys = 0
    for rs in productos:
        regsys += 1
        cantsys += rs.cantidad

    # Conteo de Registros de inventario
    reginv = 0
    cantinv = 0
    for ri in inventario:
        reginv += 1
        cantinv += ri.cantidad

    regpc = 0
    cantpc = 0
    # Conteo de Coincidentes por Categoría
    for pc in productos_coincidentes:
        inv = Inventario.objects.get(sku=co.sku)
        regpc += 1
        cantpc += inv.cantidad


    # Conteo de productos perdidos
    for pf in productos_faltantes:
        profal += pf.cantidad

    usr = request.user
    usuario = usr.username
    contexto = {
        'skus_sobrantes': skus_sobrantes,
        'skus_faltantes': skus_faltantes,
        'productos_sobrantes': productos_sobrantes,
        'productos_faltantes': productos_faltantes,
        'productos_coincidentes': productos_coincidentes,
        'ganancia_perdida': ganancia_perdida,
        'inversion_perdida': inversion_perdida,
        'regsys': regsys,
        'cantsys': cantsys,
        'reginv': reginv,
        'cantinv': cantinv,
        'regpc': regpc,
        'cantpc': cantpc,
        'profal': profal,
        'usuario': usuario}
    return render(request, "resumeninventario.html", contexto)


@login_required
def FinalizarInventario(request):
    fecha = datetime.now()
    usuario = request.user
    contraseña = request.POST.get('contraseña')
    if request.method == 'POST':
        if usuario.check_password(contraseña):
            # Recalcular registros
            inventario = Inventario.objects.all()
            productos = Producto.objects.all()
            inventario_skus = set(inventario.values_list('sku', flat=True))
            productos_skus = set(productos.values_list('sku', flat=True))
            skus_sobrantes = inventario_skus - productos_skus
            skus_faltantes = productos_skus - inventario_skus
            skus_coincidentes = productos_skus - skus_faltantes

            productos_sobrantes = Inventario.objects.filter(sku__in=skus_sobrantes)
            productos_coincidentes = Producto.objects.filter(sku__in=skus_coincidentes)
            productos_faltantes = Producto.objects.filter(sku__in=skus_faltantes)
            
            # Eliminar registro de faltantes
            for pf in productos_faltantes:
                historial = Historial.objects.create(ingreso=fecha,
                                            movimiento='Eliminación (Inventario)',
                                            precio_costo=pf.precio_costo,
                                            precio_venta=pf.precio_venta,
                                            stock=pf.cantidad,
                                            categoria_nombre=pf.id_categoria.nombre,
                                            ubicacion_nombre=pf.id_ubicacion.nombre,
                                            sku=pf.sku)
                historial.save()
                pf.delete()

            # Actualizar cantidad de coincidentes
            for pc in productos_coincidentes:
                pc.cantidad = Inventario.objects.get(sku=pc.sku).cantidad
                historial = Historial.objects.create(ingreso=fecha,
                                            movimiento='Modificación (Inventario)',
                                            precio_costo=pc.precio_costo,
                                            precio_venta=pc.precio_venta,
                                            stock=pc.cantidad,
                                            categoria_nombre=pc.id_categoria.nombre,
                                            ubicacion_nombre=pc.id_ubicacion.nombre,
                                            sku=pc.sku)
                historial.save()
                pc.save()
            
            # Ingresar sobrantes como pendientes
            for ps in productos_sobrantes:
                producto = Producto.objects.create(sku=ps.sku,
                                        nombre='PENDIENTE',
                                        descripcion='PENDIENTE',
                                        precio_costo=0,
                                        precio_venta=0,
                                        cantidad=ps.cantidad,
                                        id_categoria_id=1,
                                        id_ubicacion_id=1)
                producto.save()
                historial = Historial.objects.create(ingreso=fecha,
                                            movimiento='REGISTRO PENDIENTE (Inventario)',
                                            precio_costo=0,
                                            precio_venta=0,
                                            stock=ps.cantidad,
                                            categoria_nombre=producto.id_categoria.nombre,
                                            ubicacion_nombre=producto.id_ubicacion.nombre,
                                            sku=producto.sku)
                historial.save()

            # Limpiar los registros en 0
            Producto.objects.filter(cantidad__lte=0).delete()
            Inventario.objects.all().delete()
            empresa = Empresa.objects.get()
            empresa.inventario = fecha
            empresa.save()

            usr = request.user
            usuario = usr.username
            return render(request, "registroinventario.html", {'mensaje': 'Inventario Finalizado', 'usuario': usuario})
        else:
            inventario = Inventario.objects.all()
            usr = request.user
            usuario = usr.username
            contexto = {'inventario': inventario,
                        'mensaje': 'Contraseña incorrecta',
                        'usuario': usuario}
            return render(request, 'registroinventario.html', contexto)
    inventario = Inventario.objects.all()
    usr = request.user
    usuario = usr.username
    contexto = {'inventario': inventario,
                'mensaje': 'Contraseña incorrecta',
                'usuario': usuario}
    return redirect(request, "resumeninventario.html", contexto)


@login_required
def GuardarInventario(request):
    # Obtener información adicional
    fecha = datetime.now().strftime('%d/%m/%Y')
    hora = datetime.now().strftime('%H:%M:%S')
    date_titulo = datetime.now().strftime('%S_%M_%H-%d_%m_%Y')
    empresa = Empresa.objects.get()
    usr = request.user
    usuario = usr.username

    # Volver a calcular las variables anteriores
    inventario = Inventario.objects.all()
    productos = Producto.objects.all()
    inventario_skus = set(inventario.values_list('sku', flat=True))
    productos_skus = set(productos.values_list('sku', flat=True))
    skus_sobrantes = inventario_skus - productos_skus
    skus_faltantes = productos_skus - inventario_skus
    skus_coincidentes = productos_skus - skus_faltantes
    productos_sobrantes = Inventario.objects.filter(sku__in=skus_sobrantes)
    productos_faltantes = Producto.objects.filter(sku__in=skus_faltantes)
    productos_coincidentes = Producto.objects.filter(sku__in=skus_coincidentes)

    ganancia_perdida = request.POST.get('ganancia_perdida')
    inversion_perdida = request.POST.get('inversion_perdida')
    regsys = request.POST.get('regsys')
    cantsys = request.POST.get('cantsys')
    reginv = request.POST.get('reginv')
    cantinv = request.POST.get('cantinv')
    regpc = request.POST.get('regpc')
    cantpc = request.POST.get('cantpc')
    profal = request.POST.get('profal')



    # Crear una respuesta HTTP con el tipo de contenido de PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Inventario_{empresa.nombre}_{date_titulo}.pdf"'

    # Crear el objeto PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter


    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 100, f"INVENTARIO {empresa.nombre} - {fecha}")


    # Resumen
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 140, "RESUMEN")

    # Datos Importantes
    p.setFont("Helvetica-Bold", 12)
    y_position = height - 160
    p.drawString(100, y_position, "Información General:")
    p.setFont("Helvetica", 12)
    y_position -= 15
    p.drawString(120, y_position, f"Registros de Sistema: {regsys}")
    y_position -= 15
    p.drawString(140, y_position, f"Stock: {cantsys}")
    y_position -= 15
    p.drawString(120, y_position, f"Registros de Inventario: {reginv}")
    y_position -= 15
    p.drawString(140, y_position, f"Stock: {cantinv}")
    y_position -= 15
    p.drawString(120, y_position, f"Registros Coincidentes: {regpc}")
    y_position -= 15
    p.drawString(140, y_position, f"Cantidad: {cantpc}")


    # Resultados
    p.setFont("Helvetica-Bold", 14)
    y_position -= 40
    p.drawString(100, y_position, "RESULTADOS")

    # Productos Sobrantes
    p.setFont("Helvetica-Bold", 12)
    y_position -= 20
    p.drawString(100, y_position, "Productos Sobrantes:")
    p.setFont("Helvetica", 12)
    y_position -= 15
    for ps in productos_sobrantes:
        p.drawString(120, y_position, f"SKU: {ps.sku}, Stock: {ps.cantidad}")
        y_position -= 15

    # Productos Faltantes
    p.setFont("Helvetica-Bold", 12)
    y_position -= 10
    p.drawString(100, y_position, "Productos Faltantes:")
    p.setFont("Helvetica", 12)
    y_position -= 15
    for pf in productos_faltantes:
        p.drawString(120, y_position, f"SKU: {pf.sku}, Nombre: {pf.nombre}, Stock: {pf.cantidad}")
        y_position -= 15
    
    # Productos Coincidentes
    p.setFont("Helvetica-Bold", 12)
    y_position -= 10
    p.drawString(100, y_position, "Productos Coincidentes:")
    p.setFont("Helvetica", 12)
    y_position -= 15
    for pc in productos_coincidentes:
        p.drawString(120, y_position, f"SKU: {pc.sku}, Nombre: {pc.nombre}, Stock: {pc.cantidad}")
        y_position -= 15

    # Pérdidas Generales
    p.setFont("Helvetica-Bold", 12)
    y_position -= 10
    p.drawString(100, y_position, "Pérdidas Generales:")
    p.setFont("Helvetica", 12)
    y_position -= 15
    p.drawString(120, y_position, f"Inversión perdida: ${inversion_perdida}")
    y_position -= 15
    p.drawString(120, y_position, f"Ganancias perdidas: ${ganancia_perdida}")
    y_position -= 15
    p.drawString(120, y_position, f"Cantidad de Productos Perdidos: {profal}")

    # Marca de cierre
    p.setFont("Helvetica", 10)
    y_position -= 40
    p.drawString(100, y_position, f"Informe generado por el usuario {usuario} a las {hora} del día {fecha}")
    y_position -= 10
    p.drawString(100, y_position, f"por 'Nombre de Software' para la empresa {empresa.nombre}.")

    # Finalizar el PDF
    p.showPage()
    p.save()

    return response