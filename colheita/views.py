from django.shortcuts import redirect
from django.views.generic import TemplateView

from colheita import mocks
from colheita.choices import Categoria, Estado, Transporte
from core.mixins import AgricultorRequeridoMixin, OngAtivaRequeridaMixin
from core.perfis import perfil_da_requisicao
from ongs import mocks as ongs_mocks

LIMITES_KM = {'30': 30, '60': 60, 'todas': None}


class OfertasView(TemplateView):
    """Tela 7 · Ofertas da Colheita (BL-18, Gabriel). RF-19 a RF-22, RF-27, RF-28.
    Versão ONG ativa: distância, filtros de km e reserva. Versão visitante/doador: só consulta (D-26).
    MOCK: trocar na camada 1 (BL-33, BL-34).
    """
    template_name = 'colheita/ofertas.html'

    def dispatch(self, request, *args, **kwargs):
        perfil = perfil_da_requisicao(request)
        if perfil in ('ong-pendente', 'ong-reprovada'):
            return redirect('ongs:minha_ong')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil = perfil_da_requisicao(self.request)

        dist = self.request.GET.get('dist', 'todas')
        if dist not in LIMITES_KM:
            dist = 'todas'

        ofertas = [o for o in mocks.OFERTAS if o.saldo > 0]

        if perfil == 'ong':
            limite = LIMITES_KM[dist]
            if limite is not None:
                ofertas = [o for o in ofertas if o.distancia_km <= limite]

            # RF-22: direcionadas à ONG primeiro, depois urgentes, depois as mais perto.
            ofertas.sort(
                key=lambda o: (
                    o.ong_destino is None,
                    not o.urgente,
                    o.distancia_km,
                )
            )
        else:
            # Visitante e doador não veem ofertas direcionadas (RN-04).
            ofertas = [o for o in ofertas if o.ong_destino is None]

        context.update(
            ofertas=ofertas,
            dist=dist,
            versao_ong=perfil == 'ong',
            localidade_da_ong='Ceilândia',
        )
        return context


class PublicarOfertaView(AgricultorRequeridoMixin, TemplateView):
    """Tela 6 · Publicar oferta (BL-17, Gabriel). RF-18, RN-13, RN-16.
    MOCK: trocar na camada 1 (BL-32).
    """
    template_name = 'colheita/publicar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            categorias=Categoria.choices,
            estados=Estado.choices,
            transportes=Transporte.choices,
            localidades=ongs_mocks.LOCALIDADES,
            ongs=ongs_mocks.ONGS,
            localidade_do_agricultor='Brazlândia',
        )
        return context


class MinhasOfertasView(AgricultorRequeridoMixin, TemplateView):
    """Tela 13 · Minhas ofertas do agricultor (BL-21, Pedro). RF-25, RF-27.
    MOCK: trocar na camada 1 (BL-36).
    """
    template_name = 'colheita/minhas_ofertas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ofertas'] = mocks.OFERTAS_DO_AGRICULTOR
        context['reservas'] = [
            r for r in mocks.RESERVAS_DA_ONG
            if r.situacao == 'ativa'
        ]
        return context


class MinhasReservasView(OngAtivaRequeridaMixin, TemplateView):
    """Tela 11 · Minhas reservas da ONG (BL-19, Gabriel). RF-23, RF-24, RF-27, RN-17.
    MOCK: trocar na camada 1 (BL-35) e cancelar na camada 3 (BL-47).
    """
    template_name = 'colheita/minhas_reservas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ativas'] = [
            r for r in mocks.RESERVAS_DA_ONG
            if r.situacao == 'ativa'
        ]
        context['recebidas'] = [
            r for r in mocks.RESERVAS_DA_ONG
            if r.situacao == 'recebida'
        ]
        context['aba'] = 'reservas'
        return context
    