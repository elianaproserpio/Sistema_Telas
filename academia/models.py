from django.db import models
from django.core.exceptions import ValidationError

class Alumna(models.Model):
    TURNOS = [
        ('lunes_1', 'Lunes y Miércoles 18:30 a 19:30'),
        ('lunes_2', 'Lunes y Miércoles 19:30 a 21:00'),
        ('martes_1', 'Martes y Jueves 17:30 a 19:00'),
        ('martes_2', 'Martes y Jueves 19:00 a 20:30'),
    ]
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    turno = models.CharField(max_length=50, choices=TURNOS, blank=True)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    def get_cuota_actual(self):
        """Obtiene la cuota más reciente (mes/año actual o más cercano)"""
        from datetime import datetime
        cuota_actual = self.cuotas.all().first()
        return cuota_actual


class Cuota(models.Model):
    MESES = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre'),
    ]
    
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
    ]
    
    alumna = models.ForeignKey(Alumna, on_delete=models.CASCADE, related_name='cuotas')
    mes = models.IntegerField(choices=MESES)
    anio = models.IntegerField(default=2026)
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='efectivo')

    class Meta:
        # Evitar duplicados: una alumna no puede tener más de una cuota por mes/año
        unique_together = ('alumna', 'mes', 'anio')
        ordering = ['-anio', '-mes']

    def __str__(self):
        return f"{self.alumna} - {self.get_mes_display()} {self.anio}"
    
    def clean(self):
        # Validación adicional
        if self.mes < 1 or self.mes > 12:
            raise ValidationError("El mes debe estar entre 1 y 12")