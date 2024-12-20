from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse
from plataforma.models import Pessoa, is_aprovado, is_medico
from medicos.models import DatasAbertas, Especialidade
from .models import Avaliacao, Consulta, Documento


@login_required
def agendar_horario(request, id_medico):
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_analise'))
    
    template_name = 'agendar_horario.html'
    if request.method == "GET":
        paciente = Pessoa.objects.get(user=request.user)
        medico = Pessoa.objects.get(user=id_medico)
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendada=False).order_by('data')

        context = {
            'paciente': paciente, 
            'legenda': 'Agende sua consulta',
            'medico': medico, 
            'datas_abertas': datas_abertas,
            'is_medico': is_medico(request.user),
            'is_aprovado': is_aprovado(request.user),
        }

        return render(request, template_name, context)


@login_required
def escolher_horario(request, id_data_aberta):
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_analise'))
    
    if request.method == "GET":
        data_aberta = get_object_or_404(DatasAbertas, id=id_data_aberta)
        medico_id = request.META['HTTP_REFERER'][-2]

        if data_aberta.user.id != int(medico_id):
            messages.add_message(request, messages.ERROR, 'O Horário pretendido não pertence ao médico escolhido.')

            return redirect(f'/pacientes/agendar-horario/{medico_id}')

        horario_agendado = Consulta(
            paciente= Pessoa.objects.get(user=request.user),
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
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_analise'))
    
    template_name = 'minhas_consultas.html'
    if request.method == "GET":
        status_consulta = Consulta.status_choices
        # minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        paciente = Pessoa.objects.get(user=request.user)
        minhas_consultas = Consulta.objects.filter(paciente=paciente)

        context = {
            'paciente': paciente, 
            'legenda': 'Veja suas consultas',
            'status_consulta': status_consulta, 
            'minhas_consultas': minhas_consultas,
            'is_medico': is_medico(request.user),
            'is_aprovado': is_aprovado(request.user),
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
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_analise'))
    
    template_name = 'consulta.html'
    if request.method == 'GET':
        paciente = Pessoa.objects.get(user=request.user)
        consulta = get_object_or_404(Consulta, id=id_consulta)
        avaliacao = Avaliacao.objects.filter(consulta=consulta)
        if avaliacao:
            avaliacao = avaliacao[0]

        if consulta.paciente != paciente:
            messages.add_message(
                request, 
                messages.ERROR, 
                'A consulta que você tentou acessar não lhe pertence !'
            )
            return redirect(reverse('minhas_consultas')) 
        
        status_consulta = Consulta.status_choices
        medico = Pessoa.objects.get(user=consulta.data_aberta.user)
        documentos = Documento.objects.filter(consulta=consulta)

        context = {
            'paciente': paciente, 
            'legenda': 'Veja sua consulta detalhada',
            'consulta': consulta, 
            'status_consulta': status_consulta, 
            'medico': medico, 
            'documentos': documentos, 
            'is_medico': is_medico(request.user),
            'is_aprovado': is_aprovado(request.user),
            'avaliacao': avaliacao
        }

        return render(request, template_name, context)


@login_required
def cancelar_consulta(request, id_consulta):
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_analise'))
    
    consulta = get_object_or_404(Consulta, id=id_consulta)
    if consulta.paciente != Pessoa.objects.get(user=request.user):
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


@login_required
def avaliar_consulta(request, id_consulta):
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_analise'))
    
    if request.method == 'POST':
        consulta = get_object_or_404(Consulta, id=id_consulta)

        if consulta.paciente != Pessoa.objects.get(user=request.user):
            messages.add_message(
                request, 
                messages.ERROR, 
                'A consulta que você tentou avaliar não lhe pertence !'
            )
            return redirect(f'/pacientes/consulta/{id_consulta}/')

        if consulta.status != 'F':
            messages.add_message(
                request, 
                messages.ERROR, 
                'Esta consulta ainda não pode ser avaliada, pois não foi finalizada !'
            )
            return redirect(f'/pacientes/consulta/{id_consulta}/')

        avaliacao = Avaliacao(
            consulta=consulta,
            tempo_espera = request.POST.get('espera'),
            satisfacao = request.POST.get('satisfacao'),
        )

        try:
            avaliacao.save()
            messages.add_message(request, messages.SUCCESS, 'Avaliação realizada com sucesso !'
            )
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e} !')

        return redirect(f'/pacientes/consulta/{id_consulta}/')


@login_required
def ser_medico(request):
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_analise'))
    
    template_name = 'ser_medico.html'
    paciente = Pessoa.objects.get(user=request.user)
    especialidades = Especialidade.objects.all()

    context = {
        'paciente': paciente, 
        'legenda': 'Quero ser médico',
        'is_medico': is_medico(request.user),
        'is_aprovado': is_aprovado(request.user),
        'especialidades': especialidades,
    }

    if request.method == 'POST':
        crm = request.POST.get('crm')
        data_crm = request.POST.get('data_crm')
        cim = request.FILES.get('cim')
        especialidade = request.POST.get('especialidade')
        valor_consulta = request.POST.get('valor_consulta')

        context_medico = {
            'crm': crm.strip(),
            'data_crm': data_crm,
            'especialidade_medica': int(especialidade.strip()),
            'valor_consulta': valor_consulta.strip(),
            'cim': cim,
        }

        preenchido = True
        for k, v in context_medico.items():
            if k == 'especialidade_medica':
                if v is None:
                    preenchido = False
            elif len(v) == 0:
                preenchido = False

            if not preenchido:
                messages.add_message(request, messages.WARNING, f'O campo "{k}" não foi informado !')
                return render(request, template_name, context)

        try:
            paciente.crm = crm.strip()
            paciente.data_crm = data_crm
            paciente.especialidade_id = especialidade
            paciente.valor_consulta = valor_consulta
            paciente.save()
            messages.add_message(request, messages.SUCCESS, 'Solicitação realizada com sucesso, aguarde a análise !')
            return redirect(reverse('home'))
        
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}')
            return render(request, template_name, context)
    
    return render(request, template_name, context)
