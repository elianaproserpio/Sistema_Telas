from django import forms
from .models import Alumna, Cuota

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