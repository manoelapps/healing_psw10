from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro_pessoa, name='cadastro_pessoa'),
    path('cadastro/analise/', views.cadastro_analise, name='cadastro_analise'),
    path('', views.home, name='home'),
]
