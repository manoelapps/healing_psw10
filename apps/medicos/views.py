from datetime import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import DatasAbertas
from plataforma.models import Pessoa, is_aprovado, is_medico


@login_required
def abrir_horario(request):
    pessoa_logada = Pessoa.objects.get(user=request.user)
    if pessoa_logada.status != 'A':
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
    pessoa_logada = Pessoa.objects.get(user=request.user)
    if pessoa_logada.status != 'A':
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
