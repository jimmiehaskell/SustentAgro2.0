from django.views.generic import TemplateView

from colheita import mocks, services
from colheita.choices import Categoria, Estado, Transporte
from core.perfis import perfil_da_requisicao
from ongs import mocks as ongs_mocks

LIMITES_KM = {'30': 30, '60': 60, 'todas': None}


class OfertasView(TemplateView):
    """Tela 7 · Ofertas da Colheita (BL-18, BL-33, Gabriel). RF-19 a RF-22, RF-27, RF-28.
    Versão ONG ativa: distância, filtros de km e reserva. Versão visitante/doador: só consulta (D-26).
    MOCK: o formulário de reserva troca na camada 1 (BL-34).
    """
    template_name = 'colheita/ofertas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil = perfil_da_requisicao(self.request)
        dist = self.request.GET.get('dist', 'todas')
        if dist not in LIMITES_KM:
            dist = 'todas'
        ong = getattr(self.request.user, 'ong', None) if perfil == 'ong' else None
        ofertas = services.ofertas_da_lista(ong=ong, limite_km=LIMITES_KM[dist])
        context.update(ofertas=ofertas, dist=dist, versao_ong=ong is not None,
                       localidade_da_ong=ong.localidade.nome if ong else '')
        return context


class PublicarOfertaView(TemplateView):
    """Tela 6 · Publicar oferta (BL-17, Gabriel). RF-18, RN-13, RN-16.
    MOCK: trocar na camada 1 (BL-32). Proteger com AgricultorRequeridoMixin.
    """
    template_name = 'colheita/publicar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(categorias=Categoria.choices, estados=Estado.choices, transportes=Transporte.choices,
                       localidades=ongs_mocks.LOCALIDADES, ongs=ongs_mocks.ONGS,
                       localidade_do_agricultor='Brazlândia')
        return context


class MinhasOfertasView(TemplateView):
    """Tela 13 · Minhas ofertas do agricultor (BL-21, Pedro). RF-25, RF-27.
    MOCK: trocar na camada 1 (BL-36). Proteger com AgricultorRequeridoMixin.
    """
    template_name = 'colheita/minhas_ofertas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agricultor'] = mocks.AGRICULTOR
        # Cada oferta vai com o resumo do que já foi recebido (protótipo: oferta vencida)
        context['ofertas'] = [(oferta, services.resumo_recebido(oferta)) for oferta in mocks.OFERTAS_DO_AGRICULTOR]
        return context


class MinhasReservasView(TemplateView):
    """Tela 11 · Minhas reservas da ONG (BL-19, Gabriel). RF-23, RF-24, RF-27, RN-17.
    MOCK: trocar na camada 1 (BL-35) e cancelar na camada 3 (BL-47). Proteger com OngAtivaRequeridaMixin.
    """
    template_name = 'colheita/minhas_reservas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ativas'] = [r for r in mocks.RESERVAS_DA_ONG if r.situacao == 'ativa']
        context['recebidas'] = [r for r in mocks.RESERVAS_DA_ONG if r.situacao == 'recebida']
        context['aba'] = 'reservas'
        return context
