from django.urls import path

from colheita import views

app_name = 'colheita'

urlpatterns = [
    path('', views.OfertasView.as_view(), name='ofertas'),
    path('<int:pk>/reservar/', views.ReservarOfertaView.as_view(), name='reservar'),
    path('publicar/', views.PublicarOfertaView.as_view(), name='publicar'),
    path('minhas-ofertas/', views.MinhasOfertasView.as_view(), name='minhas_ofertas'),
    path('minhas-reservas/', views.MinhasReservasView.as_view(), name='minhas_reservas'),
    path('minhas-reservas/<int:pk>/receber/', views.ConfirmarRecebimentoView.as_view(), name='confirmar_recebimento'),
]
