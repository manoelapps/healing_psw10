from django.contrib import admin
from .models import Pessoa, Analise


class PessoaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'is_medico', 'status', 'get_is_staff']
    search_fields = ['nome']
    list_filter = ['is_medico', 'status']

    @admin.display(description="Is Membro")
    def get_is_staff(self, obj):
        return obj.user.is_staff

admin.site.register(Pessoa, PessoaAdmin)
admin.site.register(Analise)
