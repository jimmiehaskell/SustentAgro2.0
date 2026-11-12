from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from core.perfis import perfil_da_requisicao
from ongs import mocks, services
from ongs.choices import TipoNecessidade
from contas.models import Localidade


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
        ongs = services.filtrar_ongs(**filtros)
        # MOCK: filtros em memória, combinados por E lógico (RF-04); no BL-30 viram filtros da consulta
        context.update(filtros=filtros, ongs=[(o, services.precisa_agora(o)) for o in ongs],
                       ods=services.ods_com_contagem(), tipos=TipoNecessidade.choices,
                       localidades=Localidade.objects.order_by('nome'))
        return context


class DetalheOngView(TemplateView):
    """Tela 3 · Página da ONG (BL-06, tela-exemplo de Jimmie). RF-06, RN-21.
    MOCK: trocar na camada 1 (BL-30) por get_object_or_404(Ong, pk=pk, situacao='ativa').
    """
    template_name = 'ongs/detalhe.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ong = get_object_or_404(services.ongs_ativas(), pk=kwargs['pk'])
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


class NecessidadesView(TemplateView):
    """Tela 10 · Necessidades da ONG (BL-16, Júlia). RF-13, RN-21. Camada 2 (BL-41).
    MOCK: trocar na camada 2. Proteger com OngAtivaRequeridaMixin.
    """
    template_name = 'ongs/necessidades.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(ong=mocks.ONGS[0], aba='necessidades', tipos=TipoNecessidade.choices)
        return context
