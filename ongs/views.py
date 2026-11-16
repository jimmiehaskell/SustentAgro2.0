from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from core.perfis import perfil_da_requisicao
from ongs import mocks
from ongs.choices import TipoNecessidade
from ongs.models import Ong
from ongs.services import CAMPOS_DA_NECESSIDADE, criar_necessidade, editar_necessidade, encerrar_necessidade
from core.mixins import OngAtivaRequeridaMixin  # troque pelo módulo que o git grep indicou

class ListaOngsView(TemplateView):
    """Tela 2 · Lista de ONGs (BL-15, Júlia). RF-04, RF-05, UC-01.
    MOCK: trocar na camada 1 (BL-30) por Ong.objects ativas com os filtros da querystring.
    """
    template_name = 'ongs/lista.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET
        filtros = {'q': q.get('q', ''), 'ods': q.get('ods', ''), 'tipo': q.get('tipo', ''),
                   'cidade': q.get('cidade', '')}
        ongs = [ong for ong in mocks.ONGS if ong.situacao == 'ativa']
        # MOCK: filtros em memória, combinados por E lógico (RF-04); no BL-30 viram filtros da consulta
        if filtros['q']:
            termo = filtros['q'].casefold()
            ongs = [o for o in ongs
                    if any(
                        termo in campo.casefold()
                          for campo in (o.nome, o.nome_curto, o.slogan, o.descricao, o.localidade.nome,*(ods.nome for ods in o.ods))
                          )]
        if filtros['ods'].isdigit():
            ongs = [o for o in ongs if any(ods.numero == int(filtros['ods']) for ods in o.ods)]
        if filtros['tipo'] in TipoNecessidade.values:
            ongs = [o for o in ongs if getattr(o, f"aceita_{filtros['tipo']}")]
        if filtros['cidade']:
            ongs = [o for o in ongs if o.localidade.nome == filtros['cidade']]
        context.update(filtros=filtros, ongs=[(o, mocks.precisa_agora(o)) for o in ongs],
                       ods=mocks.ODS, tipos=TipoNecessidade.choices, localidades=mocks.LOCALIDADES)
        return context


class DetalheOngView(TemplateView):
    """Tela 3 · Página da ONG (BL-06, tela-exemplo de Jimmie). RF-06, RN-21.
    MOCK: trocar na camada 1 (BL-30) por get_object_or_404(Ong, pk=pk, situacao='ativa').
    """
    template_name = 'ongs/detalhe.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ong = mocks.ong_por_pk(kwargs['pk'])
        if ong is None:
            raise Http404('ONG não encontrada.')
        context['ong'] = ong
        context['necessidades'] = [n for n in ong.necessidades.all() if n.situacao != 'encerrada']
        return context


class MinhaOngView(TemplateView):
    """Tela 9 · Minha conta da ONG: situação e perfil (BL-16, Júlia). RF-11, RF-12, RN-20.
    MOCK: trocar na camada 1 (BL-31). Proteger com OngRequeridaMixin (aceita pendente e reprovada).
    """
    template_name = 'ongs/minha_ong.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # MOCK: a ONG vem do perfil simulado; no BL-31 vira a ONG do usuário logado
        ong = {'ong-pendente': mocks.ONG_PENDENTE, 'ong-reprovada': mocks.ONG_REPROVADA}.get(
            perfil_da_requisicao(self.request), mocks.ONGS[0])
        context.update(ong=ong, ods=mocks.ODS, localidades=mocks.LOCALIDADES, aba='perfil')
        return context


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
