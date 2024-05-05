from datetime import datetime
from django.contrib.auth.models import User
from django.db import models


class Especialidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    icone = models.ImageField(upload_to="especialidade/icones", null=True, blank=True)

    def __str__(self):
        return self.nome


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
    
    @property
    def get_nome_user(self):
        from plataforma.models import Pessoa
        return Pessoa.objects.get(user=self.user).nome

    class Meta:
        verbose_name_plural = 'Datas abertas'

    def __str__(self):
        return str(self.data)
