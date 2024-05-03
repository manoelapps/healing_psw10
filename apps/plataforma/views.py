from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from medicos.models import Especialidade
from pacientes.models import Consulta
from .models import is_medico, Pessoa


@login_required
def cadastro_pessoa(request):
    template_name = 'cadastro_pessoa.html'
    # pessoa_logada = Pessoa.objects.get(user=request.user)
    if Pessoa.objects.filter(user=request.user.id):
        return redirect(reverse('home'))

    if is_medico(request.user):
        messages.add_message(request, messages.WARNING, 'Redirecionado, pois vocé já consta como médico !')
        return redirect(reverse('abrir_horario'))

    especialidades = Especialidade.objects.all()

    context = {
        'especialidades': especialidades,
        # 'pessoa': pessoa_logada,
        'is_medico': is_medico(request.user),
    }

    if request.method == "POST":
        nome = request.POST.get('nome')
        cnh_rg = request.FILES.get('cnh_rg')
        data_nascimento = request.POST.get('data_nascimento')
        foto = request.FILES.get('foto')
        cep = request.POST.get('cep')
        logradouro = request.POST.get('logradouro')
        numero = request.POST.get('numero')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        uf = request.POST.get('uf')
        descricao = request.POST.get('descricao')
        sou_medico = request.POST.get('sou_medico')
        crm = request.POST.get('crm')
        data_crm = request.POST.get('data_crm')
        cim = request.FILES.get('cim')
        especialidade = request.POST.get('especialidade')
        valor_consulta = request.POST.get('valor_consulta')

        context_nao_obrigado = {
            'numero': numero.strip(),
            'descricao': descricao.strip(),
            'sou_medico': sou_medico,
        }
        for k, v in context_nao_obrigado.items():
                context[k] = v

        context_paciente = {
            'nome': nome.strip(),
            'data_nascimento': data_nascimento,
            'cep': cep.strip(),
            'logradouro': logradouro.strip(),
            'bairro': bairro.strip(),
            'cidade': cidade.strip(),
            'uf': uf.strip(),
            'cnh_rg': cnh_rg,
            'foto': foto,
        }

        context_medico = {
            'crm': crm.strip(),
            'data_crm': data_crm,
            'especialidade_medica': int(especialidade.strip()) if sou_medico else None,
            'valor_consulta': valor_consulta.strip(),
            'cim': cim,
        }

        context_unificado = context_paciente
        if sou_medico:
            for k, v in context_medico.items():
                context_unificado[k] = v

        for k, v in context_unificado.items():
                context[k] = v
    
        preenchido = True
        for k, v in context_unificado.items():
            if k in ['cnh_rg', 'foto', 'cim', 'especialidade_medica']:
                if v is None:
                    preenchido = False
            elif len(v) == 0:
                preenchido = False

            if not preenchido:
                messages.add_message(request, messages.WARNING, f'O campo "{k}" não foi informado !')
                return render(request, template_name, context)
                
        pessoa = Pessoa(
            user=request.user,
            nome=nome.strip(),
            cnh_rg=cnh_rg,
            data_nascimento=data_nascimento,
            foto=foto,
            cep=cep.strip(),
            logradouro=logradouro.strip(),
            numero=numero if numero else None,
            bairro=bairro.strip(),
            cidade=cidade.strip(),
            uf=uf.strip(),
            descricao=descricao.strip(),
            is_medico = True if sou_medico else False,
            crm=crm.strip(),
            data_crm=data_crm if sou_medico else None,
            cedula_identidade_medica=cim,
            especialidade_id=especialidade,
            valor_consulta=valor_consulta.strip() if sou_medico else None,
        )

        try:
            pessoa.save()
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}')
            return render(request, template_name, context)

        if sou_medico:
            return redirect(reverse('abrir_horario'))
        else:
            return redirect(reverse('home'))

    return render(request, template_name, context)


@login_required
def home(request):
    template_name = 'home.html'
    paciente = Pessoa.objects.get(user=request.user)
    medicos = Pessoa.objects.filter(is_medico=True).exclude(user=request.user)
    especialidades = Especialidade.objects.all()
    qtd_dias_desde_cadastro = (datetime.now().date() - paciente.criado_em.date()).days
    
    medico_filtrar = request.GET.get('medico')
    especialidades_filtrar = request.GET.getlist('especialidades')

    consultas_usuario = Consulta.objects.filter(paciente=request.user)
    consultas_agendadas = consultas_usuario.filter(data_aberta__data__gte=datetime.now()).filter(status='A')

    if medico_filtrar:
        medicos = medicos.filter(nome__icontains = medico_filtrar)

    if especialidades_filtrar:
        medicos = medicos.filter(especialidade_id__in=especialidades_filtrar)

    context = {
        'legenda': 'Agende sua consulta',
        'paciente': paciente,
        'medicos': medicos,
        'especialidades': especialidades,
        'consultas_agendadas': consultas_agendadas,
        'is_medico': is_medico(request.user),
        'qtd_dias_desde_cadastro': qtd_dias_desde_cadastro
    }

    return render(request, template_name, context)
