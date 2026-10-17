from django.urls import path

from core import views

app_name = 'core'

urlpatterns = [
    path('', views.InicioView.as_view(), name='inicio'),
    path('saude/', views.saude, name='saude'),
    # Só em DEBUG: troca o perfil simulado para navegar pelas telas mock
    path('mock/perfil/<str:perfil>/', views.definir_perfil_mock, name='perfil_mock'),
]
