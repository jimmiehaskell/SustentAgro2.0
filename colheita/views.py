from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.formats import number_format
from django.views import View
from django.views.generic import TemplateView

from colheita import mocks, services
from colheita.choices import CanceladaPor, Categoria, Estado, SituacaoReserva, Transporte
from colheita.models import Oferta, Reserva
from core.mixins import AgricultorRequeridoMixin, OngAtivaRequeridaMixin
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
            messages.success(request, f'Reserva feita: {number_format(reserva.quantidade.normalize())} {oferta.unidade} de {oferta.produto}. '
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
    MOCK: trocar na camada 1 (BL-36). Proteger com AgricultorRequeridoMixin. Os botões de cancelar entram
    nessa troca: CancelarReservaDoAgricultorView e CancelarOfertaView (BL-47) já estão prontas.
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
    Reservas reais, com o contato do agricultor (BL-34) e o formulário de recebimento (BL-35, em
    ConfirmarRecebimentoView) e o cancelamento (BL-47, em CancelarReservaView).
    """
    template_name = 'colheita/minhas_reservas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservas = services.reservas_da_ong(self.request.user.ong)
        context['ativas'] = [r for r in reservas if r.situacao == SituacaoReserva.ATIVA]
        context['recebidas'] = [r for r in reservas if r.situacao == SituacaoReserva.RECEBIDA]
        context['aba'] = 'reservas'
        return context


class ConfirmarRecebimentoView(OngAtivaRequeridaMixin, View):
    """Confirmar recebimento, formulário da Tela 11 (BL-35, Gabriel). RF-23, RN-16, RN-17, RN-18, E-02, E-03.
    Só ONG ativa e só a dona da reserva; reserva de outra ONG (ou inexistente) dá 404.
    """
    http_method_names = ['post']

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva.objects.select_related('oferta'), pk=pk, ong=request.user.ong)
        try:
            quantidade = Decimal(request.POST.get('quantidade_recebida', '').replace(',', '.'))
            if not quantidade.is_finite():
                raise InvalidOperation
            reserva = services.confirmar_recebimento(reserva, quantidade)
        except InvalidOperation:
            messages.error(request, 'Informe a quantidade recebida em números.')
        except ValidationError as erro:
            messages.error(request, ' '.join(erro.messages))
        else:
            produto, unidade = reserva.oferta.produto, reserva.oferta.unidade
            if reserva.situacao == SituacaoReserva.RECEBIDA:
                messages.success(request, f'Recebimento confirmado: {number_format(reserva.quantidade_recebida.normalize())} {unidade} '
                                          f'de {produto}. A quantidade já conta no painel de impacto.')
            elif reserva.oferta.vencida:
                messages.success(request, f'Reserva de {produto} encerrada como não recebida.')
            else:
                messages.success(request, f'Reserva de {produto} encerrada como não recebida. '
                                          'A quantidade voltou ao saldo da oferta.')
        return redirect('colheita:minhas_reservas')


class CancelarReservaView(OngAtivaRequeridaMixin, View):
    """Cancelar reserva, botão da Tela 11 (BL-47, Gabriel). RF-24, UC-09.
    Só ONG ativa e só a dona da reserva; reserva de outra ONG (ou inexistente) dá 404.
    """
    http_method_names = ['post']

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva.objects.select_related('oferta'), pk=pk, ong=request.user.ong)
        try:
            reserva = services.cancelar_reserva(reserva, CanceladaPor.ONG)
        except ValidationError as erro:
            messages.error(request, ' '.join(erro.messages))
        else:
            messages.success(request, _mensagem_reserva_cancelada(reserva))
        return redirect('colheita:minhas_reservas')


class CancelarReservaDoAgricultorView(AgricultorRequeridoMixin, View):
    """Cancelar reserva de uma oferta do agricultor, Tela 13 (BL-47, Gabriel). RF-24, UC-11, RNF-05.
    Só o agricultor dono da oferta; reserva de oferta de outro (ou inexistente) dá 404.
    """
    http_method_names = ['post']

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva.objects.select_related('oferta'), pk=pk,
                                    oferta__agricultor=request.user.perfil_pessoa)
        try:
            reserva = services.cancelar_reserva(reserva, CanceladaPor.AGRICULTOR)
        except ValidationError as erro:
            messages.error(request, ' '.join(erro.messages))
        else:
            messages.success(request, _mensagem_reserva_cancelada(reserva))
        return redirect('colheita:minhas_ofertas')


class CancelarOfertaView(AgricultorRequeridoMixin, View):
    """Cancelar oferta, Tela 13 (BL-47, Gabriel). RF-24, UC-11, RNF-05.
    Só o agricultor dono; oferta de outro (ou inexistente) dá 404.
    """
    http_method_names = ['post']

    def post(self, request, pk):
        oferta = get_object_or_404(Oferta, pk=pk, agricultor=request.user.perfil_pessoa)
        try:
            oferta = services.cancelar_oferta(oferta)
        except ValidationError as erro:
            messages.error(request, ' '.join(erro.messages))
        else:
            messages.success(request, f'Oferta de {oferta.produto} cancelada. Ela saiu da lista das ONGs.')
        return redirect('colheita:minhas_ofertas')


def _mensagem_reserva_cancelada(reserva):
    produto = reserva.oferta.produto
    if reserva.oferta.vencida:
        return f'Reserva de {produto} cancelada.'
    return f'Reserva de {produto} cancelada. A quantidade voltou ao saldo da oferta.'
