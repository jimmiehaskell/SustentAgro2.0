from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from contas.models import Localidade
from core.mixins import OngAtivaRequeridaMixin, OngRequeridaMixin
from ongs import services
from ongs.choices import TipoNecessidade
from ongs.forms import PerfilOngForm
from ongs.models import Ods, Ong
from ongs.services import CAMPOS_DA_NECESSIDADE, criar_necessidade, editar_necessidade, encerrar_necessidade


class ListaOngsView(TemplateView):
    """Tela 2 · Lista de ONGs (BL-15, Júlia). RF-04, RF-05, UC-01.
    MOCK: trocar na camada 1 (BL-30) por Ong.objects ativas com os filtros da querystring."""
    template_name = 'ongs/lista.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET
        filtros = {'q': q.get('q', ''), 'ods': q.get('ods', ''), 'tipo': q.get('tipo', ''),
                   'cidade': q.get('cidade', '')}
        ongs = services.buscar_ongs(filtros['q'], filtros['ods'], filtros['tipo'], filtros['cidade'])
        context.update(filtros=filtros, ongs=[(o, services.precisa_agora(o)) for o in ongs],
                       ods=Ods.objects.all(), tipos=TipoNecessidade.choices,
                       localidades=Localidade.objects.order_by('nome'))
        return context


class DetalheOngView(TemplateView):
    """Tela 3 · Página da ONG (BL-06, tela-exemplo de Jimmie). RF-06, RN-21.
    MOCK: trocar na camada 1 (BL-30) por get_object_or_404(Ong, pk=pk, situacao='ativa').
    """
    template_name = 'ongs/detalhe.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ong = get_object_or_404(services.ongs_ativas(), pk=kwargs['pk'])  # RN-01: pendente/desativada = 404
        context['ong'] = ong
        context['necessidades'] = ong.necessidades.exclude(situacao='encerrada')
        return context


class MinhaOngView(OngRequeridaMixin, UpdateView):
    """Tela 9 · Minha conta da ONG: situação e perfil (BL-16, BL-31, Júlia). RF-11, RF-12, RN-20, RNF-05.
    A ONG edita o próprio perfil; pendente e reprovada também editam (OngRequeridaMixin).
    """
    template_name = 'ongs/minha_ong.html'
    form_class = PerfilOngForm
    success_url = reverse_lazy('ongs:minha_ong')

    def get_object(self, queryset=None):
        # RNF-05: a ONG vem sempre do usuário logado, nunca de id na URL ou no POST
        return get_object_or_404(Ong, usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aba'] = 'perfil'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado.')
        return super().form_valid(form)


class NecessidadesView(OngAtivaRequeridaMixin, TemplateView):
    """Tela 10 · Necessidades da ONG (BL-16, BL-41, Júlia). RF-13, RN-21, UC-04, RNF-05.
    A ONG é sempre a do usuário logado; as regras ficam em ongs.services.
    """
    template_name = 'ongs/necessidades.html'

    def _ong(self):
        # RNF-05: nunca um id vindo da URL ou do POST
        return get_object_or_404(Ong, usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ong = self._ong()
        context.update(ong=ong, necessidades=ong.necessidades.all(), aba='necessidades',
                       tipos=TipoNecessidade.choices)
        return context

    def post(self, request, *args, **kwargs):
        ong = self._ong()
        acao = request.POST.get('acao')
        dados = {campo: request.POST.get(campo, '').strip() for campo in CAMPOS_DA_NECESSIDADE
                 if campo in request.POST}
        if 'meta' in dados:
            dados['meta'] = dados['meta'].replace(',', '.')  # "60,5" digitado em português
        try:
            if acao == 'criar':
                criar_necessidade(ong, dados)
                messages.success(request, 'Necessidade criada.')
            elif acao in ('editar', 'encerrar'):
                pk = request.POST.get('necessidade', '')
                if not pk.isdecimal():
                    raise Http404('Necessidade não encontrada.')
                # RNF-05: só entre as necessidades da própria ONG; de outra ONG dá 404
                necessidade = get_object_or_404(ong.necessidades.all(), pk=pk)
                if acao == 'editar':
                    editar_necessidade(necessidade, dados)
                    messages.success(request, 'Necessidade atualizada.')
                else:
                    encerrar_necessidade(necessidade)
                    messages.success(request, 'Necessidade encerrada.')
            else:
                raise Http404('Ação desconhecida.')
        except ValidationError as erro:
            for mensagem in erro.messages:
                messages.error(request, mensagem)
        return redirect(request.path)
