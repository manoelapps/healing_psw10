from django.contrib import admin
from .models import Consulta

class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'data_aberta', 'status', 'link']

admin.site.register(Consulta, ConsultaAdmin)


