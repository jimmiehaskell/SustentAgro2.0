from django.http import Http404
from django.views.generic import TemplateView

from doacoes import mocks
from ongs import mocks as ongs_mocks

TIPOS = ('itens', 'voluntariado', 'dinheiro')


class ContribuirView(TemplateView):
    """Tela 15 · Contribuir (BL-22, Pedro). RF-14, RF-15, RF-17. Camada 2 (BL-42, BL-43).
    MOCK: trocar na camada 2. Proteger com DoadorRequeridoMixin (visitante vai ao login, UC-05).
    """
    template_name = 'doacoes/contribuir.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ong = ongs_mocks.ong_por_pk(kwargs['ong_pk'])
        tipo = kwargs['tipo']
        if ong is None or tipo not in TIPOS:
            raise Http404
        context.update(ong=ong, tipo=tipo,
                       necessidades=[n for n in ong.necessidades if n.situacao == 'aberta' and n.tipo == tipo])
        return context


class AConfirmarView(TemplateView):
    """Tela 12 · Doações a confirmar pela ONG (BL-22, Pedro). RF-16, RN-02. Camada 2 (BL-44).
    MOCK: trocar na camada 2. Proteger com OngAtivaRequeridaMixin.
    """
    template_name = 'doacoes/a_confirmar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pendentes'] = mocks.PENDENTES_DA_ONG
        context['aba'] = 'doacoes'
        return context
