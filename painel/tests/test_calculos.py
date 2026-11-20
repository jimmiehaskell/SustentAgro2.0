"""BL-37 parte 1 (Pedro): as contas do painel, sem banco. RF-30, RF-31, RN-07, RN-08, RN-23, E-09, E-10.

Usa objetos de exemplo (core.mocks_util) com os mesmos nomes de campo do model Reserva, então as
contas são as mesmas quando as reservas vierem do banco (parte 2).
"""
from datetime import datetime, timezone as tz
from decimal import Decimal

from django.test import SimpleTestCase

from core.mocks_util import lista, obj
from painel.services import agrupar_kg_por_mes, calcular_fatia_por_ods

ODS_1, ODS_2, ODS_10 = obj(numero=1), obj(numero=2), obj(numero=10)
SOL = obj(ods=lista(ODS_1, ODS_2))          # ONG com dois ODS
PRATO = obj(ods=lista(ODS_2, ODS_10))
EM_KG, EM_UNIDADES = obj(unidade='kg'), obj(unidade='un')


def _reserva(recebida_em_utc, kg, oferta=EM_KG, ong=SOL, situacao='recebida'):
    return obj(situacao=situacao, oferta=oferta, ong=ong, quantidade_recebida=Decimal(kg),
               recebida_em=recebida_em_utc)


def _utc(ano, mes, dia, hora=12):
    return datetime(ano, mes, dia, hora, tzinfo=tz.utc)   # o banco guarda as datas em UTC


class AgruparKgPorMesTest(SimpleTestCase):
    def test_soma_por_mes_em_ordem(self):
        reservas = [_reserva(_utc(2026, 10, 5), '100'), _reserva(_utc(2026, 9, 20), '40'),
                    _reserva(_utc(2026, 10, 25), '30')]
        self.assertEqual(agrupar_kg_por_mes(reservas), [('set', Decimal('40')), ('out', Decimal('130'))])

    def test_usa_o_mes_no_horario_de_brasilia(self):  # RN-23, E-09
        # 1º/11 à 1h em UTC = 31/10 às 22h em Brasília: conta em outubro
        reservas = [_reserva(_utc(2026, 11, 1, hora=1), '50')]
        self.assertEqual(agrupar_kg_por_mes(reservas), [('out', Decimal('50'))])

    def test_so_conta_recebidas_em_kg(self):  # RN-08, P-01
        reservas = [_reserva(_utc(2026, 10, 5), '100'),
                    _reserva(_utc(2026, 10, 6), '30', oferta=EM_UNIDADES),     # unidades não são kg
                    _reserva(_utc(2026, 10, 7), '20', situacao='ativa')]       # ainda não chegou
        self.assertEqual(agrupar_kg_por_mes(reservas), [('out', Decimal('100'))])

    def test_sem_reservas(self):
        self.assertEqual(agrupar_kg_por_mes([]), [])


class CalcularFatiaPorOdsTest(SimpleTestCase):
    def test_cada_reserva_conta_para_cada_ods_da_ong(self):  # RN-07
        # SOL (ODS 1 e 2) recebeu 2 vezes; PRATO (ODS 2 e 10) recebeu 1 vez.
        # Contagens: ODS 2 = 3, ODS 1 = 2, ODS 10 = 1. Total = 6.
        reservas = [_reserva(_utc(2026, 10, 1), '10'), _reserva(_utc(2026, 10, 2), '10'),
                    _reserva(_utc(2026, 10, 3), '10', ong=PRATO)]
        fatias = [(ods.numero, pct) for ods, pct in calcular_fatia_por_ods(reservas)]
        self.assertEqual(fatias, [(2, 50), (1, 33), (10, 17)])

    def test_reserva_nao_recebida_nao_conta(self):  # E-10: só as recebidas
        reservas = [_reserva(_utc(2026, 10, 1), '10', ong=PRATO),
                    _reserva(_utc(2026, 10, 2), '10', situacao='ativa')]
        fatias = [(ods.numero, pct) for ods, pct in calcular_fatia_por_ods(reservas)]
        self.assertEqual(fatias, [(2, 50), (10, 50)])

    def test_sem_reservas_recebidas_da_lista_vazia(self):
        self.assertEqual(calcular_fatia_por_ods([_reserva(_utc(2026, 10, 1), '10', situacao='ativa')]), [])
