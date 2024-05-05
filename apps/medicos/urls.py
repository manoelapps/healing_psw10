from django.urls import path
from . import views, htmx_views

urlpatterns = [
    path('abrir-horario/', views.abrir_horario, name='abrir_horario'),
    path('deletar-horario/<int:id_horario>/', views.deletar_horario, name='deletar_horario'),
    path('consultas/', views.consultas_medico, name='consultas_medico'),
    path('consulta-detalhe/<int:id_consulta>/', views.consulta_detalhe, name='consulta_detalhe'),
    path('add_documento/<int:id_consulta>/', views.add_documento, name="add_documento"),
    path('finalizar-consulta/<int:id_consulta>/', views.finalizar_consulta, name='finalizar_consulta'),
]

htmx_urlpatterns = [
    path('fitrar-horarios/', htmx_views.filtrar_horarios, name='filtrar_horarios'),
]

urlpatterns += htmx_urlpatterns
