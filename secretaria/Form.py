from django import forms
from .models import Cliente,Vehiculo,Reparacion,OrdenTrabajo
from django.core.exceptions import ValidationError
import re
from datetime import datetime

class FormularioCliente(forms.ModelForm):
    COMUNAS = [
        ('penco', 'Penco'), 
        ('talcahuano', 'Talcahuano'),
        ('chiguayante', 'Chiguayante'),
        ('San Pedro', 'San Pedro'),
        ('hualpen', 'Hualpen'),
        ('Tomé', 'Tomé'),
        ('Concepción', 'Concepción'),
        ('Coronel', 'Coronel'),
        ('Lota', 'Lota'),
        ('Arauco', 'Arauco'),

    ]

    comuna = forms.ChoiceField(choices=COMUNAS, label='Comuna', widget=forms.Select)
    
    
    class Meta:
        model = Cliente
        # Excluimos el campo 'id' ya que no debe ser modificado
        fields = ['rut', 'nombres', 'apellidos', 'telefono', 'email', 'direccion', 'comuna']
        labels = {
            'rut': 'RUT',
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'telefono': 'Teléfono',
            'email':'Email',
            'direccion': 'Dirección',
            'comuna': 'Comuna'
        }
        widgets = {
            'rut': forms.TextInput(attrs={
                'placeholder': 'Ingrese su RUT. Ejemplo: 12345678-9'
            }),
            'nombres': forms.TextInput(attrs={
                'placeholder': 'Ingrese sus nombres. Ejemplo: Juan Andrés'
            }),
            'apellidos': forms.TextInput(attrs={
                'placeholder': 'Ingrese sus apellidos. Ejemplo: Pérez López'
            }),
            'telefono': forms.TextInput(attrs={
                'placeholder': 'Ingrese su teléfono. Ejemplo: 912345678'
            }),
            'email': forms.TextInput(attrs={
                'placeholder': 'Ingrese su Email. Ejemplo: alfonso@gmail.com'
            }),
            'direccion': forms.TextInput(attrs={
                'placeholder': 'Ingrese su dirección. Ejemplo: Calle 123, Comuna'
            }),
        } 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Si el formulario es para editar un cliente existente
            self.fields['rut'].widget.attrs.update({'readonly': 'readonly'})

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')

        # Verifica que el formato sea válido usando una expresión regular
        if not re.match(r'^\d{7,8}-[0-9kK]$', rut):
            raise ValidationError("El RUT ingresado no tiene un formato válido. Ejemplo: 12345678-9")
        
         # Verificar si todos los números del RUT son iguales
        numeros, dv = rut.split('-')
        if len(set(numeros)) == 1:  # Comprueba si todos los dígitos en "numeros" son iguales
            raise ValidationError("El RUT ingresado no es válido: contiene todos los dígitos iguales.")

        # Valida el dígito verificador
        if not self.validar_digito_verificador(rut):
            raise ValidationError("El RUT ingresado no es válido.")

        # Verifica si el RUT ya existe en la base de datos excluyendo al cliente actual
        if Cliente.objects.filter(rut=rut).exclude(id=self.instance.id).exists():
            raise ValidationError("El RUT ingresado ya está registrado.")

        return rut
    
    def validar_digito_verificador(self, rut):
        """Valida el dígito verificador del RUT chileno."""
        rut, dv = rut.split("-")
        rut = list(map(int, rut[::-1]))  # Invierte el RUT y convierte a entero
        factores = [2, 3, 4, 5, 6, 7]
        suma = sum(r * factores[i % 6] for i, r in enumerate(rut))
        dv_calculado = 11 - (suma % 11)
        dv_calculado = "0" if dv_calculado == 11 else "k" if dv_calculado == 10 else str(dv_calculado)
        return dv_calculado.lower() == dv.lower()
    
    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if not re.match(r'^[a-zA-Z0-9\s,.\-]{6,}$', direccion):
            raise ValidationError(
                "La dirección debe tener al menos 6 caracteres y solo puede incluir letras, números, espacios, comas (,), puntos (.) y guiones (-)."
            )
        return direccion




# formulario para vehiculos


from django import forms
from django.core.exceptions import ValidationError
import re
from datetime import datetime
from .models import Vehiculo

class FormularioVehiculo(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['patente', 'modelo', 'año', 'marca']
        labels = {
            'patente': 'Patente',
            'modelo': 'Modelo',
            'año': 'Año',
            'marca': 'Marca',
        }
        widgets = {
            'patente': forms.TextInput(attrs={
                'placeholder': 'Ingrese la patente. Ejemplo: ABC1234',
                'class': 'form-control'
            }),
            'modelo': forms.TextInput(attrs={
                'placeholder': 'Ingrese el modelo. Ejemplo: Corolla',
                'class': 'form-control'
            }),
            'año': forms.NumberInput(attrs={
                'placeholder': 'Ingrese el año. Ejemplo: 2020',
                'class': 'form-control'
            }),
            'marca': forms.TextInput(attrs={
                'placeholder': 'Ingrese la marca. Ejemplo: Toyota',
                'class': 'form-control'
            }),
        }

    def clean_patente(self):
        patente = self.cleaned_data.get('patente')

        # Validar formato de patente
        if not re.match(r'^[A-Z0-9]+$', patente):
            raise ValidationError("La patente solo puede contener letras mayúsculas y números.")

        # Verificar si la patente ya está registrada (excluyendo el vehículo actual)
        if Vehiculo.objects.filter(patente=patente).exclude(id=self.instance.id).exists():
            raise ValidationError("Esta patente ya está registrada.")
        
        return patente

    def clean_año(self):
        año = self.cleaned_data.get('año')
        
        # Validar rango de años
        if año < 1900 or año > datetime.now().year:
            raise ValidationError("El año debe estar entre 1900 y el año actual.")
        
        return año



class ContactForm(forms.Form):
    name = forms.CharField(
        label="Nombre y apellido",
        required=True,
        min_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Agregue sus datos"
        })
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Correo"
        })
    )

    message = forms.CharField(
        label="Mensaje",
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': "Introduzca un mensaje",
            
        })
    )


class ReparacionForm(forms.ModelForm):  # Cambiado a ModelForm
    class Meta:  
        model = Reparacion  
        fields = ['nombre', 'precio', 'descripcion']
        labels = {
            'nombre': 'Nombre',
            'precio': 'Precio',
            'descripcion': 'Descripción'
        }

class OtForm(forms.ModelForm):
    class Meta:
        model=OrdenTrabajo
        fields=['fecha_inicio','fecha_entrega','observacion']
        labels={
            'fecha_inicio':'Fecha inicio',
            'fecha_entrega':'Fecha entrega',
            'observacion':'observacion'
        }