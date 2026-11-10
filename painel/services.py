"""Cálculos do painel de impacto (BL-37, Pedro). Só lê dados; nunca grava."""
from collections import Counter
from datetime import date
from decimal import Decimal

from django.utils import timezone
from django.utils.formats import date_format

from colheita.choices import SituacaoReserva, Unidade


def indicadores():
    """RF-29. Devolve um objeto (ou dict) com:
    - kg_salvos: soma de quantidade_recebida das reservas recebidas de ofertas em kg (RN-08, P-01);
    - familias_atendidas: soma de familias_por_mes das ONGs ativas (RN-10);
    - renda_gerada: soma de preco_unitario × quantidade_recebida das ofertas de venda recebidas (RN-09);
    - ongs_ativas: quantidade de ONGs com situacao = ativa (RN-11).
    Testes: painel/tests/test_indicadores.py
    """
    raise NotImplementedError('BL-37')


def kg_por_mes():
    """RF-30, RN-23, E-09. Lista de (mês, kg) agrupada pela data de recebida_em, no fuso de Brasília."""
    raise NotImplementedError('BL-37')


def fatia_por_ods():
    """RF-31, RN-07, E-10. Lista de (ods, percentual). Cada ação confirmada conta uma vez para cada ODS da
    ONG que a recebeu; o percentual de um ODS é a contagem dele dividida pela soma das contagens.
    Com só a camada 1 pronta, as ações são as reservas recebidas."""
    raise NotImplementedError('BL-37')


# ---------------------------------------------------------------------------------------------
# BL-37 parte 1: as contas do painel, sem banco. Recebem uma lista de reservas (do mock ou do model
# Reserva, com os mesmos nomes de campo). Na parte 2, kg_por_mes() e fatia_por_ods() só buscam as
# reservas no banco e chamam estas funções.
# ---------------------------------------------------------------------------------------------

def agrupar_kg_por_mes(reservas):
    """RF-30, RN-08, RN-23, E-09. Soma os kg recebidos por mês, pelo mês de recebida_em no horário de
    Brasília (TIME_ZONE do settings), e não no UTC em que o banco guarda.

    Só contam reservas recebidas de ofertas em kg. Devolve uma lista de (mês, kg) em ordem
    cronológica, com o mês abreviado em português ('out'), só com os meses que tiveram recebimento.
    Testes: painel/tests/test_calculos.py
    """
    kg_por_mes = {}
    for reserva in reservas:
        if reserva.situacao != SituacaoReserva.RECEBIDA or reserva.oferta.unidade != Unidade.KG:
            continue
        no_brasil = timezone.localtime(reserva.recebida_em)
        mes = (no_brasil.year, no_brasil.month)
        kg_por_mes[mes] = kg_por_mes.get(mes, Decimal('0')) + reserva.quantidade_recebida
    return [(date_format(date(ano, numero, 1), 'b'), kg) for (ano, numero), kg in sorted(kg_por_mes.items())]


def calcular_fatia_por_ods(reservas):
    """RF-31, RN-07, E-10. Cada reserva recebida conta uma vez para cada ODS da ONG que a recebeu; o
    percentual de um ODS é a contagem dele dividida pela soma das contagens, arredondado para inteiro.

    Devolve uma lista de (ods, percentual), do maior para o menor (empate: pelo número do ODS).
    Sem reservas recebidas, devolve lista vazia (o template mostra o estado vazio).
    Testes: painel/tests/test_calculos.py
    """
    contagem = Counter()
    ods_por_numero = {}
    for reserva in reservas:
        if reserva.situacao != SituacaoReserva.RECEBIDA:
            continue
        for ods in reserva.ong.ods.all():
            contagem[ods.numero] += 1
            ods_por_numero[ods.numero] = ods
    total = sum(contagem.values())
    if total == 0:
        return []
    fatias = [(ods_por_numero[numero], round(quantas * 100 / total)) for numero, quantas in contagem.items()]
    return sorted(fatias, key=lambda fatia: (-fatia[1], fatia[0].numero))
