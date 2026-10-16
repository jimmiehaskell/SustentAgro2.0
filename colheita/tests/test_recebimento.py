"""BL-35 (Gabriel, em dupla com Jimmie): RF-23, RN-17, RN-18, E-02, E-03.
Remova o @skip ao implementar colheita.services.confirmar_recebimento (depende de BL-34).
"""
from datetime import date, timedelta
from decimal import Decimal
from unittest import skip

from django.core.exceptions import ValidationError
from django.test import TestCase

from core.tests.fabricas import criar_oferta, criar_ong


@skip('Remova ao implementar o BL-35 (depois do BL-34)')
class ConfirmarRecebimentoTest(TestCase):
    def setUp(self):
        from colheita.services import confirmar_recebimento, reservar_oferta, saldo
        self.confirmar, self.saldo = confirmar_recebimento, saldo
        self.oferta = criar_oferta(quantidade='100', unidade='kg')
        self.reserva = reservar_oferta(self.oferta, criar_ong(), Decimal('50'))

    def test_recebimento_total(self):
        reserva = self.confirmar(self.reserva, Decimal('50'))
        self.assertEqual(reserva.situacao, 'recebida')
        self.assertEqual(reserva.quantidade_recebida, Decimal('50'))
        self.assertIsNotNone(reserva.recebida_em)

    def test_recebeu_menos_conta_so_o_recebido(self):
        reserva = self.confirmar(self.reserva, Decimal('48'))
        self.assertEqual(reserva.quantidade_recebida, Decimal('48'))
        self.assertEqual(self.saldo(self.oferta), Decimal('50'))  # a diferença não volta ao saldo

    def test_nao_aceita_mais_que_o_reservado(self):  # E-02
        with self.assertRaises(ValidationError):
            self.confirmar(self.reserva, Decimal('51'))

    def test_zero_e_nao_recebida_e_devolve_ao_saldo(self):  # E-03
        reserva = self.confirmar(self.reserva, Decimal('0'))
        self.assertEqual(reserva.situacao, 'nao_recebida')
        self.assertEqual(self.saldo(self.oferta), Decimal('100'))

    def test_oferta_vencida_ainda_aceita_confirmacao(self):  # RN-18, E-04
        self.oferta.colher_ate = date.today() - timedelta(days=1)
        self.oferta.save()
        reserva = self.confirmar(self.reserva, Decimal('50'))
        self.assertEqual(reserva.situacao, 'recebida')
