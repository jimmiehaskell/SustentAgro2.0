"""BL-36 parte 1 (Pedro): resumo do que já foi recebido de uma oferta. RF-25, RN-08, RN-09.

Usa objetos de exemplo (core.mocks_util), com os mesmos nomes de campo do model Reserva: a regra
funciona igual quando a oferta vier do banco (parte 2 da BL-36).
"""
from decimal import Decimal

from django.test import SimpleTestCase

from colheita.services import resumo_recebido
from core.mocks_util import lista, obj

ONG_A, ONG_B = obj(pk=1), obj(pk=2)


def _oferta(destino='doar', preco=None, reservas=()):
    return obj(destino=destino, preco_unitario=Decimal(preco) if preco else None, reservas=lista(*reservas))


def _reserva(ong, situacao, recebida=None):
    return obj(ong=ong, situacao=situacao, quantidade_recebida=Decimal(recebida) if recebida else None)


class ResumoRecebidoTest(SimpleTestCase):
    def test_soma_so_as_reservas_recebidas(self):
        oferta = _oferta(reservas=[_reserva(ONG_A, 'recebida', '150'), _reserva(ONG_B, 'recebida', '110'),
                                   _reserva(ONG_A, 'ativa'), _reserva(ONG_B, 'nao_recebida')])
        resumo = resumo_recebido(oferta)
        self.assertEqual(resumo['quantidade_recebida'], Decimal('260'))
        self.assertEqual(resumo['ongs'], 2)

    def test_mesma_ong_conta_uma_vez(self):
        oferta = _oferta(reservas=[_reserva(ONG_A, 'recebida', '10'), _reserva(ONG_A, 'recebida', '5')])
        self.assertEqual(resumo_recebido(oferta)['ongs'], 1)

    def test_renda_em_oferta_de_venda(self):  # RN-09: preço × recebido
        oferta = _oferta('vender', '0.80', [_reserva(ONG_A, 'recebida', '150'), _reserva(ONG_B, 'recebida', '110')])
        self.assertEqual(resumo_recebido(oferta)['renda'], Decimal('208.00'))

    def test_doacao_nao_tem_renda(self):
        oferta = _oferta(reservas=[_reserva(ONG_A, 'recebida', '20')])
        self.assertIsNone(resumo_recebido(oferta)['renda'])

    def test_oferta_sem_nada_recebido(self):
        resumo = resumo_recebido(_oferta('vender', '2.50', [_reserva(ONG_A, 'ativa')]))
        self.assertEqual(resumo, {'quantidade_recebida': Decimal('0'), 'ongs': 0, 'renda': Decimal('0.00')})
