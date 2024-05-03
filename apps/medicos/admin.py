from django.contrib import admin
from .models import Especialidade, DatasAbertas

class DatasAbertasAdmin(admin.ModelAdmin):
    list_display = ('data', 'user', 'agendada')


admin.site.register(Especialidade)
admin.site.register(DatasAbertas, DatasAbertasAdmin)
