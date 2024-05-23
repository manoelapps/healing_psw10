from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro_pessoa, name='cadastro_pessoa'),
    path('cadastro/situacao/', views.cadastro_situacao, name='cadastro_situacao'),
    path('', views.home, name='home'),
    path('cadastro/solicitacoes/', views.cadastro_solicitacoes, name='cadastro_solicitacoes'),
    path('cadastro/reanalises/', views.cadastro_reanalises, name='cadastro_reanalises'),
    path('analise-cadastro/<int:id_pessoa>', views.analise_cadastro, name='analise_cadastro'),
]
