from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
]

htmx_urlpatterns = [

]

urlpatterns += htmx_urlpatterns
