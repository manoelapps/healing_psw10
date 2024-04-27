from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User


def check_username(request):
    username = request.GET.get('username')

    try:
        user = User.objects.get(username=username)
        return HttpResponse('Este username já existe !')
    except User.DoesNotExist:
        return HttpResponse('')
