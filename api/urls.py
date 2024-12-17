"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# api/urls.py
from django.contrib import admin
from django.urls import path, include
from secretaria import views
from mecanico import views as mc
from login import views as lg
from jefe import views as jefe_views

urlpatterns = [


    
    path('crearCliente/', views.crearCliente, name='crearCliente'),

    path('otmecanico/<int:ot_id>/', mc.otmecanico, name='otmecanico'),

    path('crearOrdenTrabajos/', views.crearOT, name='crearOT'),
    path('crearReparaciones/', views.crearReparaciones, name='crearReparaciones'),
    path('crearVehiculos/', views.crearV, name='crearVehiculos'),

    path('gestionarClientes/', views.gestionarC, name='gestionarC'),
    path('validar-rut/', views.validar_rut, name='validar_rut'),

    path('eliminarClientes/<int:id_cliente>', views.deleteCl, name='deleteCl'),
    path('eliminarVehiculos/<int:id_vehiculo>',views.deleteVC, name='deleteVC'),
    
    path('gestionarOrdenTrabajos/', views.gestionarOT, name='gestionarOrdenTrabjos'),
    path('gestionarVehiculos/', views.gestionarV, name='gestionarVehiculos'),
    path('gestionarReparaciones/', views.gestionarReparaciones, name='gestionarReparaciones'),
    path('mecanico/', mc.mecanico, name='mecanico'),

    path('editarCliente/<int:id_cliente>/', views.edit, name='editarCliente'),
    path('editarVehiculo/<int:id_vehiculo>/', views.editV, name='editarVehiculo'),

    path('editarOT/<int:id_ot>', views.editOt, name='editarOt'),

    path('eliminarOT/<int:id_ot>/',views.eliminarOT, name="deleteOT"),

    #path('jefe/', include('jefe.urls', namespace='jefe')),  # Asegúrate de incluir el espacio de nombres

    path('', lg.login_view, name="login"),
    path('salir/',mc.salir, name="salir"),


    path('informe/', jefe_views.informe, name="informe"),
    path('informe/pdf/', jefe_views.generar_pdf, name='generar_pdf'),  # Ruta para generar el PDF
    path('gestionar-usuarios/', jefe_views.gestionar_usuarios, name='gestionar_usuarios'),
    path('editar-usuario/<int:user_id>/', jefe_views.editar_usuario, name='editar_usuario'),
    path('cambiar-estado-usuario/<int:user_id>/', jefe_views.cambiar_estado_usuario, name='cambiar_estado_usuario'),

    


    


    path('editarReparacion/<int:id_reparaciones>/', views.editR, name="editarReparaciones"),
    path('eliminarReparacion/<int:id_reparaciones>/', views.deleteR, name="eliminarReparacion"),
    path('admin/', admin.site.urls),


    path('email/<int:id_cliente>/',views.email, name="email")
]
