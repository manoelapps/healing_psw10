from datetime import datetime
from django.db import models
from django.contrib.auth.models import User


def is_medico(user):
    return Medico.objects.filter(user=user).exists()


class Pessoa(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, primary_key=True)
    nome = models.CharField(max_length=100)
    cnh_rg = models.FileField(upload_to="pessoa/cnh_rg")
    foto = models.ImageField(upload_to="pessoa/foto_perfil")
    cep = models.CharField(max_length=8)
    logradouro = models.CharField(max_length=100)
    numero = models.PositiveSmallIntegerField(blank=True, null=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    descricao = models.TextField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True, auto_now=False)
    modificado_em = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        abstract = True


class Especialidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    icone = models.ImageField(upload_to="especialidade/icones", null=True, blank=True)

    def __str__(self):
        return self.nome


class Medico(Pessoa):
    crm = models.CharField(max_length=30, unique=True)
    cedula_identidade_medica = models.FileField(upload_to='medico/cim')
    especialidade = models.ForeignKey(Especialidade, on_delete=models.DO_NOTHING, null=True, blank=True)
    valor_consulta = models.DecimalField(max_digits=10, decimal_places=2, default=100)

    @property
    def proxima_data(self):
        proxima_data = DatasAbertas.objects.filter(user=self.user).filter(data__gt=datetime.now()).filter(agendada=False).order_by('data').first()     
        return proxima_data
    
    def __str__(self):
        return self.user.username


class DatasAbertas(models.Model):
    data = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    agendada = models.BooleanField(default=False)

    @property
    def data_br(self):
        return str(self.data.strftime('%d/%m/%Y %H:%M'))

    @property
    def qtd_dias(self):
        qtd_dias = (self.data.date() - datetime.now().date()).days
        return f'{qtd_dias} dias' if qtd_dias > 1 else f'{qtd_dias} dia'

    class Meta:
        verbose_name_plural = 'Datas abertas'

    def __str__(self):
        return str(self.data)

