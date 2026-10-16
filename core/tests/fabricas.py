"""Fábricas de dados para os testes (camada 1).

Os imports dos models ficam dentro das funções porque os models ainda não existem no esqueleto:
assim, os testes marcados com skip não quebram enquanto o item não é implementado.
Os nomes de campo seguem o modelo de dados (docs/modelo-de-dados.pdf).
"""
from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone

COORDENADAS = {
    'Ceilândia': ('-15.819700', '-48.108300'),
    'Brazlândia': ('-15.675800', '-48.200300'),
    'Planaltina': ('-15.621400', '-47.649200'),
    'Gama': ('-16.018100', '-48.061400'),
}

_contador = {'n': 0}


def _proximo():
    _contador['n'] += 1
    return _contador['n']


def criar_usuario(tipo_conta='pessoa', **campos):
    from contas.models import Usuario
    n = _proximo()
    return Usuario.objects.create_user(username=campos.pop('username', f'usuario{n}'), password='senha-de-teste-123',
                                       tipo_conta=tipo_conta, **campos)


def criar_localidade(nome='Ceilândia'):
    from contas.models import Localidade
    lat, lon = COORDENADAS[nome]
    localidade, _ = Localidade.objects.get_or_create(
        nome=nome, defaults={'uf': 'DF', 'latitude': Decimal(lat), 'longitude': Decimal(lon)})
    return localidade


def criar_agricultor(localidade='Brazlândia', **campos):
    from contas.models import PerfilPessoa
    return PerfilPessoa.objects.create(
        usuario=criar_usuario('pessoa'), nome_completo=campos.pop('nome_completo', 'Antônio Ribeiro'),
        telefone='(61) 98123-4567', eh_agricultor=True, localidade=criar_localidade(localidade), **campos)


def criar_doador(**campos):
    from contas.models import PerfilPessoa
    return PerfilPessoa.objects.create(usuario=criar_usuario('pessoa'), nome_completo='Mariana Costa',
                                       eh_doador=True, **campos)


def criar_ods(numero=2):
    from ongs.models import Ods
    ods, _ = Ods.objects.get_or_create(numero=numero, defaults={'nome': f'ODS {numero}', 'cor': '#DDA63A'})
    return ods


def criar_ong(situacao='ativa', localidade='Ceilândia', familias_por_mes=100, ods=(2,), **campos):
    from ongs.models import Ong
    n = _proximo()
    ong = Ong.objects.create(
        usuario=criar_usuario('ong'), nome=f'ONG de teste {n}', nome_curto=f'Teste {n}',
        cnpj=campos.pop('cnpj', f'{n:014d}'), telefone='(61) 3333-0000', email_contato=f'ong{n}@exemplo.org',
        familias_por_mes=familias_por_mes, situacao=situacao, localidade=criar_localidade(localidade), **campos)
    ong.ods.set([criar_ods(numero) for numero in ods])
    return ong


def criar_oferta(agricultor=None, quantidade='100', unidade='kg', destino='doar', preco_unitario=None,
                 localidade='Brazlândia', colher_ate=None, ong_destino=None, **campos):
    from colheita.models import Oferta
    agora = timezone.now()
    return Oferta.objects.create(
        agricultor=agricultor or criar_agricultor(localidade), categoria=campos.pop('categoria', 'hortalicas'),
        produto=campos.pop('produto', 'Alface crespa'), quantidade=Decimal(quantidade), unidade=unidade,
        colher_ate=colher_ate or date.today() + timedelta(days=5), localidade=criar_localidade(localidade),
        estado=campos.pop('estado', 'excedente'), destino=destino,
        preco_unitario=Decimal(preco_unitario) if preco_unitario else None,
        local_retirada='Chácara 12, Núcleo Rural Alexandre Gusmão', transporte='ong_busca',
        ong_destino=ong_destino, aberta_a_todas_em=agora + timedelta(hours=48) if ong_destino else agora, **campos)
