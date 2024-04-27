from django.urls import path
from . import views, htmx_views

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.logar, name='login'),
    path('logout/', views.sair, name='sair'),
]

htmx_urlpatterns = [
    path('checa-username/', htmx_views.check_username, name='check_username'),
    path('checa-senha/', htmx_views.check_senha, name='check_senha'),
]

urlpatterns += htmx_urlpatterns
