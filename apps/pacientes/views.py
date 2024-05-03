from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse
from plataforma.models import Pessoa, is_medico
from medicos.models import DatasAbertas
from .models import Consulta


@login_required
def agendar_horario(request, id_medico):
    template_name = 'agendar_horario.html'
    if request.method == "GET":
        paciente = Pessoa.objects.get(user=request.user)
        medico = Pessoa.objects.get(user=id_medico)
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendada=False)

        context = {
            'paciente': paciente, 
            'legenda': 'Agende sua consulta',
            'medico': medico, 
            'datas_abertas': datas_abertas,
            'is_medico': is_medico(request.user)
        }

        return render(request, template_name, context)


@login_required
def escolher_horario(request, id_data_aberta):
    if request.method == "GET":
        data_aberta = get_object_or_404(DatasAbertas, id=id_data_aberta)
        medico_id = request.META['HTTP_REFERER'][-2]

        if data_aberta.user.id != int(medico_id):
            messages.add_message(request, messages.ERROR, 'O Horário pretendido não pertence ao médico escolhido.')

            return redirect(f'/pacientes/agendar-horario/{medico_id}')

        horario_agendado = Consulta(
            paciente=request.user,
            data_aberta=data_aberta
        )

        with transaction.atomic():
            horario_agendado.save()

            data_aberta.agendada = True  # trocando para agendado ocorre erro
            data_aberta.save()

            messages.add_message(request, messages.SUCCESS, 'Horário agendado com sucesso.')

            return redirect(reverse('minhas_consultas'))

        #TODO: Implementar msg caso não comitada


@login_required
def minhas_consultas(request):
    template_name = 'minhas_consultas.html'
    if request.method == "GET":
        status_consulta = Consulta.status_choices
        # minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        paciente = Pessoa.objects.get(user=request.user)
        minhas_consultas = Consulta.objects.filter(paciente=paciente.user)

        context = {
            'paciente': paciente, 
            'legenda': 'Veja suas consultas',
            'status_consulta': status_consulta, 
            'minhas_consultas': minhas_consultas,
            'is_medico': is_medico(request.user)
        }

        medico_filter = request.GET.get('medico')
        status_filter = request.GET.get('status')
        data_filter = request.GET.get('data')

        if medico_filter:
            context['medico_filter'] = medico_filter
            minhas_consultas = minhas_consultas.filter(data_aberta__user__username__icontains=medico_filter)
            context['minhas_consultas'] = minhas_consultas

        if status_filter:
            context['status_filter'] = status_filter
            minhas_consultas = minhas_consultas.filter(status=status_filter)
            context['minhas_consultas'] = minhas_consultas
            
        if data_filter:
            context['data_filter'] = data_filter
            minhas_consultas = minhas_consultas.filter(data_aberta__data__icontains=data_filter)
            context['minhas_consultas'] = minhas_consultas

        return render(request, template_name, context)


@login_required
def consulta(request, id_consulta):
    template_name = 'consulta.html'
    if request.method == 'GET':
        paciente = Pessoa.objects.get(user=request.user)
        consulta = get_object_or_404(Consulta, id=id_consulta)
        if consulta.paciente != request.user:
            messages.add_message(
                request, 
                messages.ERROR, 
                'A consulta que você tentou acessar não lhe pertence !'
            )
            return redirect(reverse('minhas_consultas')) 
        
        status_consulta = Consulta.status_choices
        dado_medico = Pessoa.objects.get(user=consulta.data_aberta.user)
        # documentos = Documento.objects.filter(consulta=consulta)

        context = {
            'paciente': paciente, 
            'legenda': 'Veja sua consulta detalhada',
            'consulta': consulta, 
            'status_consulta': status_consulta, 
            'dado_medico': dado_medico, 
            # 'documentos': documentos, 
            'is_medico': is_medico(request.user)
        }

        return render(request, template_name, context)


@login_required
def cancelar_consulta(request, id_consulta):
    consulta = get_object_or_404(Consulta, id=id_consulta)
    if consulta.paciente != request.user:
        messages.add_message(
            request, 
            messages.ERROR, 
            'A consulta que você tentou cancelar não lhe pertence !'
        )
        return redirect(reverse('minhas_consultas')) 
    
    if consulta.status != 'A':
        messages.add_message(
            request, 
            messages.ERROR, 
            'Esta consulta não pode mais ser cancelada !'
        )
        return redirect(reverse('minhas_consultas')) 
    
    data_aberta = DatasAbertas.objects.get(id=consulta.data_aberta.id)

    with transaction.atomic():
        try:
            consulta.status = 'C'
            consulta.save()
            data_aberta.agendada = False
            data_aberta.save()
            messages.add_message(
                request, 
                messages.SUCCESS, 
                f'Consulta cancelada com sucesso !'
            )
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e} !')

        return redirect(reverse('minhas_consultas')) 

#TODO: Consultar medicamentos semelhantes via api anvisa
