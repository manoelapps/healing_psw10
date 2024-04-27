from django.urls import path
from . import views, htmx_views

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
]

htmx_urlpatterns = [
    path('checa/', htmx_views.check_username, name='check_username'),
]

urlpatterns += htmx_urlpatterns
