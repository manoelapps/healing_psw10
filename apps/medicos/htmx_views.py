from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import DatasAbertas


@login_required
def filtrar_horarios(request):
    template_name = 'htmx/filtro_horarios.html'
    data = request.GET.get('data-filter')

    datas_abertas = DatasAbertas.objects.filter(user=request.user).filter(data__contains=data)

    context = {
        'datas_abertas': datas_abertas,
    }

    return render(request, template_name, context)
