from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.core.exceptions import ValidationError
from django.template.response import TemplateResponse

from ongs import services
from ongs.models import Necessidade, Ods, Ong


@admin.register(Ods)
class OdsAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nome', 'cor')


class NecessidadeInline(admin.TabularInline):
    model = Necessidade
    extra = 0
    fields = ('titulo', 'tipo', 'unidade', 'meta', 'situacao')


class MotivoDaReprovacaoForm(forms.Form):
    motivo = forms.CharField(label='Motivo da reprovação', widget=forms.Textarea(attrs={'rows': 4, 'cols': 60}),
                             help_text='A ONG vê este texto ao entrar na "Minha conta" (RN-20).')


@admin.register(Ong)
class OngAdmin(admin.ModelAdmin):
    """RN-14, P-11 (BL-29): o administrador aprova, reprova ou desativa ONGs só pelas ações da lista,
    que chamam ongs.services. Por isso a situação, as datas e o motivo não são editados no formulário."""
    list_display = ('nome', 'localidade', 'situacao', 'verificacao_cnpj', 'criada_em')
    list_filter = ('situacao', 'verificacao_cnpj', 'localidade')
    search_fields = ('nome', 'nome_curto', 'cnpj', 'usuario__username')
    list_select_related = ('localidade',)
    filter_horizontal = ('ods',)
    readonly_fields = ('situacao', 'motivo_reprovacao', 'criada_em', 'aprovada_em')
    inlines = [NecessidadeInline]
    actions = ['aprovar', 'reprovar', 'desativar']

    @admin.action(description='Aprovar as ONGs selecionadas')
    def aprovar(self, request, queryset):
        for ong in queryset:
            services.aprovar_ong(ong)
        self.message_user(request, f'{len(queryset)} ONG(s) aprovada(s). Elas já aparecem no site.',
                          messages.SUCCESS)

    @admin.action(description='Reprovar as ONGs selecionadas (pede o motivo)')
    def reprovar(self, request, queryset):
        # Página intermediária: o motivo é obrigatório (RN-20)
        form = MotivoDaReprovacaoForm(request.POST if 'reprovar_com_motivo' in request.POST else None)
        if form.is_bound and form.is_valid():
            try:
                for ong in queryset:
                    services.reprovar_ong(ong, form.cleaned_data['motivo'])
            except ValidationError as erro:
                form.add_error('motivo', erro.message_dict['motivo_reprovacao'])
            else:
                self.message_user(request, f'{len(queryset)} ONG(s) reprovada(s). A ONG vê o motivo ao entrar.',
                                  messages.SUCCESS)
                return None
        contexto = {**self.admin_site.each_context(request), 'title': 'Reprovar ONGs', 'ongs': queryset,
                    'form': form, 'opts': self.model._meta, 'action_checkbox_name': ACTION_CHECKBOX_NAME}
        return TemplateResponse(request, 'admin/ongs/ong/reprovar.html', contexto)

    @admin.action(description='Desativar as ONGs selecionadas (cancela as reservas ativas)')
    def desativar(self, request, queryset):
        canceladas = sum(services.desativar_ong(ong) for ong in queryset)
        self.message_user(request, f'{len(queryset)} ONG(s) desativada(s) e {canceladas} reserva(s) ativa(s) '
                                   'cancelada(s). As quantidades voltaram ao saldo das ofertas.',
                          messages.WARNING)


@admin.register(Necessidade)
class NecessidadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ong', 'tipo', 'meta', 'unidade', 'situacao', 'criada_em')
    list_filter = ('tipo', 'situacao')
    search_fields = ('titulo', 'ong__nome')
    list_select_related = ('ong',)
