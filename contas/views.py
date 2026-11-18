from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView

from core.perfis import CHAVE_SESSAO_MOCK, destino_minha_conta, perfil_da_requisicao
from contas.forms import ContaCadastroForm, OngCadastroForm, PessoaCadastroForm
from contas.services import cadastrar_usuario
from contas import mocks as contas_mocks
from doacoes import mocks as doacoes_mocks

TIPOS_CADASTRO = ('pessoa', 'agricultor', 'ong')


def minha_conta(request):
    """Leva cada perfil para a própria área (D-16). Visitante vai para o login."""
    perfil = perfil_da_requisicao(request)
    if perfil == 'visitante':
        return redirect('contas:entrar')
    return redirect(destino_minha_conta(perfil))


class CadastroView(TemplateView):
    """Tela 4 · Cadastro real e login automático (BL-28)."""
    template_name = 'contas/cadastro.html'

    def dispatch(self, request, *args, **kwargs):
        self.tipo = kwargs.get('tipo', 'pessoa')
        if self.tipo not in TIPOS_CADASTRO:
            raise Http404('Perfil de cadastro inválido.')
        if request.user.is_authenticated:
            return redirect('contas:minha_conta')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dados = self.request.POST if self.request.method == 'POST' else None
        context['tipo'] = self.tipo
        context.setdefault('form_conta', ContaCadastroForm(dados))
        context.setdefault('form_perfil', OngCadastroForm(dados) if self.tipo == 'ong'
                           else PessoaCadastroForm(dados, agricultor=self.tipo == 'agricultor'))
        return context

    def post(self, request, *args, **kwargs):
        contexto = self.get_context_data(**kwargs)
        conta, perfil = contexto['form_conta'], contexto['form_perfil']
        conta_valida, perfil_valido = conta.is_valid(), perfil.is_valid()
        if conta_valida and perfil_valido:
            try:
                usuario = cadastrar_usuario(conta, perfil)
            except ValidationError:
                if not conta.errors and not perfil.errors:
                    conta.add_error(None, 'Confira os dados do cadastro.')
            except IntegrityError:
                conta.add_error(None, 'Não foi possível concluir o cadastro. Confira os dados e as duplicidades.')
            else:
                request.session.pop(CHAVE_SESSAO_MOCK, None)
                login(request, usuario)
                return redirect('contas:minha_conta')
        return self.render_to_response(contexto)


class EntrarView(LoginView):
    template_name = 'contas/entrar.html'

    def form_valid(self, form):
        self.request.session.pop(CHAVE_SESSAO_MOCK, None)
        return super().form_valid(form)


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
