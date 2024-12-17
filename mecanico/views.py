from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.core.paginator import Paginator
from secretaria.models import OrdenTrabajo, Reparacion
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from django.shortcuts import get_object_or_404
from django.contrib import messages

def is_mecanico(user):
    return user.groups.filter(name='mecanicos').exists()

# Create your views here.

@login_required(login_url='/')
@user_passes_test(is_mecanico, login_url='/')
def mecanico(request):
    # Obtener los valores de los filtros
    rut = request.GET.get('rut', '').strip()
    patente = request.GET.get('patente', '').strip()
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_termino = request.GET.get('fecha_termino', '').strip()
    

    # Inicializar las órdenes de trabajo como vacías
    ordenes_trabajo = OrdenTrabajo.objects.none()

    try:
        # Aplicar filtros solo si se proporciona al menos uno
       
        if rut or patente or (fecha_inicio and fecha_termino):
            ordenes_trabajo = OrdenTrabajo.objects.exclude(estado="Terminado").order_by('fecha_inicio')

            if rut:
                ordenes_trabajo = ordenes_trabajo.filter(usuario__username__icontains=rut)

            if patente:
                ordenes_trabajo = ordenes_trabajo.filter(vehiculo__patente__icontains=patente)

            if fecha_inicio and fecha_termino:
                ordenes_trabajo = ordenes_trabajo.filter(
                fecha_inicio__gte=fecha_inicio,
                fecha_inicio__lte=fecha_termino
                )
                
            if rut and patente:
                ordenes_trabajo = ordenes_trabajo.filter(
                    usuario__username__icontains=rut,
                    vehiculo__patente__icontains=patente
                )

            if rut and fecha_inicio and fecha_termino:
                ordenes_trabajo = ordenes_trabajo.filter(
                    usuario__username__icontains=rut,
                    fecha_inicio__gte=fecha_inicio,
                    fecha_inicio__lte=fecha_termino
                )

            if patente and fecha_inicio and fecha_termino:
                ordenes_trabajo = ordenes_trabajo.filter(
                    vehiculo__patente__icontains=patente,
                    fecha_inicio__gte=fecha_inicio,
                    fecha_inicio__lte=fecha_termino
                )
                
            if patente and rut and fecha_inicio and fecha_termino:
                ordenes_trabajo = ordenes_trabajo.filter(
                    vehiculo__patente__icontains=patente,
                    usuario__username__icontains=rut,
                    fecha_inicio__gte=fecha_inicio,
                    fecha_inicio__lte=fecha_termino
                )

    
    except Exception as e:
        return render(request, 'mecanico/mecanico.html', {
            'error': f'Error al procesar la solicitud: {str(e)}',
            'rut': rut,
            'patente': patente,
            'fecha_inicio': fecha_inicio,
            'fecha_termino': fecha_termino,
        })

    # Paginación
    paginator = Paginator(ordenes_trabajo, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'mecanico/mecanico.html',
        {
            'ordenes': page_obj,
            'rut': rut,
            'patente': patente,
            'fecha_inicio': fecha_inicio,
            'fecha_termino': fecha_termino,
            
        }
    )
    
def otmecanico(request, ot_id):
    ot = get_object_or_404(OrdenTrabajo, id=ot_id)
    reparaciones = ot.reparacion.all()

    if request.method == 'POST':
        # Obtener el nuevo estado
        nuevo_estado = request.POST.get('estado', ot.estado)
        
        # Verificar si todos los checkboxes están marcados al intentar cambiar a Terminado
        hidden_inputs = [f'reparacion_hidden_{r.id}' for r in reparaciones]
        todos_marcados = all(request.POST.get(hidden, 'false') == 'true' for hidden in hidden_inputs)
        
        # Validación: Estado de OT a "Terminado" solo si todas las reparaciones están completadas
        if nuevo_estado == 'Terminado':
            if not todos_marcados:
                messages.error(request, "No puede cambiar el estado a 'Terminado' hasta que todas las reparaciones estén completadas.")
                return redirect('otmecanico', ot_id=ot.id)

        # Actualizar reparaciones 
        for reparacion in reparaciones:
            hidden_name = f'reparacion_hidden_{reparacion.id}'
            
            # Usar el valor del campo oculto para determinar el estado
            reparacion.estado = request.POST.get(hidden_name, 'false') == 'true'
            reparacion.save()

        # Guardar cambios en la OT
        ot.estado = nuevo_estado
        ot.observacion = request.POST.get('observacion', ot.observacion)
        ot.save()

        messages.success(request, "Orden de trabajo actualizada correctamente.")
        return redirect('otmecanico', ot_id=ot.id)

    return render(request, 'mecanico/otmecanico.html', {
        'ot': ot,
        'reparaciones': reparaciones
    })
    
def salir (request):
   
    logout(request)
    return redirect('login')

