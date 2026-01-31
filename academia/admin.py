from django.contrib import admin
from .models import Alumna, Cuota

@admin.register(Alumna)
class AlumnaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'telefono', 'fecha_registro')
    search_fields = ('nombre', 'apellido')

@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ('alumna', 'mes', 'anio', 'monto', 'pagado', 'fecha_pago')
    list_filter = ('pagado', 'mes', 'anio') # Filtros laterales mágicos
    list_editable = ('pagado',) # Permite marcar como pagado sin entrar al registro
    search_fields = ('alumna__nombre', 'alumna__apellido')