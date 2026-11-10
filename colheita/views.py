from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from colheita import mocks, services
from colheita.choices import Categoria, Estado, SituacaoReserva, Transporte
from core.mixins import OngAtivaRequeridaMixin
from core.perfis import perfil_da_requisicao
from ongs import mocks as ongs_mocks

LIMITES_KM = {'30': 30, '60': 60, 'todas': None}


class OfertasView(TemplateView):
    """Tela 7 · Ofertas da Colheita (BL-18, BL-33, Gabriel). RF-19 a RF-22, RF-27, RF-28.
    Versão ONG ativa: distância, filtros de km e reserva. Versão visitante/doador: só consulta (D-26).
    O formulário de reserva faz POST em ReservarOfertaView (BL-34).
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


class ReservarOfertaView(OngAtivaRequeridaMixin, View):
    """Reservar oferta, formulário da Tela 7 (BL-34, Gabriel). RF-20, RF-27, RN-01, RN-03, RN-16.
    Só ONG ativa; oferta fora da lista dela (inexistente, direcionada a outra, vencida, sem saldo) dá 404.
    """
    http_method_names = ['post']

    def post(self, request, pk):
        ong = request.user.ong
        oferta = next((o for o in services.ofertas_da_lista(ong=ong) if o.pk == pk), None)
        if oferta is None:
            raise Http404
        try:
            quantidade = Decimal(request.POST.get('quantidade', '').replace(',', '.'))
            if not quantidade.is_finite():
                raise InvalidOperation
            reserva = services.reservar_oferta(oferta, ong, quantidade)
        except InvalidOperation:
            messages.error(request, 'Informe a quantidade em números.')
        except ValidationError as erro:
            messages.error(request, ' '.join(erro.messages))
        else:
            messages.success(request, f'Reserva feita: {reserva.quantidade.normalize():f} {oferta.unidade} de {oferta.produto}. '
                                      'O contato do agricultor está em Minhas reservas.')
        return redirect('colheita:ofertas')


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


class MinhasReservasView(OngAtivaRequeridaMixin, TemplateView):
    """Tela 11 · Minhas reservas da ONG (BL-19, BL-34, Gabriel). RF-23, RF-24, RF-27, RN-17.
    Reservas reais, com o contato do agricultor (BL-34). MOCK: o formulário de recebimento troca na camada 1
    (BL-35) e cancelar na camada 3 (BL-47).
    """
    template_name = 'colheita/minhas_reservas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservas = services.reservas_da_ong(self.request.user.ong)
        context['ativas'] = [r for r in reservas if r.situacao == SituacaoReserva.ATIVA]
        context['recebidas'] = [r for r in reservas if r.situacao == SituacaoReserva.RECEBIDA]
        context['aba'] = 'reservas'
        return context
