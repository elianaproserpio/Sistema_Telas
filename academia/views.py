from django.shortcuts import render, redirect, get_object_or_404
from .models import Alumna, Cuota
from .forms import AlumnaForm, CuotaForm, CuotaEditForm
from django.contrib import messages
from django.db import IntegrityError


def buscar_alumna(request):
    """Vista principal - busca y muestra alumnas con sus cuotas"""
    query = request.GET.get('q', '').strip()
    resultado = None
    cuotas = None

    if query:
        # Dividir la búsqueda para permitir "nombre apellido"
        palabras = query.split()
        
        # Buscar por nombre completo o parcial
        if len(palabras) >= 2:
            # Si hay 2 o más palabras, buscar por nombre Y apellido
            resultado = Alumna.objects.filter(
                nombre__icontains=palabras[0],
                apellido__icontains=palabras[1]
            ).first()
            
            # Si no encuentra con ese orden, intentar invertido
            if not resultado:
                resultado = Alumna.objects.filter(
                    nombre__icontains=palabras[1],
                    apellido__icontains=palabras[0]
                ).first()
        else:
            # Si es una sola palabra, buscar en nombre o apellido
            resultado = Alumna.objects.filter(
                nombre__icontains=query
            ).first()
            
            if not resultado:
                resultado = Alumna.objects.filter(
                    apellido__icontains=query
                ).first()
        
        if resultado:
            # Traemos todas sus cuotas ordenadas por mes descendente
            cuotas = Cuota.objects.filter(alumna=resultado).order_by('-anio', '-mes')

    return render(request, 'academia/inicio.html', {
        'alumna': resultado,
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
        initial_data = {}
        if alumna_preseleccionada:
            initial_data['alumna'] = alumna_preseleccionada
        form = CuotaForm(initial=initial_data)
    
    return render(request, 'academia/formulario.html', {
        'form': form,
        'titulo': '💰 Registrar Pago',
        'alumna_preseleccionada': alumna_preseleccionada
    })


def listar_alumnas(request):
    """Lista todas las alumnas registradas agrupadas por turno"""
    # Obtener todos los turnos disponibles
    turnos_choices = Alumna._meta.get_field('turno').choices
    
    # Agrupar alumnas por turno
    alumnas_por_turno = {}
    for turno_code, turno_display in turnos_choices:
        alumnas = Alumna.objects.filter(turno=turno_code).order_by('nombre', 'apellido')
        if alumnas.exists():
            alumnas_por_turno[turno_display] = alumnas
    
    # También incluir alumnas sin turno
    sin_turno = Alumna.objects.filter(turno='').order_by('nombre', 'apellido')
    if sin_turno.exists():
        alumnas_por_turno['Sin turno especificado'] = sin_turno
    
    return render(request, 'academia/listar_alumnas.html', {
        'alumnas_por_turno': alumnas_por_turno,
        'total_alumnas': Alumna.objects.count()
    })


def gestionar_pagos(request):
    """Vista para gestionar pagos de alumnas por turno"""
    from datetime import datetime
    
    turnos_choices = Alumna._meta.get_field('turno').choices
    mes_actual = datetime.now().month
    anio_actual = datetime.now().year
    
    # Obtener mes/año seleccionados (por defecto, mes actual)
    mes_seleccionado = int(request.GET.get('mes', mes_actual))
    anio_seleccionado = int(request.GET.get('anio', anio_actual))
    
    pagos_por_turno = {}
    estadisticas = {
        'total_pagado_mes': 0,
        'total_alumnas': Alumna.objects.count()
    }
    
    for turno_code, turno_display in turnos_choices:
        alumnas = Alumna.objects.filter(turno=turno_code).order_by('nombre', 'apellido')
        if alumnas.exists():
            alumnas_con_cuota = []
            for alumna in alumnas:
                # Obtener cuota del mes seleccionado
                try:
                    cuota_mes_seleccionado = Cuota.objects.get(alumna=alumna, mes=mes_seleccionado, anio=anio_seleccionado)
                except Cuota.DoesNotExist:
                    cuota_mes_seleccionado = None
                
                alumnas_con_cuota.append({
                    'alumna': alumna,
                    'cuota_mes_seleccionado': cuota_mes_seleccionado,
                })
                
                # Estadísticas del mes seleccionado (solo pagados)
                if cuota_mes_seleccionado and cuota_mes_seleccionado.pagado:
                    estadisticas['total_pagado_mes'] += cuota_mes_seleccionado.monto
            
            pagos_por_turno[turno_display] = alumnas_con_cuota
    
    # También incluir alumnas sin turno
    sin_turno = Alumna.objects.filter(turno='').order_by('nombre', 'apellido')
    if sin_turno.exists():
        alumnas_con_cuota = []
        for alumna in sin_turno:
            try:
                cuota_mes_seleccionado = Cuota.objects.get(alumna=alumna, mes=mes_seleccionado, anio=anio_seleccionado)
            except Cuota.DoesNotExist:
                cuota_mes_seleccionado = None
            
            alumnas_con_cuota.append({
                'alumna': alumna,
                'cuota_mes_seleccionado': cuota_mes_seleccionado,
            })
            
            if cuota_mes_seleccionado and cuota_mes_seleccionado.pagado:
                estadisticas['total_pagado_mes'] += cuota_mes_seleccionado.monto
        
        pagos_por_turno['Sin turno especificado'] = alumnas_con_cuota
    
    # Generar lista de meses para el selector
    meses = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre'),
    ]
    
    # Generar lista de años (últimos 3 años + próximo año)
    anios = list(range(anio_actual - 2, anio_actual + 2))
    
    return render(request, 'academia/gestionar_pagos.html', {
        'pagos_por_turno': pagos_por_turno,
        'estadisticas': estadisticas,
        'mes_seleccionado': mes_seleccionado,
        'anio_seleccionado': anio_seleccionado,
        'meses': meses,
        'anios': anios,
        'mes_actual': mes_actual,
        'anio_actual': anio_actual
    })