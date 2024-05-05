from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from pacientes.models import Consulta, Documento
from .models import DatasAbertas
from plataforma.models import Pessoa, is_aprovado, is_medico


@login_required
def abrir_horario(request):
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_analise'))
    
    if not is_medico(request.user):
        messages.add_message(request, messages.WARNING, 'Somente médicos podem acessar essa página, você foi redirecionado !')
        return redirect(reverse('home'))
    
    template_name = 'abrir_horario.html'
    medico = Pessoa.objects.get(user=request.user)
    datas_abertas = DatasAbertas.objects.filter(user=request.user)

    context = {
        'medico': medico,
        'datas_abertas': datas_abertas,
        'is_medico': is_medico(request.user),
        'is_aprovado': is_aprovado(request.user),
    }

    if request.method == "POST":
        data = request.POST.get('data')

        if not data:
            messages.add_message(request, messages.WARNING, 'Data não informada !')
            return redirect(reverse('abrir_horario'))

        data_formatada = datetime.strptime(data, "%Y-%m-%dT%H:%M")

        if datas_abertas.filter(data=data):
            context['data_informada'] = data
            messages.add_message(request, messages.ERROR, f'A data/hora informada já foi cadastrada anteriormente !')
            return render(request, template_name, context)
        
        if data_formatada <= datetime.now():
            context['data_informada'] = data
            messages.add_message(request, messages.WARNING, 'A data/hora deve ser maior ou igual a data/hora atual.')
            return render(request, template_name, context)

        data_aberta = DatasAbertas(
            data=data,
            user=request.user
        )
        try:
            data_aberta.save()
            messages.add_message(request, messages.SUCCESS, 'Data/Horário cadastrado com sucesso.')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}')

        return redirect(reverse('abrir_horario'))

    return render(request, template_name, context)


@login_required
def deletar_horario(request, id_horario):
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_analise'))
    
    data_aberta = get_object_or_404(DatasAbertas, id=id_horario)
    if data_aberta.user != request.user:
        messages.add_message(request, messages.ERROR, 'Esta data/horário não lhe pertence !') 
        return redirect(reverse('abrir_horario'))
    
    if data_aberta.agendada:
        messages.add_message(request, messages.ERROR, 'Esta data/horário não pode ser excluída, pois está agendada !') 
        return redirect(reverse('abrir_horario'))

    try:
        data_aberta.delete()
        messages.add_message(request, messages.SUCCESS, 'Data/Hora removida com sucesso.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, f'Erro: {e}') 

    return redirect(reverse('abrir_horario'))


@login_required
def consultas_medico(request):
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_analise'))
    
    template_name = 'consultas.html'
    if not is_medico(request.user):
        messages.add_message(request, messages.WARNING, 'Somente médicos podem acessar a página pretendida, você foi redirecionado.')
        return redirect(reverse('home'))
    
    status_consulta = Consulta.status_choices
    hoje = datetime.now().date()
    
    consultas = Consulta.objects.filter(data_aberta__user=request.user)

    consultas_hoje = consultas.filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1))

    consultas_restantes = consultas.exclude(id__in=consultas_hoje.values('id'))

    context = {
        'status_consulta': status_consulta, 
        'consultas_hoje': consultas_hoje, 
        'consultas_restantes': consultas_restantes, 
        'is_medico': is_medico(request.user),
        'is_aprovado': is_aprovado(request.user),
    }

    paciente_filter = request.GET.get('paciente')
    status_filter = request.GET.get('status')
    data_filter = request.GET.get('data')

    if paciente_filter:
        context['paciente_filter'] = paciente_filter
        consultas_hoje = consultas_hoje.filter(paciente__username__icontains=paciente_filter)
        context['consultas_hoje'] = consultas_hoje
        consultas_restantes = consultas_restantes.filter(paciente__username__icontains=paciente_filter)
        context['consultas_restantes'] = consultas_restantes

    if status_filter:
        context['status_filter'] = status_filter
        consultas_hoje = consultas_hoje.filter(status=status_filter)
        context['consultas_hoje'] = consultas_hoje
        consultas_restantes = consultas_restantes.filter(status=status_filter)
        context['consultas_restantes'] = consultas_restantes
        
    if data_filter:
        context['data_filter'] = data_filter
        consultas_hoje = consultas_hoje.filter(data_aberta__data__icontains=data_filter)
        context['consultas_hoje'] = consultas_hoje
        consultas_restantes = consultas_restantes.filter(data_aberta__data__icontains=data_filter)
        context['consultas_restantes'] = consultas_restantes

    return render(request, template_name, context)


@login_required
def consulta_detalhe(request, id_consulta):
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_analise'))
    
    if not is_medico(request.user):
        messages.add_message(request, messages.WARNING, 'Somente médicos podem acessar a página pretendida, você foi redirecionado !')
        return redirect(reverse('home'))
    
    template_name = 'consulta_detalhe.html'
    consulta = Consulta.objects.get(id=id_consulta)
    status_consulta = Consulta.status_choices
    paciente = Pessoa.objects.get(user=consulta.paciente)
    documentos = Documento.objects.filter(consulta=consulta)

    context = {
        'consulta': consulta,
        'status_consulta': status_consulta,
        'paciente': paciente,
        'documentos': documentos,
        'is_medico': is_medico(request.user),
        'is_aprovado': is_aprovado(request.user),
    }

    if request.method == "POST":
        # Inicializa a consulta + link da chamada
        link = request.POST.get('link')

        if consulta.data_aberta.data > datetime.now():
            messages.add_message(request, messages.WARNING, 'Essa consulta ainda não está na data/horário, você não pode inicia-la !')
            return redirect(f'/medicos/consulta-detalhe/{id_consulta}')

        if consulta.status == 'C':
            messages.add_message(request, messages.WARNING, 'Essa consulta já foi cancelada, você não pode inicia-la !')
            return redirect(f'/medicos/consulta-detalhe/{id_consulta}')
        elif consulta.status == "F" or consulta.status == "NC":
            messages.add_message(request, messages.WARNING, 'Essa consulta já foi finalizada, você não pode inicia-la !')
            return redirect(f'/medicos/consulta-detalhe/{id_consulta}')
        
        if len(link.strip()) == 0:
            messages.add_message(request, messages.WARNING, 'Link não informado !')
            return redirect(f'/medicos/consulta-detalhe/{id_consulta}')
        
        try:
            consulta.link = link.strip()
            consulta.status = 'I'
            consulta.save()

            messages.add_message(request, messages.SUCCESS, 'Consulta inicializada com sucesso.')

        except Exception as e:
            messages.add_message(request, messages.WARNING, f'Erro: {e} !')
        
        return redirect(f'/medicos/consulta-detalhe/{id_consulta}')
    
    else:
        return render(request, template_name, context) 


@login_required
def add_documento(request, id_consulta):
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_analise'))
    
    if not is_medico(request.user):
        messages.add_message(request, messages.WARNING, 'Somente médicos podem acessar a página pretendida, você foi redirecionado !')
        return redirect(reverse('home'))
    
    if request.method == 'POST':
        consulta = Consulta.objects.get(id=id_consulta)
        
        if consulta.data_aberta.user != request.user:
            messages.add_message(
                request, 
                messages.ERROR, 
                f'Você não pode adicionar documento a uma consulta que não lhe pertence !'
            )
            return redirect(f'/medicos/consulta-detalhe/{id_consulta}')
        
        if consulta.status in ('A', 'C', 'NC'):
            messages.add_message(
                request, 
                messages.ERROR, 
                'Você não pode adicionar documento para consulta que não foi iniciada ou finalizada !'
            )
            return redirect(f'/medicos/consulta-detalhe/{id_consulta}')

        titulo = request.POST.get('titulo')
        documento = request.FILES.get('documento')

        if len(titulo.strip()) == 0 or not documento:
            messages.add_message(
                request, 
                messages.WARNING, 
                'Informe título e documento !'
            )
            return redirect(f'/medicos/consulta-detalhe/{id_consulta}')

        documento = Documento(
            consulta=consulta,
            titulo=titulo.strip(),
            documento=documento
        )

        try:
            documento.save()
            messages.add_message(request, messages.SUCCESS, 'Documento enviado com sucesso!')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}')

        return redirect(f'/medicos/consulta-detalhe/{id_consulta}')


@login_required
def finalizar_consulta(request, id_consulta):
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_analise'))
    
    if not is_medico(request.user):
        messages.add_message(request, messages.WARNING, 'Somente médicos podem acessar a página pretendida, você foi redirecionado !')
        return redirect(reverse('home'))

    if request.method == 'POST':
        consulta = Consulta.objects.get(id=id_consulta)

        if consulta.data_aberta.user != request.user:
            messages.add_message(
                request, 
                messages.ERROR, 
                f'A consulta que você tentou finalizar não lhe pertence !'
            )
            return redirect(f'/medicos/consulta-detalhe/{id_consulta}')
        
        anotacoes = request.POST.get('anotacoes')

        try:
            consulta.anotacoes = anotacoes
            consulta.status = 'F'
            consulta.save()
            messages.add_message(request, messages.SUCCESS, 'Consulta finalizada com sucesso.')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}')
            
        return redirect(f'/medicos/consulta-detalhe/{id_consulta}')
