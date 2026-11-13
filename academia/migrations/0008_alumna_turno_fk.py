from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Paso 3/3: elimina la columna de texto vieja y deja la nueva como `turno`."""

    dependencies = [
        ('academia', '0007_copiar_turnos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alumna',
            name='turno',
        ),
        migrations.RenameField(
            model_name='alumna',
            old_name='turno_ref',
            new_name='turno',
        ),
        migrations.AlterField(
            model_name='alumna',
            name='turno',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alumnas', to='academia.turno'),
        ),
    ]
