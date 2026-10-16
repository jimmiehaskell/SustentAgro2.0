from django.contrib.auth import views as auth_views
from django.urls import path

from contas import views

app_name = 'contas'

urlpatterns = [
    path('', views.minha_conta, name='minha_conta'),
    path('cadastro/', views.CadastroView.as_view(), name='cadastro'),
    path('cadastro/<str:tipo>/', views.CadastroView.as_view(), name='cadastro_perfil'),
    path('entrar/', auth_views.LoginView.as_view(template_name='contas/entrar.html'), name='entrar'),
    path('sair/', auth_views.LogoutView.as_view(), name='sair'),
    path('contribuicoes/', views.ContribuicoesView.as_view(), name='contribuicoes'),
]
