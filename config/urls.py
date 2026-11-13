from django.contrib import admin
from django.urls import path
from academia.views import (
    buscar_alumna, 
    registrar_alumna, 
    editar_alumna,
    editar_cuota,
    eliminar_cuota,
    eliminar_alumna,
    cargar_cuota,
    listar_alumnas,
    gestionar_pagos,
    listar_turnos,
    crear_turno,
    editar_turno,
    cambiar_estado_turno,
    eliminar_turno,
    marcar_pagado,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', buscar_alumna, name='buscar'),
    path('alumnas/', listar_alumnas, name='listar_alumnas'),
    path('pagos/', gestionar_pagos, name='gestionar_pagos'),
    path('registrar-alumna/', registrar_alumna, name='registrar_alumna'),
    path('editar-alumna/<int:id>/', editar_alumna, name='editar_alumna'),
    path('editar-cuota/<int:id>/', editar_cuota, name='editar_cuota'),
    path('eliminar-cuota/<int:id>/', eliminar_cuota, name='eliminar_cuota'),
    path('eliminar-alumna/<int:id>/', eliminar_alumna, name='eliminar_alumna'),
    path('cargar-cuota/', cargar_cuota, name='cargar_cuota'),
    path('turnos/', listar_turnos, name='listar_turnos'),
    path('turnos/nuevo/', crear_turno, name='crear_turno'),
    path('turnos/<int:id>/editar/', editar_turno, name='editar_turno'),
    path('turnos/<int:id>/estado/', cambiar_estado_turno, name='cambiar_estado_turno'),
    path('turnos/<int:id>/eliminar/', eliminar_turno, name='eliminar_turno'),
    path('pagos/marcar/', marcar_pagado, name='marcar_pagado'),
]