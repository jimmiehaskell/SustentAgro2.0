from django.contrib import admin

from colheita.models import Oferta, Reserva


class ReservaInline(admin.TabularInline):
    model = Reserva
    extra = 0
    fields = ('ong', 'quantidade', 'situacao', 'quantidade_recebida', 'recebida_em', 'cancelada_por')


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('produto', 'quantidade', 'unidade', 'saldo', 'destino', 'localidade', 'colher_ate', 'situacao')
    list_filter = ('situacao', 'destino', 'categoria', 'localidade')
    search_fields = ('produto', 'agricultor__nome_completo')
    readonly_fields = ('criada_em',)
    inlines = [ReservaInline]


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('oferta', 'ong', 'quantidade', 'situacao', 'quantidade_recebida', 'criada_em')
    list_filter = ('situacao',)
    search_fields = ('oferta__produto', 'ong__nome')
    readonly_fields = ('criada_em',)
