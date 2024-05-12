from datetime import datetime
from random import randint
from django.db.models import Sum


def calcula_total(obj, campo):

    total = obj.aggregate(Sum(campo))[f'{campo}__sum']

    return 0 if total == None else total


def calcula_media(valor, quantidade):
    try:
        media = valor / quantidade
        return int(media * 100)/100
    
    except:
        return 0


def gera_cor_da_barra():
    cor = 'rgb('
    for i in range(3):
        cor += str(randint(0, 255))
        cor += ',' if i < 2 else ')'

    return cor