"""Cálculos do painel de impacto (BL-37, Pedro). Só lê dados; nunca grava."""
from collections import Counter
from datetime import date
from decimal import Decimal

from django.db.models import DecimalField, F, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.formats import date_format

from colheita.choices import Destino, SituacaoReserva, Unidade
from colheita.models import Reserva
from ongs.choices import SituacaoOng
from ongs.models import Ong

ZERO = Decimal('0')


def indicadores():
    """RF-29. Devolve um objeto (ou dict) com:
    - kg_salvos: soma de quantidade_recebida das reservas recebidas de ofertas em kg (RN-08, P-01);
    - familias_atendidas: soma de familias_por_mes das ONGs ativas (RN-10);
    - renda_gerada: soma de preco_unitario × quantidade_recebida das ofertas de venda recebidas (RN-09);
    - ongs_ativas: quantidade de ONGs com situacao = ativa (RN-11).
    Testes: painel/tests/test_indicadores.py
    """
    recebidas = Reserva.objects.filter(situacao=SituacaoReserva.RECEBIDA)
    ongs_ativas = Ong.objects.filter(situacao=SituacaoOng.ATIVA)

    kg_salvos = recebidas.filter(oferta__unidade=Unidade.KG).aggregate(
        total=Coalesce(Sum('quantidade_recebida'), ZERO))['total']
    renda_gerada = recebidas.filter(oferta__destino=Destino.VENDER).aggregate(
        total=Coalesce(Sum(F('quantidade_recebida') * F('oferta__preco_unitario'),
                           output_field=DecimalField(max_digits=14, decimal_places=2)), ZERO))['total']
    familias = ongs_ativas.aggregate(total=Coalesce(Sum('familias_por_mes'), 0))['total']

    return {
        'kg_salvos': kg_salvos,
        'familias_atendidas': familias,
        'renda_gerada': renda_gerada.quantize(Decimal('0.01')),
        'ongs_ativas': ongs_ativas.count(),
    }


def kg_por_mes():
    """RF-30, RN-23, E-09. Lista de (mês, kg) agrupada pela data de recebida_em, no fuso de Brasília.
    Busca no banco só as reservas recebidas em kg e deixa a conta para agrupar_kg_por_mes (parte 1)."""
    reservas = (Reserva.objects.filter(situacao=SituacaoReserva.RECEBIDA, oferta__unidade=Unidade.KG)
                .select_related('oferta'))
    return agrupar_kg_por_mes(reservas)


def fatia_por_ods():
    """RF-31, RN-07, E-10. Lista de (ods, percentual). Cada ação confirmada conta uma vez para cada ODS da
    ONG que a recebeu; o percentual de um ODS é a contagem dele dividida pela soma das contagens.
    Com só a camada 1 pronta, as ações são as reservas recebidas.
    Busca no banco as reservas recebidas com os ODS da ONG e deixa a conta para calcular_fatia_por_ods (parte 1)."""
    reservas = (Reserva.objects.filter(situacao=SituacaoReserva.RECEBIDA)
                .select_related('ong').prefetch_related('ong__ods'))
    return calcular_fatia_por_ods(reservas)


# ---------------------------------------------------------------------------------------------
# As contas do painel (BL-37 parte 1). Recebem uma lista de reservas com os nomes de campo do model
# Reserva; kg_por_mes() e fatia_por_ods(), acima, buscam as reservas no banco e chamam estas funções.
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
