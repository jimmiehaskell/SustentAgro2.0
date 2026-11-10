from django.contrib import admin

from ongs.models import Necessidade, Ods, Ong

# BL-29 (Júlia): na Ong, ações do admin "Aprovar", "Reprovar" e "Desativar" que chamam
# ongs.services (RN-14, RN-19, P-11).


@admin.register(Ods)
class OdsAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nome', 'cor')


class NecessidadeInline(admin.TabularInline):
    model = Necessidade
    extra = 0
    fields = ('titulo', 'tipo', 'unidade', 'meta', 'situacao')


@admin.register(Ong)
class OngAdmin(admin.ModelAdmin):
    list_display = ('nome', 'localidade', 'situacao', 'verificacao_cnpj', 'criada_em')
    list_filter = ('situacao', 'verificacao_cnpj', 'localidade')
    search_fields = ('nome', 'nome_curto', 'cnpj', 'usuario__username')
    list_select_related = ('localidade',)
    filter_horizontal = ('ods',)
    readonly_fields = ('criada_em',)
    inlines = [NecessidadeInline]


@admin.register(Necessidade)
class NecessidadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ong', 'tipo', 'meta', 'unidade', 'situacao', 'criada_em')
    list_filter = ('tipo', 'situacao')
    search_fields = ('titulo', 'ong__nome')
    list_select_related = ('ong',)
