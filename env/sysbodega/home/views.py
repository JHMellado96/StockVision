from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Producto, Categoria, Ubicacion, Historial
from información.models import Empresa
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from dateutil.relativedelta import relativedelta


def is_superuser(user):
    return user.is_superuser


@user_passes_test(is_superuser)
def register(request):
    usuarios = User.objects.filter(is_superuser=False)
    mensaje = ' '
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            mensaje = 'Usuario creado correctamente!'
            user = form.save()
        else:
            form = UserCreationForm()
            mensaje = 'Error al crear usuario...'
    else:
        form = UserCreationForm()

    usr = request.user
    usuario = usr.username
    contexto = {'form': form,
                'usuarios': usuarios,
                'mensaje': mensaje,
                'usuario': usuario}
    return render(request, 'registration/register.html', contexto)


@login_required
def home(request):
    usr = request.user
    usuario = usr.username
    # Obtener la fecha actual
    fecha = datetime.now()
    mes = fecha.month
    anio = fecha.year
    usuarios = User.objects.filter(is_superuser=False).count()
    categorias = Categoria.objects.all().count()
    ubicaciones = Ubicacion.objects.all().count()
    prod = Producto.objects.all()

    if not request.user.is_authenticated:
        return redirect('login')
    else:
        try:
            emp = Empresa.objects.get()
            empresa = emp.nombre
            # INVENTARIO
            if emp.inventario:
                inventario = emp.inventario.strftime('%d/%m/%Y')
                # Próximo inventario
                pi = inventario + relativedelta(months=1)
                proximo_inventario = pi.strftime('%d/%m/%Y')
            else:
                inventario = 'sin registros'
                proximo_inventario = 'sin registros'
        except Empresa.DoesNotExist:
            empresa = 'no'
            inventario = 'sin registros'
            proximo_inventario = 'sin registros'
        
        # PRODUCTOS
        productos = Producto.objects.all().count()
        # INGRESOS
        ing = Historial.objects.filter(ingreso__month=mes, movimiento='Ingreso')
        ingresos = 0
        for i in ing:
            ingresos += i.stock
        # SALIDAS
        sal = Historial.objects.filter(Q(ingreso__month=mes) & Q(movimiento='Salida por Retiro') | Q(movimiento='Salida por Vencimiento') | Q(movimiento='Salida por Obsolescencia'))
        salidas = 0
        for s in sal:
            salidas += s.stock
        # MOVIMIENTOS
        movimientos = Historial.objects.filter(ingreso__month=mes, ingreso__year=anio).count()
        # GANANCIAS E INVERSIONES
        costo = 0
        ganancia = 0
        for p in prod:
            costo += p.precio_costo
            ganancia += p.precio_venta - p.precio_costo
        
        contexto = {'productos': productos,
                    'empresa': empresa,
                    'ingresos': ingresos,
                    'salidas': salidas,
                    'inventario': inventario,
                    'movimientos': movimientos,
                    'usuario': usuario,
                    'usuarios': usuarios,
                    'categorias': categorias,
                    'ubicaciones': ubicaciones,
                    'costo': costo,
                    'ganancia': ganancia,
                    'proximo_inventario': proximo_inventario}
    return render(request, 'home.html', contexto)


@login_required
def RegInicial(request):
    fecha = datetime.now()
    if request.method == 'POST':
        # GUARDAR DATOS EN LA TABLA "EMPRESA"
        emp_rut = request.POST.get('rut')
        emp_dv = request.POST.get('dv')
        emp_nombre = request.POST.get('nombre')
        emp_direccion = request.POST.get('direccion')
        empresa = Empresa.objects.create(rut=emp_rut,
                                         dv=emp_dv,
                                         nombre=emp_nombre,
                                         direccion=emp_direccion,
                                         modificación=fecha)
        empresa.save()
        # GUARDAR DATOS EN LA TABLA "UBICACIÓN"
        ubi_nombre = request.POST.get('nombreubicacion')
        ubi_descripcion = request.POST.get('descripcionubicacion')
        ubicacion = Ubicacion.objects.create(nombre=ubi_nombre,
                                             descripcion=ubi_descripcion)
        ubicacion.save()
        # GUARDAR DATOS EN LA TABLA "CATEGORÍA"
        cat_nombre = request.POST.get('nombrecategoria')
        cat_descripcion = request.POST.get('descripcioncategoria')
        categoria = Categoria.objects.create(nombre=cat_nombre,
                                             descripcion=cat_descripcion)
        categoria.save()
        return redirect('home')
    return render(request, 'home.html')


@user_passes_test(is_superuser)
def EliminarUsuario(request):
    usuarios = User.objects.filter(is_superuser=False)
    mensaje = ' '
    form = UserCreationForm()
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        usuario = User.objects.get(id=usuario_id)
        usuario.delete()
        mensaje = 'Usuario eliminado correctamente!'
    usr = request.user
    usuario = usr.username
    contexto = {'form': form,
                'usuarios': usuarios,
                'mensaje': mensaje,
                'usuario': usuario}
    return render(request, 'registration/register.html', contexto)