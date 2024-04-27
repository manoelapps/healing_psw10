from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    template_name = 'home.html'
    context = {}

    return render(request, template_name, context)
