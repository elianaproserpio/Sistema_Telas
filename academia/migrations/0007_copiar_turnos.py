from django.db import migrations


# Los turnos que antes estaban fijos en el código (models.Alumna.TURNOS).
TURNOS_ANTERIORES = [
    ('lunes_1', 'Lunes y Miércoles 18:30 a 19:30'),
    ('lunes_2', 'Lunes y Miércoles 19:30 a 21:00'),
    ('martes_1', 'Martes y Jueves 17:30 a 19:00'),
    ('martes_2', 'Martes y Jueves 19:00 a 20:30'),
]


def copiar_turnos(apps, schema_editor):
    """Paso 2/3: crea los turnos existentes y le asigna a cada alumna el suyo."""
    Turno = apps.get_model('academia', 'Turno')
    Alumna = apps.get_model('academia', 'Alumna')

    turno_por_codigo = {}
    for orden, (codigo, nombre) in enumerate(TURNOS_ANTERIORES, start=1):
        turno, _ = Turno.objects.get_or_create(nombre=nombre, defaults={'orden': orden})
        turno_por_codigo[codigo] = turno

    for alumna in Alumna.objects.exclude(turno=''):
        turno = turno_por_codigo.get(alumna.turno)
        if turno is None:
            # Código desconocido: se crea un turno con ese texto para no perder el dato.
            turno, _ = Turno.objects.get_or_create(
                nombre=alumna.turno[:100], defaults={'orden': len(turno_por_codigo) + 1}
            )
            turno_por_codigo[alumna.turno] = turno
        alumna.turno_ref = turno
        alumna.save(update_fields=['turno_ref'])


def revertir(apps, schema_editor):
    """Permite volver atrás: copia el turno al campo de texto anterior."""
    Alumna = apps.get_model('academia', 'Alumna')
    codigo_por_nombre = {nombre: codigo for codigo, nombre in TURNOS_ANTERIORES}
    for alumna in Alumna.objects.exclude(turno_ref=None).select_related('turno_ref'):
        nombre = alumna.turno_ref.nombre
        alumna.turno = codigo_por_nombre.get(nombre, nombre[:50])
        alumna.save(update_fields=['turno'])


class Migration(migrations.Migration):

    dependencies = [
        ('academia', '0006_turno'),
    ]

    operations = [
        migrations.RunPython(copiar_turnos, revertir),
    ]
