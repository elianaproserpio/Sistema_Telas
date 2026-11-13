from django.contrib import admin
from .models import Alumna, Cuota, Turno

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden', 'activo')
    list_editable = ('orden', 'activo')

@admin.register(Alumna)
class AlumnaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'turno', 'telefono', 'fecha_registro')
    list_filter = ('turno',)
    search_fields = ('nombre', 'apellido')

@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ('alumna', 'mes', 'anio', 'monto', 'pagado', 'fecha_pago')
    list_filter = ('pagado', 'mes', 'anio') # Filtros laterales mágicos
    list_editable = ('pagado',) # Permite marcar como pagado sin entrar al registro
    search_fields = ('alumna__nombre', 'alumna__apellido')