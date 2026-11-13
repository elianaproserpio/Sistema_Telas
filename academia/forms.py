from django import forms
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Alumna, Cuota, Turno

# Cambiamos ModelSerializer por ModelForm
class AlumnaForm(forms.ModelForm):
    class Meta:
        model = Alumna
        fields = ['nombre', 'apellido', 'turno', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre de la alumna'}),
            'apellido': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apellido'}),
            'turno': forms.Select(attrs={'class': 'form-input'}),
            'telefono': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Teléfono'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo turnos activos; si la alumna ya tiene uno desactivado, se lo mantiene en la lista
        filtro = Q(activo=True)
        if self.instance and self.instance.turno_id:
            filtro |= Q(pk=self.instance.turno_id)
        self.fields['turno'].queryset = Turno.objects.filter(filtro)
        self.fields['turno'].empty_label = 'Sin turno'


class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['nombre', 'orden', 'activo']
        labels = {
            'nombre': 'Nombre del turno',
            'orden': 'Orden',
            'activo': 'Turno activo',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Viernes 18:00 a 19:30'}),
            'orden': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class CuotaForm(forms.ModelForm):
    class Meta:
        model = Cuota
        fields = ['alumna', 'mes', 'anio', 'monto', 'metodo_pago', 'pagado', 'fecha_pago']
        # AGREGAMOS ESTO PARA LA Ñ
        labels = {
            'anio': 'Año',
            'metodo_pago': 'Método de pago',
            'pagado': '¿Está pagado?',
        }
        widgets = {
            'alumna': forms.Select(attrs={'class': 'form-input'}),
            'mes': forms.Select(attrs={'class': 'form-input'}),
            'anio': forms.NumberInput(attrs={'class': 'form-input', 'min': '2020'}),
            'monto': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0.00'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-input'}),
            'pagado': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'fecha_pago': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Alumnas en orden alfabético para encontrarlas más fácil
        self.fields['alumna'].queryset = Alumna.objects.order_by(Lower('nombre'), Lower('apellido'))
        self.fields['alumna'].empty_label = 'Elegí una alumna'

# Formulario para editar cuotas directamente
class CuotaEditForm(forms.ModelForm):
    class Meta:
        model = Cuota
        fields = ['mes', 'anio', 'monto', 'metodo_pago', 'pagado', 'fecha_pago']
        # TAMBIÉN AQUÍ PARA QUE AL EDITAR SE VEA BIEN
        labels = {
            'anio': 'Año',
            'metodo_pago': 'Método de pago',
        }
        widgets = {
            'mes': forms.Select(attrs={'class': 'form-input'}),
            'anio': forms.NumberInput(attrs={'class': 'form-input', 'min': '2020'}),
            'monto': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0.00'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-input'}),
            'pagado': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'fecha_pago': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }
