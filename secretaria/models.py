from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from datetime import datetime

# Create your models here.


# Modelo Cliente
class Cliente(models.Model):
    id = models.AutoField(primary_key=True)  # ID autoincrementable
    rut = models.CharField("RUT",
                            max_length=10,
                            unique=True,
                            validators=[RegexValidator(regex=r'^\d{7,8}-[0-9kK]$', message="RUT inválido")])
    
    nombres = models.CharField(max_length=12,
                                validators=[RegexValidator(regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', message="solo puede contener letras")])

    apellidos = models.CharField(max_length=15,
                                 validators=[RegexValidator(regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', message="solo puede contener letras")])

    telefono = models.CharField(max_length=9,
                                validators=[RegexValidator(regex=r'^\+?\d{7,15}$', message="Teléfono inválido")])
    
    email= models.EmailField(max_length=40)

    direccion = models.CharField(max_length=200,
                                  validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s.,-]+$',
            message="solo puede contener letras, números y los caracteres . , -")])

    comuna = models.CharField(max_length=20,
                              validators=[RegexValidator(regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', message="La comuna solo puede contener letras")])

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    
# Modelo Vehiculo
class Vehiculo(models.Model):
    id = models.AutoField(primary_key=True)  # ID autoincrementable
    patente = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[A-Z0-9]+$', message="solo puede contener letras mayúsculas y números")
        ]
    )

    modelo = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^[a-zA-Z0-9\s]+$', message="El modelo solo puede contener letras y números")]
    )

    marca = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^[a-zA-Z\s]+$', message="La marca solo puede contener letras")]
    )

    año = models.IntegerField(
        validators=[
            MinValueValidator(1900, message="El año debe ser mayor o igual a 1900"),
            MaxValueValidator(datetime.now().year, message="El año no puede ser mayor al actual")
        ]
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="vehiculos")



# Modelo Reparacion
class Reparacion(models.Model):
    id = models.AutoField(primary_key=True)  # ID autoincrementable
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    estado= models.BooleanField(default=False)

    def __str__(self):
        return self.nombre
    


# Modelo OrdenTrabajo
class OrdenTrabajo(models.Model):
    id = models.AutoField(primary_key=True)  # ID autoincrementable
    fecha_inicio = models.DateField()
    fecha_entrega = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=50)
    observacion = models.TextField()
    reparacion =  models.ManyToManyField(Reparacion)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Relación con el modelo User
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    def calcular_total(self):
        # Calcula el total de las reparaciones asociadas
        return sum(reparacion.precio for reparacion in self.reparacion.all())

    def __str__(self):
        return f"Orden {self.id} - {self.usuario.username if self.usuario else 'Sin Asignar'}"