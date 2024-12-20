from datetime import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from medicos.models import Especialidade
from pacientes.models import Consulta
from .models import Pessoa, Analise, is_aprovado, is_medico, is_membro


@login_required
def cadastro_pessoa(request):
    if Pessoa.objects.filter(user=request.user.id):
        return redirect(reverse('home'))

    template_name = 'cadastro_pessoa.html'
    especialidades = Especialidade.objects.all()

    context = {
        'especialidades': especialidades,
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
            
        if len(crm.strip()) > 0:
            if Pessoa.objects.filter(crm=crm.strip()):
                messages.add_message(request, messages.WARNING, 'CRM já cadastrado para outra pessoa !')
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
def cadastro_situacao(request):
    if is_aprovado(request.user):
        return redirect(reverse('home'))
    
    template_name = 'cadastro_situacao.html'
    pessoa_logada = Pessoa.objects.get(user=request.user)
    qtd_dias_desde_cadastro = (datetime.now().date() - pessoa_logada.criado_em.date()).days

    context = {
        'pessoa': pessoa_logada,
        'is_medico': is_medico(request.user),
        'is_aprovado': is_aprovado(request.user),
        'qtd_dias_desde_cadastro': qtd_dias_desde_cadastro
    }

    if request.method == 'POST':
        motivo = request.POST.get('motivo')

        if len(motivo.strip()) == 0:
            messages.add_message(request, messages.WARNING, 'Motivo não preenchido!')
            return redirect(reverse('cadastro_analise'))
        
        assunto = 'HEALING - Análise cadastro'
        mensagem = f"""Olá,
        
        {motivo}
        """

        if send_mail(
            assunto,
            mensagem,
            request.user.email,
            [settings.EMAIL_HOST_USER,]
        ):
            messages.add_message(request, messages.SUCCESS, 'E-mail enviado com sucesso, aguarde resposta.')
        else:
            messages.add_message(request, messages.ERROR, 'Não foi possível enviar o e-mail!')

        return redirect(reverse('cadastro_analise'))

    return render(request, template_name, context)
    

@login_required
def home(request):
    if is_membro(request.user):
        return redirect(reverse('cadastro_solicitacoes'))
    
    if not is_aprovado(request.user):
        return redirect(reverse('cadastro_situacao'))
    
    template_name = 'home.html'
    paciente = Pessoa.objects.get(user=request.user)
    medicos = Pessoa.objects.filter(is_medico=True).exclude(user=request.user)
    especialidades = Especialidade.objects.all()
    qtd_dias_desde_cadastro = (datetime.now().date() - paciente.criado_em.date()).days
    
    medico_filtrar = request.GET.get('medico')
    especialidades_filtrar = request.GET.getlist('especialidades')

    consultas_usuario = Consulta.objects.filter(paciente=paciente)
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
        'is_aprovado': is_aprovado(request.user),
        'qtd_dias_desde_cadastro': qtd_dias_desde_cadastro
    }

    return render(request, template_name, context)


@login_required
def cadastro_solicitacoes(request):
    if not is_membro(request.user):
        return redirect(reverse('home'))
    
    template_name = 'cadastro_solicitacoes.html'

    solicitacoes = Pessoa.objects.filter(status='S')

    context = {
        'is_membro': is_membro(request.user),
        'solicitacoes': solicitacoes,
    }

    return render(request, template_name, context)


@login_required
def cadastro_reanalises(request):
    if not is_membro(request.user):
        return redirect(reverse('home'))
    
    template_name = 'cadastro_reanalises.html'

    solicitacoes = Pessoa.objects.filter(status='R')

    pessoa_filtro = request.GET.get('pessoa')

    if pessoa_filtro:
        solicitacoes = solicitacoes.filter(nome__icontains=pessoa_filtro)

    context = {
        'is_membro': is_membro(request.user),
        'solicitacoes': solicitacoes,
    }

    return render(request, template_name, context)


@login_required
def analise_cadastro(request, id_pessoa):

    if not is_membro(request.user):
        return redirect(reverse('home'))
    
    pessoa = Pessoa.objects.get(user__id=id_pessoa)
    
    template_name = 'analise_cadastro.html'

    context = {
        'is_membro': is_membro(request.user),
        'pessoa': pessoa,
    }
    
    if request.method == 'POST':
        status = request.POST.get('status')
        mensagem = request.POST.get('mensagem')

        if status:
            if status == 'A':
                mensagem = 'Link de acesso: http://127.0.0.1:8000/auth/login/'
            else:
                if len(mensagem.strip()) == 0:
                    messages.add_message(request, messages.WARNING, 'Mensagem não informada !')
                    return redirect(f'/plataforma/analise-cadastro/{id_pessoa}')
                mensagem = 'Motivo: ' + mensagem

            try:
                with transaction.atomic():
                    pessoa.status = status.upper()
                    pessoa.save()
                    analise = Analise(
                                pessoa = pessoa,
                                decisao = status.upper(),
                                mensagem = mensagem,
                                analisador = request.user
                            )
                    analise.save()

                messages.add_message(request, messages.SUCCESS, f"Cadastro analisado com sucesso")
                return redirect(reverse('cadastro_solicitacoes'))
            
            except Exception as e:
                messages.add_message(request, messages.ERROR, f'Erro: {e}')
                return redirect(f'/plataforma/analise-cadastro/{id_pessoa}')
        else:
            messages.add_message(request, messages.WARNING, 'Status não selecionado !')
            return redirect(f'/plataforma/analise-cadastro/{id_pessoa}')

    return render(request, template_name, context)

@login_required
def cadastro_analise(request):
    try:
        pessoa = Pessoa.objects.get(user=request.user)
    except Pessoa.DoesNotExist:
        messages.add_message(request, messages.ERROR, "Cadastro não encontrado.")
        return redirect(reverse('home'))

    if pessoa.status == 'A':
        messages.add_message(request, messages.SUCCESS, "Seu cadastro já foi aprovado!")
        return redirect(reverse('home'))

    if request.method == "POST":
        try:
            pessoa.status = 'S'
            pessoa.save()
            messages.add_message(request, messages.SUCCESS, "Seu cadastro foi enviado para análise.")
        except Exception as e:
            messages.add_message(request, messages.ERROR, f"Erro ao atualizar o status: {e}")
        return redirect(reverse('cadastro_analise'))

    # Renderiza o template com informações do cadastro
    template_name = 'cadastro_situacao.html'
    context = {
        'pessoa': pessoa,
        'status': pessoa.status,
    }

    return render(request, template_name, context)

