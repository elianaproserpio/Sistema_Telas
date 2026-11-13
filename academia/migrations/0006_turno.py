from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Paso 1/3: crea la tabla de turnos y una columna nueva (vacía) en Alumna."""

    dependencies = [
        ('academia', '0005_cuota_metodo_pago_alter_alumna_turno'),
    ]

    operations = [
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('orden', models.PositiveIntegerField(default=0, help_text='Los turnos se muestran de menor a mayor según este número.')),
                ('activo', models.BooleanField(default=True, help_text='Si está desactivado, no aparece para asignar a nuevas alumnas.')),
            ],
            options={
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.AddField(
            model_name='alumna',
            name='turno_ref',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='academia.turno'),
        ),
    ]
