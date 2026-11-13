import unicodedata
from datetime import date
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from .models import Alumna, Cuota, Turno, MESES
from .forms import AlumnaForm, CuotaForm, CuotaEditForm, TurnoForm
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Count
from django.urls import reverse
from django.views.decorators.http import require_POST


def normalizar(texto):
    """Pasa a minúsculas y quita tildes, para buscar 'rodriguez' y encontrar 'Rodríguez'."""
    texto = unicodedata.normalize('NFD', texto or '')
    return ''.join(c for c in texto if unicodedata.category(c) != 'Mn').lower()


def buscar_alumnas(query):
    """Devuelve todas las alumnas cuyo nombre + apellido contienen todas las palabras buscadas."""
    palabras = normalizar(query).split()
    if not palabras:
        return []
    coincidencias = []
    for alumna in Alumna.objects.select_related('turno').order_by('nombre', 'apellido'):
        texto = normalizar(f'{alumna.nombre} {alumna.apellido}')
        if all(p in texto for p in palabras):
            coincidencias.append(alumna)
    return coincidencias


def buscar_alumna(request):
    """Vista principal - busca alumnas y muestra una con sus cuotas"""
    query = request.GET.get('q', '').strip()
    alumna_id = request.GET.get('id', '')
    resultado = None
    resultados = []
    cuotas = None

    if alumna_id.isdigit():
        # Se eligió una alumna de la lista de resultados
        resultado = Alumna.objects.filter(id=alumna_id).first()
    elif query:
        resultados = buscar_alumnas(query)
        if len(resultados) == 1:
            resultado = resultados[0]
            resultados = []

    if resultado:
        # Traemos todas sus cuotas ordenadas por mes descendente
        cuotas = Cuota.objects.filter(alumna=resultado).order_by('-anio', '-mes')

    return render(request, 'academia/inicio.html', {
        'alumna': resultado,
        'resultados': resultados,
        'cuotas': cuotas,
        'query': query
    })


def registrar_alumna(request):
    """Registra una nueva alumna"""
    if request.method == 'POST':
        form = AlumnaForm(request.POST)
        if form.is_valid():
            alumna = form.save()
            messages.success(request, f'✅ Alumna {alumna.nombre} registrada correctamente.')
            return redirect('buscar')
    else:
        form = AlumnaForm()
    
    return render(request, 'academia/formulario.html', {
        'form': form,
        'titulo': '➕ Nueva Alumna'
    })


def editar_alumna(request, id):
    """Edita los datos de una alumna y sus cuotas"""
    alumna = get_object_or_404(Alumna, id=id)
    cuotas = Cuota.objects.filter(alumna=alumna).order_by('-anio', '-mes')
    
    if request.method == 'POST':
        form = AlumnaForm(request.POST, instance=alumna)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Alumna {alumna.nombre} actualizada correctamente.')
            return redirect('buscar')
    else:
        form = AlumnaForm(instance=alumna)
    
    return render(request, 'academia/editar_alumna.html', {
        'form': form,
        'alumna': alumna,
        'cuotas': cuotas,
        'titulo': f'✏️ Editar - {alumna.nombre}'
    })


def editar_cuota(request, id):
    """Edita una cuota de pago específica"""
    cuota = get_object_or_404(Cuota, id=id)
    
    if request.method == 'POST':
        form = CuotaEditForm(request.POST, instance=cuota)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Cuota actualizada correctamente.')
            return redirect('editar_alumna', id=cuota.alumna.id)
    else:
        form = CuotaEditForm(instance=cuota)
    
    return render(request, 'academia/formulario.html', {
        'form': form,
        'titulo': f'💰 Editar Cuota - {cuota.alumna.nombre}'
    })


def eliminar_cuota(request, id):
    """Elimina una cuota de pago"""
    cuota = get_object_or_404(Cuota, id=id)
    alumna_id = cuota.alumna.id
    
    if request.method == 'POST':
        cuota.delete()
        messages.success(request, f'✅ Cuota de {cuota.get_mes_display()} eliminada.')
        return redirect('editar_alumna', id=alumna_id)
    
    return render(request, 'academia/confirmar_eliminar_cuota.html', {
        'cuota': cuota
    })


def eliminar_alumna(request, id):
    """Elimina una alumna y todas sus cuotas"""
    alumna = get_object_or_404(Alumna, id=id)
    
    if request.method == 'POST':
        nombre = alumna.nombre
        alumna.delete()
        messages.success(request, f'✅ Alumna {nombre} eliminada correctamente.')
        return redirect('buscar')
    
    return render(request, 'academia/confirmar_eliminar.html', {
        'alumna': alumna
    })


def cargar_cuota(request):
    """Registra una nueva cuota de pago"""
    alumna_id = request.GET.get('alumna_id', None)
    alumna_preseleccionada = None
    
    if alumna_id:
        try:
            alumna_preseleccionada = Alumna.objects.get(id=alumna_id)
        except Alumna.DoesNotExist:
            alumna_preseleccionada = None
    
    if request.method == 'POST':
        form = CuotaForm(request.POST)
        if form.is_valid():
            try:
                cuota = form.save()
                messages.success(request, f'✅ Cuota de {cuota.alumna.nombre} registrada correctamente.')
                return redirect('editar_alumna', id=cuota.alumna.id)
            except IntegrityError:
                form.add_error(None, '❌ Esta alumna ya tiene registrada una cuota para ese mes y año. Edita la existente para cambiar el estado a Pagado.')
    else:
        # Por defecto: mes y año actuales (o los que vienen desde Gestionar Pagos)
        hoy = date.today()
        mes = entero(request.GET.get('mes'), hoy.month, 1, 12)
        anio = entero(request.GET.get('anio'), hoy.year, 2000, 2100)
        initial_data = {'mes': mes, 'anio': anio}
        if alumna_preseleccionada:
            initial_data['alumna'] = alumna_preseleccionada
        form = CuotaForm(initial=initial_data)

    return render(request, 'academia/formulario.html', {
        'form': form,
        'titulo': '💰 Registrar Pago',
        'alumna_preseleccionada': alumna_preseleccionada,
    })


def entero(valor, por_defecto, minimo, maximo):
    """Convierte un parámetro de la URL a número, con un valor por defecto si viene mal."""
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return por_defecto
    return numero if minimo <= numero <= maximo else por_defecto


def listar_alumnas(request):
    """Lista todas las alumnas registradas agrupadas por turno"""
    # Agrupar alumnas por turno (en el orden definido en la pantalla de Turnos)
    alumnas_por_turno = {}
    for turno in Turno.objects.all():
        alumnas = Alumna.objects.filter(turno=turno).order_by('nombre', 'apellido')
        if alumnas.exists():
            alumnas_por_turno[turno.nombre] = alumnas

    # También incluir alumnas sin turno
    sin_turno = Alumna.objects.filter(turno__isnull=True).order_by('nombre', 'apellido')
    if sin_turno.exists():
        alumnas_por_turno['Sin turno especificado'] = sin_turno
    
    return render(request, 'academia/listar_alumnas.html', {
        'alumnas_por_turno': alumnas_por_turno,
        'total_alumnas': Alumna.objects.count()
    })


def gestionar_pagos(request):
    """Vista para gestionar pagos de alumnas por turno"""
    hoy = date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year
    
    # Obtener mes/año seleccionados (por defecto, mes actual)
    mes_seleccionado = entero(request.GET.get('mes'), mes_actual, 1, 12)
    anio_seleccionado = entero(request.GET.get('anio'), anio_actual, 2000, 2100)

    # Todas las cuotas del mes en una sola consulta
    cuotas_del_mes = {
        c.alumna_id: c
        for c in Cuota.objects.filter(mes=mes_seleccionado, anio=anio_seleccionado)
    }

    pagos_por_turno = {}
    estadisticas = {
        'total_pagado_mes': 0,
        'pagadas': 0,
        'pendientes': 0,
        'total_alumnas': Alumna.objects.count()
    }

    def armar_lista(alumnas):
        lista = []
        for alumna in alumnas:
            cuota = cuotas_del_mes.get(alumna.id)
            lista.append({'alumna': alumna, 'cuota_mes_seleccionado': cuota})
            if cuota and cuota.pagado:
                estadisticas['total_pagado_mes'] += cuota.monto
                estadisticas['pagadas'] += 1
            else:
                estadisticas['pendientes'] += 1
        return lista

    alumnas_por_turno = {}
    for alumna in Alumna.objects.order_by('nombre', 'apellido'):
        alumnas_por_turno.setdefault(alumna.turno_id, []).append(alumna)

    for turno in Turno.objects.all():
        if turno.id in alumnas_por_turno:
            pagos_por_turno[turno.nombre] = armar_lista(alumnas_por_turno[turno.id])

    # También incluir alumnas sin turno
    if None in alumnas_por_turno:
        pagos_por_turno['Sin turno especificado'] = armar_lista(alumnas_por_turno[None])

    # Generar lista de años (últimos 3 años + próximo año)
    anios = list(range(anio_actual - 2, anio_actual + 2))
    if anio_seleccionado not in anios:
        anios.append(anio_seleccionado)
        anios.sort()

    return render(request, 'academia/gestionar_pagos.html', {
        'pagos_por_turno': pagos_por_turno,
        'estadisticas': estadisticas,
        'mes_seleccionado': mes_seleccionado,
        'mes_seleccionado_nombre': dict(MESES)[mes_seleccionado],
        'anio_seleccionado': anio_seleccionado,
        'meses': MESES,
        'anios': anios,
        'mes_actual': mes_actual,
        'anio_actual': anio_actual
    })


@require_POST
def marcar_pagado(request):
    """Marca como pagada (o deshace) la cuota de una alumna para un mes, desde Gestionar Pagos"""
    alumna = get_object_or_404(Alumna, id=request.POST.get('alumna_id'))
    hoy = date.today()
    mes = entero(request.POST.get('mes'), hoy.month, 1, 12)
    anio = entero(request.POST.get('anio'), hoy.year, 2000, 2100)
    accion = request.POST.get('accion', 'pagar')
    volver = f"{reverse('gestionar_pagos')}?mes={mes}&anio={anio}#alumna-{alumna.id}"
    nombre_mes = dict(MESES)[mes]

    cuota = Cuota.objects.filter(alumna=alumna, mes=mes, anio=anio).first()

    if accion == 'deshacer':
        if cuota and cuota.pagado:
            cuota.pagado = False
            cuota.fecha_pago = None
            cuota.save(update_fields=['pagado', 'fecha_pago'])
            messages.success(request, f'↩️ {alumna.nombre} {alumna.apellido}: {nombre_mes} volvió a pendiente.')
        return redirect(volver)

    metodo = request.POST.get('metodo')
    if metodo not in dict(Cuota.METODOS_PAGO):
        metodo = 'efectivo'

    # El monto lo escriben en la fila (cada alumna puede pagar distinto).
    # Si la cuota ya existe con monto y no escriben nada, se mantiene el que tenía.
    monto = None
    texto_monto = (request.POST.get('monto') or '').strip().replace('$', '').replace(' ', '')
    if texto_monto:
        # Acepta "25000", "25.000", "25000,50" y "25.000,50"
        if ',' in texto_monto:
            texto_monto = texto_monto.replace('.', '').replace(',', '.')
        elif texto_monto.count('.') == 1 and len(texto_monto.split('.')[1]) == 3:
            texto_monto = texto_monto.replace('.', '')
        try:
            monto = Decimal(texto_monto)
        except InvalidOperation:
            monto = None
        if monto is None or monto <= 0 or monto >= Decimal('100000000'):
            messages.error(request, f'❌ El monto "{request.POST.get("monto")}" no es válido.')
            return redirect(volver)

    if monto is None and not (cuota and cuota.monto):
        messages.error(
            request,
            f'❌ Escribí el monto que pagó {alumna.nombre} antes de tocar Efectivo o Transferencia.'
        )
        return redirect(volver)

    if cuota is None:
        cuota = Cuota(alumna=alumna, mes=mes, anio=anio)
    if monto is not None:
        cuota.monto = monto
    cuota.pagado = True
    cuota.metodo_pago = metodo
    cuota.fecha_pago = cuota.fecha_pago or hoy
    cuota.save()
    messages.success(
        request,
        f'✅ {alumna.nombre} {alumna.apellido}: {nombre_mes} pagado (${cuota.monto}, {cuota.get_metodo_pago_display()}).'
    )
    return redirect(volver)


# ---------------------------------------------------------------------------
# Gestión de turnos
# ---------------------------------------------------------------------------

def listar_turnos(request):
    """Lista los turnos con la cantidad de alumnas en cada uno"""
    turnos = Turno.objects.annotate(cantidad_alumnas=Count('alumnas'))
    return render(request, 'academia/listar_turnos.html', {
        'turnos': turnos,
        'sin_turno': Alumna.objects.filter(turno__isnull=True).count(),
    })


def crear_turno(request):
    """Crea un turno nuevo"""
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            turno = form.save()
            messages.success(request, f'✅ Turno "{turno.nombre}" creado correctamente.')
            return redirect('listar_turnos')
    else:
        siguiente_orden = (Turno.objects.order_by('-orden').values_list('orden', flat=True).first() or 0) + 1
        form = TurnoForm(initial={'orden': siguiente_orden, 'activo': True})

    return render(request, 'academia/formulario.html', {
        'form': form,
        'titulo': '⏰ Nuevo Turno',
        'volver_url': reverse('listar_turnos'),
    })


def editar_turno(request, id):
    """Edita el nombre, orden o estado de un turno"""
    turno = get_object_or_404(Turno, id=id)

    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Turno "{turno.nombre}" actualizado correctamente.')
            return redirect('listar_turnos')
    else:
        form = TurnoForm(instance=turno)

    return render(request, 'academia/formulario.html', {
        'form': form,
        'titulo': '✏️ Editar Turno',
        'volver_url': reverse('listar_turnos'),
    })


@require_POST
def cambiar_estado_turno(request, id):
    """Activa o desactiva un turno"""
    turno = get_object_or_404(Turno, id=id)
    turno.activo = not turno.activo
    turno.save(update_fields=['activo'])
    estado = 'activado' if turno.activo else 'desactivado'
    messages.success(request, f'✅ Turno "{turno.nombre}" {estado}.')
    return redirect('listar_turnos')


def eliminar_turno(request, id):
    """Elimina un turno, solo si no tiene alumnas asignadas"""
    turno = get_object_or_404(Turno, id=id)
    cantidad_alumnas = turno.alumnas.count()

    if request.method == 'POST' and cantidad_alumnas == 0:
        nombre = turno.nombre
        turno.delete()
        messages.success(request, f'✅ Turno "{nombre}" eliminado.')
        return redirect('listar_turnos')

    return render(request, 'academia/confirmar_eliminar_turno.html', {
        'turno': turno,
        'cantidad_alumnas': cantidad_alumnas,
    })
