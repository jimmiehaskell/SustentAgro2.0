from django.shortcuts import redirect
from django.views.generic import TemplateView

from core.perfis import destino_minha_conta, perfil_da_requisicao
from contas import mocks as contas_mocks
from doacoes import mocks as doacoes_mocks
from ongs import mocks as ongs_mocks

TIPOS_CADASTRO = ('pessoa', 'agricultor', 'ong')


def minha_conta(request):
    """Leva cada perfil para a própria área (D-16). Visitante vai para o login."""
    perfil = perfil_da_requisicao(request)
    if perfil == 'visitante':
        return redirect('contas:entrar')
    return redirect(destino_minha_conta(perfil))


class CadastroView(TemplateView):
    """Tela 4 · Cadastro por perfil (BL-11, Vinicius). RF-07, RF-10, RF-33.
    MOCK: trocar na camada 1 (BL-28, BL-29) por formulários que criam a conta e já logam.
    """
    template_name = 'contas/cadastro.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipo = kwargs.get('tipo', 'pessoa')
        context['tipo'] = tipo if tipo in TIPOS_CADASTRO else 'pessoa'
        context['localidades'] = ongs_mocks.LOCALIDADES
        context['ods'] = ongs_mocks.ODS
        return context


class ContribuicoesView(TemplateView):
    """Tela 14 · Minhas contribuições (BL-13, Vinicius). RF-26, RF-08.
    MOCK: trocar na camada 2 (BL-45). Na camada 1, proteger com DoadorRequeridoMixin.
    """
    template_name = 'contas/contribuicoes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contribuicoes'] = doacoes_mocks.CONTRIBUICOES_DA_PESSOA
        context['pessoa'] = contas_mocks.PERFIL_PESSOA
        return context
