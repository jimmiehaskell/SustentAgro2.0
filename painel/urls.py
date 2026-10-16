from django.urls import path

from painel import views

app_name = 'painel'

urlpatterns = [
    path('', views.PainelView.as_view(), name='painel'),
]
