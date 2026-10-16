from django.conf import settings

from core.perfis import PERFIS, destino_colheita, destino_minha_conta, eh_ong, perfil_da_requisicao

NOMES_MOCK = {
    'pessoa': 'Mariana Costa',
    'agricultor': 'Antônio Ribeiro',
    'ong': 'Cozinha Solidária Sol Nascente',
    'ong-pendente': 'Horta Comunitária Vila Planalto',
    'ong-reprovada': 'Instituto Raízes do Planalto',
}


def perfil(request):
    """Disponibiliza o perfil atual em todos os templates (menu, botões, avisos)."""
    atual = perfil_da_requisicao(request)
    if request.user.is_authenticated:
        nome = request.user.get_full_name() or request.user.username
    else:
        nome = NOMES_MOCK.get(atual)
    return {
        'modo_debug': settings.DEBUG,
        'perfil': atual,
        'perfil_eh_ong': eh_ong(atual),
        'perfil_nome': nome,
        'perfis_mock': PERFIS,
        'url_colheita': destino_colheita(atual),
        'url_minha_conta': destino_minha_conta(atual),
    }
