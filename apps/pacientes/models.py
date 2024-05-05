from django.db import models
from plataforma.models import Pessoa
from medicos.models import DatasAbertas


class Consulta(models.Model):
    status_choices = (
        ('A', 'Agendada'),
        ('C', 'Cancelada'),
        ('I', 'Iniciada'),
        ('F', 'Finalizada'),
        ('NC', 'Não compareceu')
    )
    paciente = models.ForeignKey(Pessoa, on_delete=models.DO_NOTHING)
    data_aberta = models.ForeignKey(DatasAbertas, on_delete=models.DO_NOTHING)
    link = models.URLField(null=True, blank=True)
    anotacoes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=2, choices=status_choices, default='A')

    @property
    def valor(self):
        return Pessoa.objects.get(user=self.data_aberta.user).valor_consulta

    def __str__(self):
        return self.paciente.username


class Documento(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=30)
    documento = models.FileField(upload_to='consulta/documentos')

    def __str__(self):
        return self.titulo
