from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include, reverse
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('usuarios.urls')),
    path('plataforma/', include('plataforma.urls')),
    path('', lambda home: redirect(reverse('home'))),
    path('medicos/', include('medicos.urls')),
    path('pacientes/', include('pacientes.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
