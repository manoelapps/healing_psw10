from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from medicos.models import DatasAbertas, Especialidade


def is_aprovado(user):
    pessoa = Pessoa.objects.filter(user=user)
    return pessoa[0].status == 'A' if pessoa else False

def is_medico(user):
    pessoa = Pessoa.objects.filter(user=user)
    return pessoa[0].is_medico if pessoa else False


class Pessoa(models.Model):
    choices_status = (
        ('A', 'Aprovado'),
        ('R', 'Reprovado'),
        ('S', 'Solicitado'),
    )
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, primary_key=True)
    nome = models.CharField(max_length=100)
    cnh_rg = models.FileField(upload_to="pessoa/cnh_rg")
    data_nascimento = models.DateField()
    foto = models.ImageField(upload_to="pessoa/foto_perfil")
    cep = models.CharField(max_length=8)
    logradouro = models.CharField(max_length=100)
    numero = models.PositiveSmallIntegerField(blank=True, null=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    descricao = models.TextField(null=True, blank=True)
    # Dados médicos
    is_medico = models.BooleanField(default=False)
    crm = models.CharField(max_length=30, unique=True, blank=True, null=True)
    data_crm = models.DateField(blank=True, null=True)
    cedula_identidade_medica = models.FileField(upload_to='medico/cim', blank=True, null=True)
    especialidade = models.ForeignKey(Especialidade, on_delete=models.DO_NOTHING, null=True, blank=True)
    valor_consulta = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=1, choices=choices_status, default='S')
    # Datas automáticas 
    criado_em = models.DateTimeField(auto_now_add=True, auto_now=False)
    modificado_em = models.DateTimeField(auto_now_add=False, auto_now=True)

    @property
    def proxima_data(self):
        proxima_data = DatasAbertas.objects.filter(user=self.user).filter(data__gt=datetime.now()).filter(agendada=False).order_by('data').first()     
        return proxima_data
    
    def __str__(self):
        return self.user.username
    