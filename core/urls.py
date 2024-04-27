from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include, reverse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('usuarios.urls')),
    path('plataforma/', include('plataforma.urls')),
    path('', lambda home: redirect(reverse('home'))),
    path('medicos/', include('medicos.urls')),
]
