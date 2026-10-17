from django.conf import settings
from django.db import connection
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import TemplateView

from core.perfis import CHAVE_SESSAO_MOCK, PERFIS
from ongs import mocks as ongs_mocks

EQUIPE = [
    'Brayan Aragão Pletsch', 'Caio Vinício Nunes Vilarouca', 'Gabriel Ribeiro de Carvalho',
    'Guilherme de Melo Lucas', 'Jimmie Haskell Gonçalves da Silva', 'João Matheus Bezerra',
    'João Vitor de Freitas Silva', 'Júlia Sernagiotto Barbosa', 'Pedro Freire de Farias',
    'Vinicius Pereira Souza', 'Vitor Gomes Araújo',
]


class InicioView(TemplateView):
    """Tela 1 · Início (BL-14, Júlia). RF-01, RF-02, RF-03, RF-34."""
    template_name = 'core/inicio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # MOCK: trocar na camada 1 (BL-30) por Ods com a contagem de ONGs ativas e Ong.objects ativas
        ongs = ongs_mocks.ONGS
        context['ods_com_contagem'] = [
            (ods, sum(1 for ong in ongs if ods in ong.ods)) for ods in ongs_mocks.ODS
        ]
        context['ongs'] = ongs
        context['equipe'] = EQUIPE
        return context


def definir_perfil_mock(request, perfil):
    """Só em DEBUG: guarda na sessão um perfil simulado, para navegar pelas telas mock.
    Use /mock/perfil/ong/?proximo=/colheita/ (perfis: visitante, pessoa, agricultor, ong,
    ong-pendente, ong-reprovada). Some quando DEBUG=False.
    """
    if not settings.DEBUG or perfil not in PERFIS:
        raise Http404
    if perfil == 'visitante':
        request.session.pop(CHAVE_SESSAO_MOCK, None)
    else:
        request.session[CHAVE_SESSAO_MOCK] = perfil
    proximo = request.GET.get('proximo', '/')
    if not url_has_allowed_host_and_scheme(proximo, allowed_hosts={request.get_host()}):
        proximo = '/'
    return redirect(proximo)


def saude(request):
    """Usado pelo healthcheck do container e pela conferência após cada publicação.
    Responde 200 quando a aplicação e o banco estão de pé; 503 se o banco não responde."""
    try:
        connection.ensure_connection()
    except Exception:
        return HttpResponse('banco: erro', status=503, content_type='text/plain; charset=utf-8')
    return HttpResponse('ok', content_type='text/plain; charset=utf-8')
