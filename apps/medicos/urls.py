from django.urls import path
from . import views, htmx_views

urlpatterns = [
    path('abrir-horario/', views.abrir_horario, name='abrir_horario'),
    path('deletar-horario/<int:id_horario>/', views.deletar_horario, name='deletar_horario'),
]

htmx_urlpatterns = [
    path('fitrar-horarios/', htmx_views.filtrar_horarios, name='filtrar_horarios'),
]

urlpatterns += htmx_urlpatterns
