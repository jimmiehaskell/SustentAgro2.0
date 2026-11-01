from django.contrib import admin  # noqa: F401

# BL-25 / BL-29 (Júlia): registrar Ods, Ong e Necessidade. Na Ong, ações do admin
# "Aprovar", "Reprovar" e "Desativar" que chamam ongs.services (RN-14, RN-19, P-11).
from django.contrib import admin

from .models import Necessidade, Ods, Ong


@admin.register(Ods)
class OdsAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nome', 'cor')


@admin.register(Ong)
class OngAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'situacao', 'verificacao_cnpj', 'criada_em')
    list_filter = ('situacao', 'verificacao_cnpj')
    search_fields = ('nome', 'nome_curto', 'cnpj')
    filter_horizontal = ('ods',)


@admin.register(Necessidade)
class NecessidadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ong', 'tipo', 'meta', 'situacao')
    list_filter = ('tipo', 'situacao')