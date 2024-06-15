from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from .models import Empresa
from django.contrib.auth.decorators import login_required, user_passes_test


def is_superuser(user):
    return user.is_superuser


@login_required
def InfoCuenta(request):
    usuario = request.user
    nick = usuario.username
    nombre = usuario.first_name
    apellido = usuario.last_name
    email = usuario.email
    mensaje = ' '

    if request.method == 'POST':
        nick = request.POST.get('nick')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        passvieja = request.POST.get('passvieja')
        passnueva1 = request.POST.get('passnueva1')
        passnueva2 = request.POST.get('passnueva2')

        mensaje = 'Información guardada!'

        if passvieja and passnueva1 and passnueva2:
            if passnueva1 == passnueva2:
                if usuario.check_password(passvieja):
                    usuario.set_password(passnueva1)
                    update_session_auth_hash(request, usuario)
                    mensaje = 'Información guardada y contraseña actualizada!'
        
        usuario.username = nick
        usuario.first_name = nombre
        usuario.last_name = apellido
        usuario.email = email
        usuario.save()

    usr = request.user
    usuario = usr.username
    contexto = {'nick': nick,
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'mensaje': mensaje,
                'usuario': usuario}

    return render(request, 'cuenta.html', contexto)


@user_passes_test(is_superuser)
def InfoEmpresa(request):
    empresa = Empresa.objects.get()
    rut = empresa.rut
    dv = empresa.dv
    nombre = empresa.nombre
    direccion = empresa.direccion
    mensaje = ' '

    if request.method == 'POST':
        rut = request.POST.get('rut')
        dv = request.POST.get('dv')
        nombre = request.POST.get('nombre')
        direccion = request.POST.get('direccion')
        mensaje = 'Información guardada!'
        # GUARDAR LA INFORMACIÓN EN LA TABLA EMPRESA
        empresa.rut = rut
        empresa.dv = dv
        empresa.nombre = nombre
        empresa.direccion = direccion
        empresa.save()

    usr = request.user
    usuario = usr.username
    contexto = {'rut': rut,
                'dv': dv,
                'nombre': nombre,
                'direccion': direccion,
                'mensaje': mensaje,
                'usuario': usuario}

    return render(request, 'empresa.html', contexto)