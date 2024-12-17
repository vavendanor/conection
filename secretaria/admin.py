from django.contrib import admin
from .models import Cliente,Vehiculo,Reparacion,OrdenTrabajo

# Register your models here.


admin.site.register(OrdenTrabajo)
admin.site.register(Cliente)
admin.site.register(Vehiculo)
admin.site.register(Reparacion)