from django.http import Http404
from django.views.generic import TemplateView

from ongs import mocks
from ongs.choices import TipoNecessidade


class ListaOngsView(TemplateView):
    """
    MOCK: trocar na camada 1 (BL-30) por Ong.objects ativas com os filtros da querystring.
    """
    template_name = 'ongs/lista.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET
        filtros = {'q': q.get('q', ''), 'ods': q.get('ods', ''), 'tipo': q.get('tipo', ''),
                   'cidade': q.get('cidade', '')}
        ongs = list(mocks.ONGS)
        # MOCK: filtros em memória, combinados por E lógico (RF-04); no BL-30 viram filtros da consulta
        if filtros['q']:
            termo = filtros['q'].casefold()
            ongs = [o for o in ongs
                    if any(termo in campo.casefold() for campo in (o.nome, o.nome_curto, o.slogan, o.descricao))]
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
        context.update(ong=mocks.ONGS[0], ods=mocks.ODS, localidades=mocks.LOCALIDADES, aba='perfil')
        return context


class NecessidadesView(TemplateView):
    """Tela 10 · Necessidades da ONG (BL-16, Júlia). RF-13, RN-21. Camada 2 (BL-41).
    MOCK: trocar na camada 2. Proteger com OngAtivaRequeridaMixin.
    """
    template_name = 'ongs/necessidades.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(ong=mocks.ONGS[0], aba='necessidades')
        return context
