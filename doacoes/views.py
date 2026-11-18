from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from contas.choices import TipoConta
from core.mixins import DoadorRequeridoMixin
from doacoes import mocks
from doacoes.choices import TipoContribuicao
from doacoes.forms import InscricaoVoluntariadoForm, PromessaItensForm
from doacoes.services import registrar_contribuicao
from ongs import mocks as ongs_mocks
from ongs.choices import SituacaoNecessidade, SituacaoOng
from ongs.models import Necessidade, Ong

TIPOS = TipoContribuicao.values


class ContribuirView(DoadorRequeridoMixin, TemplateView):
    """Tela 15: itens e voluntariado reais (BL-42); dinheiro segue demonstrativo (BL-43)."""
    template_name = 'doacoes/contribuir.html'

    def dispatch(self, request, *args, **kwargs):
        self.tipo = kwargs['tipo']
        if self.tipo not in TIPOS:
            raise Http404
        if self.tipo == TipoContribuicao.DINHEIRO:
            return TemplateView.dispatch(self, request, *args, **kwargs)
        # O DEBUG pode simular o perfil visual, mas nunca autoriza gravação.
        if request.user.is_authenticated and (request.user.tipo_conta != TipoConta.PESSOA or not getattr(
                getattr(request.user, 'perfil_pessoa', None), 'eh_doador', False)):
            raise PermissionDenied('Esta página exige um perfil de doador.')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipo = self.tipo
        if tipo == TipoContribuicao.DINHEIRO:
            ong = ongs_mocks.ong_por_pk(kwargs['ong_pk'])
            if ong is None or not ong.aceita_dinheiro:
                raise Http404
            necessidades = [(n, n.meta - n.confirmado) for n in ong.necessidades
                            if n.situacao == 'aberta' and n.tipo == tipo]
        else:
            ong = get_object_or_404(Ong, pk=kwargs['ong_pk'], situacao=SituacaoOng.ATIVA)
            if not getattr(ong, f'aceita_{tipo}'):
                raise Http404
            necessidades = [(n, n.meta - n.confirmado) for n in Necessidade.objects.filter(
                ong=ong, tipo=tipo, situacao=SituacaoNecessidade.ABERTA)]
        context.update(ong=ong, tipo=tipo, necessidades=necessidades)
        return context

    def post(self, request, *args, **kwargs):
        if self.tipo == TipoContribuicao.DINHEIRO:
            raise Http404
        context = self.get_context_data(**kwargs)
        formulario = PromessaItensForm(request.POST) if self.tipo == TipoContribuicao.ITENS else InscricaoVoluntariadoForm(request.POST)
        if not formulario.is_valid():
            context['erros'] = 'Confira a necessidade e a quantidade informadas.'
            return self.render_to_response(context)
        necessidade = get_object_or_404(Necessidade, pk=formulario.cleaned_data['necessidade'])
        try:
            registrar_contribuicao(request.user.perfil_pessoa, context['ong'], self.tipo,
                                   formulario.cleaned_data.get('quantidade', 1), necessidade)
        except ValidationError as erro:
            context['erros'] = ' '.join(erro.messages)
            return self.render_to_response(context)
        messages.success(request, 'Promessa registrada e aguardando confirmação da ONG.' if self.tipo == TipoContribuicao.ITENS
                         else 'Inscrição registrada e aguardando confirmação da ONG.')
        return redirect('doacoes:contribuir', ong_pk=context['ong'].pk, tipo=self.tipo)


class AConfirmarView(TemplateView):
    """Tela 12 · Doações a confirmar pela ONG (BL-22, Pedro). RF-16, RN-02. Camada 2 (BL-44).
    MOCK: trocar na camada 2. Proteger com OngAtivaRequeridaMixin.
    """
    template_name = 'doacoes/a_confirmar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ong'] = ongs_mocks.ONGS[0]  # MOCK: a ONG logada (Cozinha Solidária Sol Nascente)
        context['pendentes'] = mocks.PENDENTES_DA_ONG
        context['aba'] = 'doacoes'
        return context
