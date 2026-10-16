from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'SustentAgro'
admin.site.site_title = 'SustentAgro'
admin.site.index_title = 'Administração'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls_core')),
    path('conta/', include('contas.urls')),
    path('ongs/', include('ongs.urls')),
    path('colheita/', include('colheita.urls')),
    path('doacoes/', include('doacoes.urls')),
    path('impacto/', include('painel.urls')),
]

# Em desenvolvimento o Django serve os uploads; na VPS quem serve é o Nginx (RNF-03)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
