# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from secretaria.models import OrdenTrabajo
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.http import HttpResponseRedirect
from reportlab.lib.pagesizes import letter
from django.contrib.auth.decorators import login_required,user_passes_test


def is_jefe(user):
    return user.groups.filter(name='jefe').exists()


@user_passes_test(is_jefe, login_url='/')
@login_required(login_url='/')
def gestionar_usuarios(request):
    usuarios = User.objects.all()  # Obtener todos los usuarios
    grupos = Group.objects.all()  # Obtener todos los grupos (roles)

     # Crear usuario si se detecta la acción en el formulario
    if request.method == 'POST' and request.POST.get('accion') == 'crear':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        grupo_id = request.POST.get('grupo')

        # Validar que el nombre de usuario y correo sean únicos
        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "El correo electrónico ya está en uso.")
        else:
            # Crear el usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            # Asignar grupo si se selecciona uno
            if grupo_id:
                grupo = get_object_or_404(Group, id=grupo_id)
                user.groups.add(grupo)

            messages.success(request, "Usuario creado exitosamente.")
            return redirect('gestionar_usuarios')

    # Parámetros del filtro
    query_rut = request.GET.get('rut', '').strip()
    query_rol = request.GET.get('rol', '').strip()

    # Filtrar usuarios por RUT o Rol
    if query_rut:
        usuarios = usuarios.filter(username__icontains=query_rut)  # Supongamos que usas `username` para el RUT

    if query_rol:
        if query_rol == "sin_rol":
            usuarios = usuarios.filter(groups=None)
        else:
            usuarios = usuarios.filter(groups__name__iexact=query_rol)

    # Paginación
    paginator = Paginator(usuarios, 10)  # 10 usuarios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'jefe/Gestor.html', {
        'usuarios': page_obj,
        'grupos': grupos,
        'query_rut': query_rut,
        'query_rol': query_rol
    })

@user_passes_test(is_jefe, login_url='/')
@login_required(login_url='/')
def editar_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    grupos = Group.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        is_active = request.POST.get('is_active') == "1"
        password = request.POST.get('password')  # Capturar nueva contraseña

        if User.objects.filter(username=username).exclude(id=user_id).exists():
            messages.error(request, "El nombre de usuario ya está en uso por otro usuario.")
            return redirect('gestionar_usuarios')

        if User.objects.filter(email=email).exclude(id=user_id).exists():
            messages.error(request, "El correo ya está en uso por otro usuario.")
            return redirect('gestionar_usuarios')

        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = is_active

        grupo_id = request.POST.get('grupo')
        if grupo_id:
            grupo = get_object_or_404(Group, id=grupo_id)
            user.groups.clear()
            user.groups.add(grupo)

        if password:
            user.set_password(password)

        user.save()
        messages.success(request, "Usuario editado exitosamente.")
        return redirect('gestionar_usuarios')

    return render(request, 'jefe/editar_usuario.html', {'user': user, 'grupos': grupos})


@user_passes_test(is_jefe, login_url='/')
@login_required(login_url='/')
def cambiar_estado_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.is_active = not user.is_active  # Alternar el estado
        user.save()
        estado = "activado" if user.is_active else "desactivado"
        messages.success(request, f"El usuario ha sido {estado} exitosamente.")
        return redirect('gestionar_usuarios')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'gestionar_usuarios'))



# funcionalidad para gestionar las ordenes de trabajo
@user_passes_test(is_jefe, login_url='/')
@login_required(login_url='/')
def informe(request):
    # Obtener los valores de los filtros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado = request.GET.get('estado')

    # Filtrar las órdenes de trabajo
    ordenes_trabajo = OrdenTrabajo.objects.prefetch_related('reparacion', 'vehiculo').all()

    if fecha_inicio and fecha_fin:
        ordenes_trabajo = ordenes_trabajo.filter(fecha_inicio__gte=fecha_inicio, fecha_entrega__lte=fecha_fin)

    if estado:
        ordenes_trabajo = ordenes_trabajo.filter(estado__iexact=estado)

    # Calcular el total general de todas las órdenes
    total_general = sum(orden.calcular_total() for orden in ordenes_trabajo)

    # Paginación
    paginator = Paginator(ordenes_trabajo, 10)  # 10 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pasar datos al template
    return render(request, 'jefe/informe.html', {
        'ordenes': page_obj,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'estado': estado,
        'total_general': total_general,  # Pasar el total general al template
    })

@user_passes_test(is_jefe, login_url='/')
@login_required(login_url='/')
def generar_pdf(request):
    # Crear la respuesta HTTP con tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="informe_ordenes_trabajo.pdf"'

    # Crear un objeto Canvas para el PDF
    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Configuración de fuentes
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Informe de Órdenes de Trabajo")

    # Encabezados de la tabla
    pdf.setFont("Helvetica-Bold", 10)
    encabezados = [
        "ID", "Fecha Inicio", "Fecha Entrega", "Vehículo",
        "Mecánico", "Reparaciones", "Precio Total"
    ]
    x_offsets = [50, 100, 170, 240, 310, 380, 500]  # Posiciones ajustadas
    y_offset = height - 80

    for i, encabezado in enumerate(encabezados):
        pdf.drawString(x_offsets[i], y_offset, encabezado)

    # Datos de las órdenes de trabajo
    pdf.setFont("Helvetica", 8)  # Fuente más pequeña
    y_offset -= 20
    ordenes = OrdenTrabajo.objects.prefetch_related('reparacion', 'vehiculo', 'usuario').all()

    total_general = 0  # Para calcular el total general

    for orden in ordenes:
        if y_offset < 50:  # Salto de página si el espacio es insuficiente
            pdf.showPage()
            y_offset = height - 50
            pdf.setFont("Helvetica", 8)

        # Procesar datos de la orden
        reparaciones = ", ".join([reparacion.nombre for reparacion in orden.reparacion.all()])
        reparaciones = (reparaciones[:30] + "...") if len(reparaciones) > 30 else reparaciones
        mecanico = f"{orden.usuario.first_name} {orden.usuario.last_name}" if orden.usuario else "Sin Asignar"
        vehiculo = orden.vehiculo.patente if orden.vehiculo else "Sin Vehículo"
        total_orden = orden.calcular_total()
        total_general += total_orden

        # Escribir datos en la tabla
        pdf.drawString(x_offsets[0], y_offset, str(orden.id))
        pdf.drawString(x_offsets[1], y_offset, str(orden.fecha_inicio))
        pdf.drawString(x_offsets[2], y_offset, str(orden.fecha_entrega or "No especificada"))
        pdf.drawString(x_offsets[3], y_offset, vehiculo)
        pdf.drawString(x_offsets[4], y_offset, mecanico)
        pdf.drawString(x_offsets[5], y_offset, reparaciones)
        pdf.drawString(x_offsets[6], y_offset, f"${int(total_orden)}")
        y_offset -= 20

    # Mostrar el total general en la parte inferior
    if y_offset < 50:
        pdf.showPage()
        y_offset = height - 50

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y_offset - 20, f"Total General de Todas las Órdenes: ${int(total_general)}")

    # Finalizar el PDF
    pdf.save()
    return response