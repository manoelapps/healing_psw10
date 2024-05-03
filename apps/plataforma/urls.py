from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro_pessoa, name='cadastro_pessoa'),
    path('', views.home, name='home'),
]

