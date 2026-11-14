from django.views.generic import TemplateView

from painel import services


class PainelView(TemplateView):
    """Tela 8 · Painel de impacto (BL-20 e BL-37, Pedro). RF-29, RF-30, RF-31. Público.
    Os números vêm do banco, calculados em painel.services. Sem reservas recebidas, a tela mostra o estado vazio.
    """
    template_name = 'painel/painel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['indicadores'] = services.indicadores()
        context['kg_por_mes'] = services.kg_por_mes()
        context['fatia_por_ods'] = services.fatia_por_ods()
        return context
