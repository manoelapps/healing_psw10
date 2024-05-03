from django.urls import path
from . import views

urlpatterns = [
    path('agendar-horario/<int:id_medico>/', views.agendar_horario, name="agendar_horario"),
    path('escolher-horario/<int:id_data_aberta>/', views.escolher_horario, name="escolher_horario"),
    path('minhas-consultas/', views.minhas_consultas, name="minhas_consultas"),
    path('consulta/<int:id_consulta>/', views.consulta, name="consulta"),
    path('cancelar-consulta/<int:id_consulta>/', views.cancelar_consulta, name="cancelar_consulta"),
]
