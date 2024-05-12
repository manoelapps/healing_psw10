from django.contrib import admin
from .models import Consulta, Documento, Avaliacao


class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['id', 'paciente', 'data_aberta', 'status', 'link']


class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['consulta', 'data', 'tempo_espera', 'satisfacao']


admin.site.register(Consulta, ConsultaAdmin)
admin.site.register(Documento)
admin.site.register(Avaliacao, AvaliacaoAdmin)

