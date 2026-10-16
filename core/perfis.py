"""Descobre o perfil de quem está navegando.

Perfis possíveis: visitante, pessoa (doador/voluntário), agricultor, ong, ong-pendente, ong-reprovada.
Enquanto as telas estão em mock (camada 0), o perfil pode ser simulado pela sessão em DEBUG
(veja core.views.definir_perfil_mock). Na camada 1, ele vem do usuário logado.
"""
from django.conf import settings

PERFIS = ['visitante', 'pessoa', 'agricultor', 'ong', 'ong-pendente', 'ong-reprovada']
CHAVE_SESSAO_MOCK = 'perfil_mock'


def perfil_da_requisicao(request):
    if settings.DEBUG:
        simulado = request.session.get(CHAVE_SESSAO_MOCK)
        if simulado in PERFIS:
            return simulado

    usuario = request.user
    if not usuario.is_authenticated:
        return 'visitante'

    if usuario.tipo_conta == 'ong':
        # A ONG só existe depois do BL-25; até lá, toda conta de ONG conta como pendente
        ong = getattr(usuario, 'ong', None)
        situacao = getattr(ong, 'situacao', 'pendente')
        return {'ativa': 'ong', 'reprovada': 'ong-reprovada'}.get(situacao, 'ong-pendente')

    # Conta de pessoa: agricultor tem precedência quando os dois perfis estão ativos (RN-25)
    perfil_pessoa = getattr(usuario, 'perfil_pessoa', None)
    if perfil_pessoa is not None and getattr(perfil_pessoa, 'eh_agricultor', False):
        return 'agricultor'
    return 'pessoa'


def eh_ong(perfil):
    return perfil.startswith('ong')


def destino_colheita(perfil):
    """Para onde o menu "Colheita Solidária" leva cada perfil (D-26, RN-25)."""
    return 'colheita:publicar' if perfil == 'agricultor' else 'colheita:ofertas'


def destino_minha_conta(perfil):
    if eh_ong(perfil):
        return 'ongs:minha_ong'
    if perfil == 'agricultor':
        return 'colheita:minhas_ofertas'
    return 'contas:contribuicoes'
