from django.views.generic import TemplateView

from painel import mocks


class PainelView(TemplateView):
    """Tela 8 · Painel de impacto (BL-20, Pedro). RF-29, RF-30, RF-31. Público.
    MOCK: trocar na camada 1 (BL-37) por painel.services.indicadores(), kg_por_mes() e fatia_por_ods().
    """
    template_name = 'painel/painel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['indicadores'] = mocks.INDICADORES
        context['kg_por_mes'] = mocks.KG_POR_MES
        context['fatia_por_ods'] = mocks.FATIA_POR_ODS
        return context
