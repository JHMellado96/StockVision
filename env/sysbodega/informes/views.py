from django.shortcuts import render, redirect
from registroinventario.models import Producto, Categoria, Ubicacion, Historial, Inventario
from ingreso.views import IngresoHistorico
from salida.views import SalidaHistorico
from información.models import Empresa
from django.contrib.auth.models import User
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from datetime import datetime
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO



def is_superuser(user):
    return user.is_superuser


@user_passes_test(is_superuser)
def Informes(request):
    historial = Historial.objects.all()
    ingresos = IngresoHistorico.objects.all()
    salidas = SalidaHistorico.objects.all()
    meses = set()
    for registro in historial:
        mes = registro.ingreso.strftime("%B, %Y")
        meses.add(mes)

    meses2 = set()
    for ing in ingresos:
        mes2 = ing.fecha.strftime("%B, %Y")
        meses2.add(mes2)
    for sal in salidas:
        mes3 = sal.fecha.strftime("%B, %Y")
        meses2.add(mes3)
    # Ordenar los meses para que se muestren en orden cronológico
    meses = sorted(meses, key=lambda x: datetime.strptime(x, "%B, %Y"))
    meses2 = sorted(meses2, key=lambda x: datetime.strptime(x, "%B, %Y"))

    usr = request.user
    usuario = usr.username
    contexto = {'usuario': usuario,
                'meses': meses,
                'meses2': meses2}
    return render(request, 'menuinformes.html', contexto)


@user_passes_test(is_superuser)
def ProductosTotales(request):
    # Obtener información adicional
    fecha = datetime.now().strftime('%d/%m/%Y')
    hora = datetime.now().strftime('%H:%M:%S')
    date_titulo = datetime.now().strftime('%S_%M_%H-%d_%m_%Y')
    empresa = Empresa.objects.get()
    usr = request.user
    usuario = usr.username

    # Cálculos del informe
    productos = Producto.objects.all()
    cantidad_registros = productos.count()
    stock = 0
    for prod in productos:
        stock += prod.cantidad

    # Obtener productos y ordenar por cantidad en stock
    productos = Producto.objects.all().order_by('-cantidad')
    total_inversion = sum([prod.precio_costo * prod.cantidad for prod in productos])

    # Crear una gráfica con los 5 productos con más stock
    top_5_productos = productos[:5]
    nombres_top_5 = [prod.nombre for prod in top_5_productos]
    stock_top_5 = [prod.cantidad for prod in top_5_productos]

    fig, ax = plt.subplots()
    ax.barh(nombres_top_5, stock_top_5, color='blue')
    ax.set_title('Top 5 Productos con Más Stock')
    ax.set_xlabel('Cantidad en Stock')
    ax.set_ylabel('Productos')
    ax.invert_yaxis()

    # Guardar la gráfica en un objeto BytesIO
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)

    # Crear una respuesta HTTP con el tipo de contenido de PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Ganancias_e_Inversiones_Mensuales_{empresa.nombre}_{date_titulo}.pdf"'

    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1
    subtitle_style = styles['Heading2']
    normal_style = styles['BodyText']

    # Título
    elements.append(Paragraph(f"Existencias Totales | {empresa.nombre} - {fecha}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Gráfica
    elements.append(Paragraph("Top 5 Productos con Más Stock", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))
    from reportlab.platypus import Image
    img = Image(buffer)
    img.drawHeight = 4 * inch
    img.drawWidth = 6 * inch
    elements.append(img)
    elements.append(Spacer(1, 0.2 * inch))

    # Resumen
    elements.append(Paragraph("RESUMEN", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(f"Registros de Sistema: {int(cantidad_registros)}", normal_style))
    elements.append(Paragraph(f"Stock Total: {int(stock)}", normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Detalles
    elements.append(Paragraph("DETALLES", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))

    # T A B L A
    data = [["N°", "SKU", "Nombre", "Stock"]]
    cont = 1
    for pr in productos:
        data.append([cont, pr.sku, pr.nombre, int(pr.cantidad)])
        cont += 1
    table = Table(data, colWidths=[0.5 * inch, 2 * inch, 3 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.aliceblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))

    # Marca de cierre
    elements.append(Paragraph(f"Informe generado por el usuario {usuario} a las {hora} del día {fecha} por STOCK VISION para la empresa {empresa.nombre}.", normal_style))

    # Construir el PDF
    doc.build(elements)

    return response


@user_passes_test(is_superuser)
def GananciasEInversion(request):
    # Obtener información adicional
    fecha = datetime.now().strftime('%d/%m/%Y')
    hora = datetime.now().strftime('%H:%M:%S')
    date_titulo = datetime.now().strftime('%S_%M_%H-%d_%m_%Y')
    empresa = Empresa.objects.get()
    usr = request.user
    usuario = usr.username

    # Cálculos del informe
    productos = Producto.objects.all()
    inversion = 0
    ganancia = 0
    for prod in productos:
        inversion += prod.precio_costo * prod.cantidad
        ganancia += (prod.precio_venta - prod.precio_costo) * prod.cantidad

    # Crear una gráfica con Matplotlib
    fig, ax = plt.subplots()
    categorias = ['Inversión', 'Ganancia']
    valores = [inversion, ganancia]
    ax.bar(categorias, valores, color=['red', 'blue'])
    ax.set_title('Inversión vs Ganancia')
    ax.set_xlabel('Categoría')
    ax.set_ylabel('Valor en $')

    # Guardar la gráfica en un objeto BytesIO
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)

    # Crear una respuesta HTTP con el tipo de contenido de PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Ganancias_e_Inversiones_Mensuales_{empresa.nombre}_{date_titulo}.pdf"'

    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1
    subtitle_style = styles['Heading2']
    normal_style = styles['BodyText']

    # Título
    elements.append(Paragraph(f"Ganancias e Inversiones | {empresa.nombre} - {fecha}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Gráfica
    elements.append(Paragraph("Gráfica de Inversión vs Ganancia", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))
    from reportlab.platypus import Image
    img = Image(buffer)
    img.drawHeight = 4 * inch
    img.drawWidth = 6 * inch
    elements.append(img)
    elements.append(Spacer(1, 0.2 * inch))

    # Resumen
    elements.append(Paragraph("RESUMEN", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(f"Inversión en Actual Bodega: ${int(inversion):,}", normal_style))
    elements.append(Paragraph(f"Ganancias Esperadas de Inversión: ${int(ganancia):,}", normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Detalles
    elements.append(Paragraph("DETALLES", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))

    # T A B L A
    data = [["N°", "SKU", "Inversión Un.", "Ganancia Un.", "Inversión Total", "Ganancia Total"]]
    cont = 1
    for pr in productos:
        inv_unit = f"${int(pr.precio_costo):,}"
        gan_unit = f"${int(pr.precio_venta - pr.precio_costo):,}"
        inv_total = f"${int(pr.precio_costo * pr.cantidad):,}"
        gan_total = f"${int((pr.precio_venta - pr.precio_costo) * pr.cantidad):,}"
        data.append([cont, pr.sku, inv_unit, gan_unit, inv_total, gan_total])
        cont += 1
    table = Table(data, colWidths=[0.5 * inch, 1.5 * inch, 1.25 * inch, 1.25 * inch, 1.25 * inch, 1.25 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.aliceblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))

    # Marca de cierre
    elements.append(Paragraph(f"Informe generado por el usuario {usuario} a las {hora} del día {fecha} por STOCK VISION para la empresa {empresa.nombre}.", normal_style))

    # Construir el PDF
    doc.build(elements)

    return response


@user_passes_test(is_superuser)
def PerdidasMensuales(request):
    # Obtener información adicional
    fecha = datetime.now().strftime('%d/%m/%Y')
    hora = datetime.now().strftime('%H:%M:%S')
    date_titulo = datetime.now().strftime('%S_%M_%H-%d_%m_%Y')
    empresa = Empresa.objects.get()
    usr = request.user
    usuario = usr.username

    # Filtrar los registros si se selecciona un mes
    historial = Historial.objects.all()
    if request.method == 'POST':
        mes_seleccionado = request.POST.get('mes_perdida')
        if mes_seleccionado:
            mes, year = mes_seleccionado.split(", ")
            historial = historial.filter(ingreso__month=datetime.strptime(mes, "%B").month,
                                         ingreso__year=int(year))

    # Cálculos del informe
    obsoletos = 0
    vencidos = 0
    perdidos = 0
    productos_obsoletos = defaultdict(int)
    productos_vencidos = defaultdict(int)
    productos_perdidos = defaultdict(int)

    for his in historial:
        if his.movimiento == 'Salida por Obsolescencia':
            productos_obsoletos[his.sku] += his.stock
            obsoletos += his.stock
        elif his.movimiento == 'Salida por Vencimiento':
            productos_vencidos[his.sku] += his.stock
            vencidos += his.stock
        elif his.movimiento == 'Eliminación (Inventario)':
            productos_perdidos[his.sku] += his.stock
            perdidos += his.stock
    
    # Crear una gráfica con Matplotlib
    fig, ax = plt.subplots()
    categorias = ['Obsoletos', 'Vencidos', 'Perdidos']
    valores = [obsoletos, vencidos, perdidos]
    ax.bar(categorias, valores, color=['blue', 'orange', 'red'])
    ax.set_title('Pérdidas Mensuales')
    ax.set_xlabel('Categoría')
    ax.set_ylabel('Cantidad')

    # Guardar la gráfica en un objeto BytesIO
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)

    # Crear una respuesta HTTP con el tipo de contenido de PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Pérdidas_Mensuales_{empresa.nombre}_{date_titulo}.pdf"'

    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1
    subtitle_style = styles['Heading2']
    normal_style = styles['BodyText']

    # Título
    elements.append(Paragraph(f"Pérdidas Mensuales | {empresa.nombre} - {fecha}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Gráfica
    elements.append(Paragraph("Gráfica de Pérdidas Mensuales", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))
    from reportlab.platypus import Image
    img = Image(buffer)
    img.drawHeight = 4 * inch
    img.drawWidth = 6 * inch
    elements.append(img)
    elements.append(Spacer(1, 0.2 * inch))

    # Resumen
    elements.append(Paragraph("RESUMEN", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(f"Mes de Registros: {mes_seleccionado}", normal_style))
    elements.append(Paragraph(f"Stock Obsoleto Registrados: {obsoletos} productos.", normal_style))
    elements.append(Paragraph(f"Stock Vencido Registrados: {vencidos} productos.", normal_style))
    elements.append(Paragraph(f"Stock Perdido Registrados: {perdidos} productos.", normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Detalles
    elements.append(Paragraph("DETALLES", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))


    elements.append(Paragraph(f"PRODUCTOS OBSOLETOS:", normal_style))
    elements.append(Paragraph(f" ", normal_style))
    # T A B L A
    data = [["N°", "SKU", "Nombre", "Cantidad"]]
    cont = 1
    for sku, cantidad in productos_obsoletos.items():
        producto = Producto.objects.get(sku=sku)
        data.append([cont, sku, producto.nombre, cantidad])
        cont += 1
    table = Table(data, colWidths=[0.5 * inch, 2 * inch, 3 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.aliceblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))


    elements.append(Paragraph(f"PRODUCTOS VENCIDOS:", normal_style))
    elements.append(Paragraph(f" ", normal_style))
    # T A B L A
    data = [["N°", "SKU", "Nombre", "Cantidad"]]
    cont = 1
    for sku, cantidad in productos_vencidos.items():
        producto = Producto.objects.get(sku=sku)
        data.append([cont, sku, producto.nombre, cantidad])
        cont += 1
    table = Table(data, colWidths=[0.5 * inch, 2 * inch, 3 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.aliceblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))


    elements.append(Paragraph(f"PRODUCTOS PERDIDOS:", normal_style))
    elements.append(Paragraph(f" ", normal_style))
    # T A B L A
    data = [["N°", "SKU", "Nombre", "Cantidad"]]
    cont = 1
    for sku, cantidad in productos_perdidos.items():
        producto = Producto.objects.get(sku=sku)
        data.append([cont, sku, producto.nombre, cantidad])
        cont += 1
    table = Table(data, colWidths=[0.5 * inch, 2 * inch, 3 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.aliceblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))


    # Marca de cierre
    elements.append(Paragraph(f"Informe generado por el usuario {usuario} a las {hora} del día {fecha} por STOCK VISION para la empresa {empresa.nombre}.", normal_style))

    # Construir el PDF
    doc.build(elements)

    return response


@user_passes_test(is_superuser)
def IngresosYSalidas(request):
    # Obtener información adicional
    fecha = datetime.now().strftime('%d/%m/%Y')
    hora = datetime.now().strftime('%H:%M:%S')
    date_titulo = datetime.now().strftime('%S_%M_%H-%d_%m_%Y')
    empresa = Empresa.objects.get()
    usr = request.user
    usuario = usr.username

    # Filtrar los registros si se selecciona un mes
    ingresos = IngresoHistorico.objects.all()
    salidas = SalidaHistorico.objects.all()
    if request.method == 'POST':
        mes_seleccionado = request.POST.get('mes_ingysal')
        if mes_seleccionado:
            mes, year = mes_seleccionado.split(", ")
            ingresos = ingresos.filter(fecha__month=datetime.strptime(mes, "%B").month,
                                         fecha__year=int(year))
            salidas = salidas.filter(fecha__month=datetime.strptime(mes, "%B").month,
                                         fecha__year=int(year))

    # Cálculos del informe
    ing_mov = ingresos.count()
    sal_mov = salidas.count()

    # Crear una gráfica con Matplotlib
    fig, ax = plt.subplots()
    categorias = ['Ingresos', 'Salidas']
    valores = [ing_mov, sal_mov]
    ax.bar(categorias, valores, color=['blue', 'red'])
    ax.set_title('Ingresos vs Salidas')
    ax.set_xlabel('Categoría')
    ax.set_ylabel('Cantidad')

    # Guardar la gráfica en un objeto BytesIO
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)

    # Crear una respuesta HTTP con el tipo de contenido de PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Ingresos_Y_Salidas_Mensuales_{empresa.nombre}_{date_titulo}.pdf"'

    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1
    subtitle_style = styles['Heading2']
    normal_style = styles['BodyText']

    # Título
    elements.append(Paragraph(f"Ingresos y Salidas Mensuales | {empresa.nombre} - {fecha}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Gráfica
    elements.append(Paragraph("Gráfica de Ingresos vs Salidas", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))
    from reportlab.platypus import Image
    img = Image(buffer)
    img.drawHeight = 4 * inch
    img.drawWidth = 6 * inch
    elements.append(img)
    elements.append(Spacer(1, 0.2 * inch))

    # Resumen
    elements.append(Paragraph("RESUMEN", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(f"Mes de Registros: {mes_seleccionado}", normal_style))
    elements.append(Paragraph(f"Ingresos Totales Registrados: {ing_mov}", normal_style))
    elements.append(Paragraph(f"Salidas Totales Registrados: {sal_mov}", normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Detalles
    elements.append(Paragraph("DETALLES", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))


    elements.append(Paragraph(f"INGRESOS:", normal_style))
    elements.append(Paragraph(f" ", normal_style))
    # T A B L A Ingresos
    data = [["N°", "Boleta/Factura", "Usuario", "Fecha", "Cantidad"]]
    cont = 1
    for i in ingresos:
        data.append([cont, i.boleta, i.usuario, i.fecha, i.cantidad])
        cont += 1
    table = Table(data, colWidths=[0.5 * inch, 1.5 * inch, 2 * inch, 2 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.aliceblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))


    elements.append(Paragraph(f"SALIDAS:", normal_style))
    elements.append(Paragraph(f" ", normal_style))
    # T A B L A Salidas
    data = [["N°", "Usuario", "Fecha", "Cantidad"]]
    cont = 1
    for s in salidas:
        data.append([cont, s.usuario, s.fecha, s.cantidad])
        cont += 1
    table = Table(data, colWidths=[0.5 * inch, 2.5 * inch, 2 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.aliceblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))


    # Marca de cierre
    elements.append(Paragraph(f"Informe generado por el usuario {usuario} a las {hora} del día {fecha} por STOCK VISION para la empresa {empresa.nombre}.", normal_style))

    # Construir el PDF
    doc.build(elements)

    return response


@user_passes_test(is_superuser)
def MovimientosMensuales(request):
    # Obtener información adicional
    fecha = datetime.now().strftime('%d/%m/%Y')
    hora = datetime.now().strftime('%H:%M:%S')
    date_titulo = datetime.now().strftime('%S_%M_%H-%d_%m_%Y')
    empresa = Empresa.objects.get()
    usr = request.user
    usuario = usr.username

    # Filtrar los registros si se selecciona un mes
    historial = Historial.objects.all()
    if request.method == 'POST':
        mes_seleccionado = request.POST.get('mes_movimientos')
        if mes_seleccionado:
            mes, year = mes_seleccionado.split(", ")
            historial = historial.filter(ingreso__month=datetime.strptime(mes, "%B").month,
                                         ingreso__year=int(year))

    # Cálculos del informe
    movimientos = 0
    for his in historial:
        movimientos += 1

    # Crear una respuesta HTTP con el tipo de contenido de PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Movimientos_Mensuales_{empresa.nombre}_{date_titulo}.pdf"'

    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1
    subtitle_style = styles['Heading2']
    normal_style = styles['BodyText']

    # Título
    elements.append(Paragraph(f"Movimientos Mensuales | {empresa.nombre} - {fecha}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Resumen
    elements.append(Paragraph("RESUMEN", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(f"Mes de Registros: {mes_seleccionado}", normal_style))
    elements.append(Paragraph(f"Movimientos Totales Registrados: {movimientos}", normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Detalles
    elements.append(Paragraph("DETALLES", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))


    # T A B L A
    data = [["N°", "SKU", "Movimiento", "Cantidad"]]
    cont = 1
    for h in historial:
        data.append([cont, h.sku, h.movimiento, h.ingreso])
        cont += 1
    table = Table(data, colWidths=[0.5 * inch, 2 * inch, 3 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.aliceblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))


    # Marca de cierre
    elements.append(Paragraph(f"Informe generado por el usuario {usuario} a las {hora} del día {fecha} por STOCK VISION para la empresa {empresa.nombre}.", normal_style))

    # Construir el PDF
    doc.build(elements)

    return response