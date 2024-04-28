from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from medicos.models import Especialidade, Medico, is_medico


@login_required
def home(request):
    template_name = 'home.html'
    # medicos = Medico.objects.exclude(user=request.user)
    medicos = Medico.objects.all()
    especialidades = Especialidade.objects.all()
    
    medico_filtrar = request.GET.get('medico')
    especialidades_filtrar = request.GET.getlist('especialidades')

    # consultas_usuario = Consulta.objects.filter(paciente=request.user)
    # consultas_agendadas = consultas_usuario.filter(data_aberta__data__gte=datetime.now()).filter(status='A')

    if medico_filtrar:
        medicos = medicos.filter(nome__icontains = medico_filtrar)

    if especialidades_filtrar:
        medicos = medicos.filter(especialidade_id__in=especialidades_filtrar)

    context = {
        'medicos': medicos,
        'especialidades': especialidades,
        # 'consultas_agendadas': consultas_agendadas,
        'is_medico': is_medico(request.user)
    }

    return render(request, template_name, context)
