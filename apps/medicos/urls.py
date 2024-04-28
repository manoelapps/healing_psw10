from django.urls import path
from . import views, htmx_views

urlpatterns = [
    path('cadastro/', views.cadastro_medico, name='cadastro_medico'),
    path('abrir-horario/', views.abrir_horario, name='abrir_horario'),
]

htmx_urlpatterns = [
    path('fitrar-horarios/', htmx_views.filtrar_horarios, name='filtrar_horarios'),
]

urlpatterns += htmx_urlpatterns
