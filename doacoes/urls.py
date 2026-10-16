from django.urls import path

from doacoes import views

app_name = 'doacoes'

urlpatterns = [
    path('contribuir/<int:ong_pk>/<str:tipo>/', views.ContribuirView.as_view(), name='contribuir'),
    path('a-confirmar/', views.AConfirmarView.as_view(), name='a_confirmar'),
]
