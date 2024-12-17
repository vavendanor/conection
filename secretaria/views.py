from email.message import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Cliente,Reparacion,Vehiculo,OrdenTrabajo
from django.contrib.auth.models import User
from .Form import FormularioCliente,FormularioVehiculo,ContactForm,ReparacionForm,OtForm
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Max

# Create your views here.

def is_secretaria(user):
    return user.groups.filter(name='secretarias').exists()



#funcionalidad crear cliente

@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def crearCliente(request):
    if request.method == 'POST':
        form = FormularioCliente(request.POST)
        if form.is_valid():
            form.save()  # Guarda el cliente en la base de datos
            messages.success(request, "Cliente creado exitosamente.")
            return redirect('crearCliente')  # Redirige después de guardar
        else:
            messages.error(request, "Hubo un error al crear el cliente.")
    else:
        form = FormularioCliente()

    return render(request, 'core/crearCliente.html', {'form': form})



#Funcionalidad crear vehiculo

@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def crearV(request):
    if request.method == 'POST':
        form = FormularioVehiculo(request.POST)
        if form.is_valid():
            try:
                # Obtenemos el cliente por el RUT ingresado
                rut_cliente = request.POST.get('rut_cliente')
                cliente = Cliente.objects.get(rut=rut_cliente)

                # Guardamos el vehículo en la base de datos
                vehiculo = form.save(commit=False)
                vehiculo.cliente = cliente
                vehiculo.save()

                # Mostramos un mensaje de éxito
                messages.success(request, f"El vehículo con patente {vehiculo.patente} ha sido registrado exitosamente.")
                return redirect('crearVehiculos')
            except Cliente.DoesNotExist:
                # Mensaje de error si el cliente no existe
                messages.error(request, f"No se encontró un cliente con el RUT {rut_cliente}.")
        else:
            # Mensajes de error del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = FormularioVehiculo()

    return render(request, 'core/crearV.html', {'form': form})





#crearOT
@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def crearOT(request):
    reparaciones = Reparacion.objects.all()  # Obtener todas las reparaciones disponibles

    if request.method == 'POST':
        patente = request.POST.get('patente')
        fecha_inicio = request.POST.get('date')
        fecha_entrega = request.POST.get('dateEnd')
        rutMecanico = request.POST.get('rutMecanico')
        rut_cliente = request.POST.get('rut_cliente') 
        observacion = request.POST.get('descripcion')  # Cambié a 'observacion' según el modelo
        reparaciones_ids = request.POST.getlist('reparaciones')  # Obtén una lista de los IDs seleccionados

        try:
            # Busca las relaciones necesarias
            vehiculo = Vehiculo.objects.get(patente=patente)
            user = User.objects.get(username=rutMecanico)
            cliente = Cliente.objects.get(rut=rut_cliente)

        except Vehiculo.DoesNotExist:
            return render(request, 'core/crearOT.html', {'error': 'Patente no encontrada', 'reparaciones': reparaciones})
        except User.DoesNotExist:
            return render(request, 'core/crearOT.html', {'error': 'Rut del mecánico no encontrado', 'reparaciones': reparaciones})
        except Cliente.DoesNotExist:
            return render(request, 'core/crearOT.html', {'error': 'RUT del cliente no encontrado', 'reparaciones': reparaciones})

        # Guarda la nueva orden de trabajo en la base de datos
        nueva_orden_trabajo = OrdenTrabajo(
            fecha_inicio=fecha_inicio,
            fecha_entrega=fecha_entrega,
            estado="Pendiente",  # Estado inicial
            observacion=observacion,
            cliente=cliente,
            vehiculo=vehiculo,
            usuario=user
        )
        nueva_orden_trabajo.save()  # Guarda la orden primero para obtener el ID

        # Asocia las reparaciones seleccionadas
        for reparacion_id in reparaciones_ids:
            try:
                reparacion = Reparacion.objects.get(id=reparacion_id)
                nueva_orden_trabajo.reparacion.add(reparacion)  # Añade la reparación
            except Reparacion.DoesNotExist:
                continue  # Si alguna reparación no existe, la ignoramos

        nueva_orden_trabajo.save()  # Asegúrate de guardar los cambios finales

        return redirect('gestionarOrdenTrabjos')  # Redirige a una página de confirmación
    
    return render(request, 'core/crearOT.html', {
        'reparaciones': reparaciones
    })






#Eliminar cliente

@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def deleteCl(request, id_cliente):
    cliente = get_object_or_404(Cliente, pk=id_cliente)  # Síncrono
    cliente.delete()  # Síncrono
    return redirect('gestionarC')  # Redirige a la vista de gestión de clientes

#Edit cliente
@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def edit(request, id_cliente):
    # Obtiene el cliente por su ID
    cliente = get_object_or_404(Cliente, id=id_cliente)
    
    if request.method == 'POST':
        # Procesa los datos enviados
        form = FormularioCliente(request.POST, instance=cliente)
        if form.is_valid():
            form.save()  # Guarda los cambios en la base de datos
            messages.success(request, "Cliente actualizado exitosamente.")  # Mensaje de éxito
            return redirect('gestionarC')  # Redirige a la lista de clientes
        else:
            # Muestra mensajes de error si el formulario no es válido
            messages.error(request, "Hubo un error al actualizar el cliente.")
    else:
        # Prellena el formulario con los datos del cliente
        form = FormularioCliente(instance=cliente)
    
    # Renderiza el template con el formulario y los datos del cliente
    return render(request, "core/clienteEdit.html", {"form": form, "cliente": cliente})

@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def crearReparaciones(request):
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            precio = request.POST.get('precio')
            descripcion = request.POST.get('descripcion')

            Reparaciones = Reparacion(nombre=nombre, precio=precio, descripcion=descripcion)
            Reparaciones.save()
            return redirect('gestionarReparaciones')
        return render(request, 'core/crearReparaciones.html')





#Buscar cliente

@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def gestionarC(request):
    rut_buscar = request.GET.get('rutCliente')  # Obtiene el RUT del formulario
    if rut_buscar:
        resultados = Cliente.objects.filter(rut__icontains=rut_buscar)  # Filtra por RUT
    else:
        resultados = Cliente.objects.all()  # Muestra todos los clientes si no hay búsqueda

    # Paginación
    paginator = Paginator(resultados, 3)  # 3 registros por página
    page_number = request.GET.get('page')  # Número de la página actual
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/gestionarC.html', {
        'resultados': page_obj,  # Pasa solo los clientes de la página actual
        'rut_buscar': rut_buscar,
        'page_obj': page_obj  # Pasa el objeto de paginación al template
    })


def validar_rut(request):
    rut = request.GET.get('rut', None)  # Obtén el RUT de la solicitud GET
    if rut:
        existe = Cliente.objects.filter(rut=rut).exists()  # Verifica si el RUT existe en la base de datos
        return JsonResponse({'existe': existe})
    return JsonResponse({'existe': False}, status=400)  # Responde con un error si no se envía el RUT

#Buscar cliente




## Gestión de Orden de Trabajo
@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def gestionarOT(request):
    patente = request.GET.get('patente', None)

    if patente:
        # Filtrar por patente y estado "Terminado"
        data = OrdenTrabajo.objects.filter(vehiculo__patente__iexact=patente)
    else:
        # Mostrar todas las órdenes con estado
        data = OrdenTrabajo.objects.filter(estado='Terminado')

    # Calcular total para cada orden
    for orden in data:
        orden.total_precio = orden.calcular_total()  # Usa el método calcular_total

    # Paginación
    paginator = Paginator(data, 3)  # 3 registros por página
    page_number = request.GET.get('page')  # Número de la página actual
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/gestionarOT.html', {
        'ordenes': page_obj,  # Órdenes paginadas
        
    })


@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def gestionarReparaciones(request):
    # Obtener el ID más grande
    max_id = Reparacion.objects.aggregate(Max('id'))['id__max'] or 0
    max_digitos = len(str(max_id))  # Número de dígitos del ID más grande

    # Obtener el código de búsqueda
    codigo = request.GET.get('codigo', '').strip()

    if codigo:
        # Si el código es válido y no está vacío, filtrar las reparaciones
        if codigo.isdigit():
            reparaciones = Reparacion.objects.filter(id=int(codigo))
        else:
            reparaciones = Reparacion.objects.none()  # Ningún resultado si no es numérico
    else:
        # Si el campo de búsqueda está vacío, mostrar todas las reparaciones
        reparaciones = Reparacion.objects.all()

    # Paginación
    paginator = Paginator(reparaciones, 10)  # 3 registros por página
    page_number = request.GET.get('page')  # Número de la página actual
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/gestionarReparaciones.html', {
        'ordenes': page_obj,        # Reparaciones paginadas
        'max_digitos': max_digitos  # Número máximo de dígitos para la validación
    })




#Gestionar Vehiculo###################################
@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def gestionarV(request):
    patente = request.GET.get('patente')  # Cambia a 'patente' para obtener la patente
    resultados = None

    if patente:
        resultados = Vehiculo.objects.filter(patente__icontains=patente)
    else: 
        resultados=Vehiculo.objects.all()

      # Paginación
    paginator = Paginator(resultados, 3)  # 3 registros por página
    page_number = request.GET.get('page')  # Número de la página actual
    page_obj = paginator.get_page(page_number)     
    return render(request, 'core/gestionarV.html', {
        
        
        'ordenes':page_obj
    })


#Eliminar Vehiculo

@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def deleteVC(request, id_vehiculo):
    try:
        # Busca el vehículo por su ID
        vehiculo_obj = Vehiculo.objects.get(id=id_vehiculo)
        vehiculo_obj.delete()  # Elimina el objeto
        return redirect('gestionarVehiculos')  # Redirige a la gestión de vehículos
    except Vehiculo.DoesNotExist:
        # Manejo de error si no se encuentra el vehículo
        return render(request, 'core/error.html', {'error': 'Vehículo no encontrado'})


@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def editV(request, id_vehiculo):
    vehiculo = get_object_or_404(Vehiculo, id=id_vehiculo)
    
    if request.method == 'POST':
        # Si se envía el formulario, procesa los datos
        form = FormularioVehiculo(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()  # Guarda los cambios en la base de datos
            return redirect('gestionarVehiculos')  # Redirige a la vista de gestión de clientes
    else:
        # Si es una solicitud GET, muestra el formulario prellenado
        form = FormularioVehiculo(instance=vehiculo)
    
    return render(request, "core/vehiculoEdit.html", {"form": form, "cliente": vehiculo})


def salir (request):
   
    logout(request)
    return redirect('login')


@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def email(request,id_cliente):
    cliente = get_object_or_404(Cliente, id=id_cliente)
    contact_form = ContactForm(initial={'email': cliente.email})
    
    if request.method == 'POST':
        contact_form= ContactForm(data=request.POST)

        if contact_form.is_valid():
            name= request.POST.get('name','')
            email=request.POST.get('email','')
            message=request.POST.get('menssage','')

            email=EmailMessage(
                'Mensaje de conctaco recibido',
                'Mensaje enviado por {} <{}>:\n\n{}'.format(name,email,message),
                email,
                ['6f74157198b5d8@inbox.mailtrap.io'],
                reply_to=[email],
            )
            try:
                email.send()
                return redirect(reverse('email', args=[id_cliente]) + '?ok')
            except:
                return redirect(reverse('email')+'?error')
    return render(request, 'core/email.html',{
        'form':contact_form
    })


#---------------edit Reparaciones elimiar Reparaciones

@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def deleteR(request,id_reparaciones):
    pass
    try:
            # Busca el vehículo por su ID
            vehiculo_obj = Reparacion.objects.get(id=id_reparaciones)
            vehiculo_obj.delete()  # Elimina el objeto
            return redirect('gestionarReparaciones')  # Redirige a la gestión de vehículos
    except Vehiculo.DoesNotExist:
            # Manejo de error si no se encuentra el vehículo
            return render(request, 'core/error.html', {'error': 'Vehículo no encontrado'})

@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def editR(request,id_reparaciones):
    pass
    reparacion = get_object_or_404(Reparacion, id=id_reparaciones)

    if request.method == 'POST':
        form = ReparacionForm(request.POST, instance=reparacion)

        if form.is_valid():
                form.save()  # Guarda los cambios en la base de datos
                return redirect('gestionarReparaciones')  # Redirige a la vista de gestión de clientes
    else:
        # Si es una solicitud GET, muestra el formulario prellenado
        form = ReparacionForm(instance=reparacion)

    return render(request, 'core/ReparacionesEdit.html',{
        'form':form
    })

#----------------edit ot eliminar ot 
@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def editOt(request,id_ot):

    ot=get_object_or_404(OrdenTrabajo,id=id_ot)

    if request.method=='POST':
        form = OtForm(request.POST, instance=ot)
        if form.is_valid():
                form.save()  # Guarda los cambios en la base de datos
                return redirect('gestionarOrdenTrabjos')
    else:
       
        form = OtForm(instance=ot)
    return render (request, 'core/otEdit.html',{
        'form':form
    })
    


@user_passes_test(is_secretaria, login_url='/')
@login_required(login_url='/')
def eliminarOT(reuqest,id_ot):
    pass
    OrdenT = get_object_or_404(OrdenTrabajo, pk=id_ot)  # Síncrono
    OrdenT.delete()  # Síncrono
    return redirect('gestionarOrdenTrabjos')

