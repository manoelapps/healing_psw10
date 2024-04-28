from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import is_medico, Especialidade, Medico, DatasAbertas


@login_required
def cadastro_medico(request):
    if is_medico(request.user):
        messages.add_message(request, messages.WARNING, 'Redirecionado, pois vocé já consta como médico !')
        return redirect(reverse('abrir_horario'))

    template_name = 'cadastro_medico.html'
    especialidades = Especialidade.objects.all()

    context = {
        'especialidades': especialidades,
        'is_medico': is_medico(request.user)
    }

    if request.method == "POST":
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        logradouro = request.POST.get('logradouro')
        numero = request.POST.get('numero')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        uf = request.POST.get('uf')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')

        context_post = {
            'crm': crm.strip(),
            'nome': nome.strip(),
            'cep': cep.strip(),
            'logradouro': logradouro.strip(),
            'numero': numero.strip(),
            'bairro': bairro.strip(),
            'cidade': cidade.strip(),
            'uf': uf.strip(),
            'especialidade_medica': especialidade.strip(),
            'descricao': descricao.strip(),
            'valor_consulta': valor_consulta.strip(),
            'cedula_identidade_medica': cim,
            'rg': rg,
            'foto': foto,
        }

        # print(f"context_post[especialidade_selecionada]: {context_post['especialidade_selecionada']}")

        for k, v in context_post.items():
            context[k] = v

        preenchido = True
        for k, v in context_post.items():
            if k != 'numero':
                if k in ['cedula_identidade_medica', 'rg', 'foto']:
                    if v is None:
                        preenchido = False
                elif len(v) == 0:
                    preenchido = False
                
                if not preenchido:
                    messages.add_message(request, messages.WARNING, f'O campo "{k}" não foi informado !')
                    #TODO: Verificar porque o select do template especialidade não fica selecionado
                    
                    # print(f"\ncontext[especialidade_medica]: {context['especialidade_medica']}\n")
                    # print(f"context: {context}")

                    return render(request, template_name, context)

        medico = Medico(
            crm=crm.strip(),
            nome=nome.strip(),
            cep=cep.strip(),
            logradouro=logradouro.strip(),
            numero=numero.strip(),
            bairro=bairro.strip(),
            cidade=cidade.strip(),
            uf=uf.strip(),
            cnh_rg=rg,
            cedula_identidade_medica=cim,
            foto=foto,
            user=request.user,
            descricao=descricao.strip(),
            especialidade_id=especialidade,
            valor_consulta=valor_consulta.strip(),
        )

        try:
            medico.save()
            messages.add_message(request, messages.SUCCESS, 'Cadastro médico realizado com sucesso.')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}')
            return render(request, template_name, context)

        return redirect(reverse('abrir_horario'))

    return render(request, template_name, context)


@login_required
def abrir_horario(request):

    if not is_medico(request.user):
        messages.add_message(request, messages.WARNING, 'Somente médicos podem acessar essa página, você foi redirecionado !')
        return redirect(reverse('home'))
    
    template_name = 'abrir_horario.html'
    medico = Medico.objects.get(user=request.user)
    datas_abertas = DatasAbertas.objects.filter(user=request.user)

    context = {
        'medico': medico,
        'datas_abertas': datas_abertas,
        'is_medico': is_medico(request.user)
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
