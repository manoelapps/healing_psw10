from django.db import models
from django.contrib.auth.models import User
from medicos.models import DatasAbertas


class Consulta(models.Model):
    status_choices = (
        ('A', 'Agendada'),
        ('C', 'Cancelada'),
        ('I', 'Iniciada'),
        ('F', 'Finalizada'),
        ('NC', 'Não compareceu')
    )
    paciente = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    data_aberta = models.ForeignKey(DatasAbertas, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=2, choices=status_choices, default='A')
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.paciente.username
