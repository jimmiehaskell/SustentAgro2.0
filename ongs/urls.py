from django.urls import path

from ongs import views

app_name = 'ongs'

urlpatterns = [
    path('', views.ListaOngsView.as_view(), name='lista'),
    path('<int:pk>/', views.DetalheOngView.as_view(), name='detalhe'),
    path('minha-ong/', views.MinhaOngView.as_view(), name='minha_ong'),
    path('minha-ong/necessidades/', views.NecessidadesView.as_view(), name='necessidades'),
]
