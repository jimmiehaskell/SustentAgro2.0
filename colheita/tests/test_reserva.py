"""BL-34 (Gabriel, em dupla com Jimmie): RF-20, RN-01, RN-03, RN-16, UC-09.
Remova o @skip ao implementar colheita.services.reservar_oferta e saldo (depende de BL-24 a BL-26).
"""
from decimal import Decimal
from unittest import skip

from django.core.exceptions import ValidationError
from django.test import TestCase

from core.tests.fabricas import criar_oferta, criar_ong


@skip('Remova ao implementar o BL-34 (depois do BL-26)')
class ReservarOfertaTest(TestCase):
    def setUp(self):
        from colheita.services import reservar_oferta, saldo
        self.reservar, self.saldo = reservar_oferta, saldo
        self.ong = criar_ong()
        self.oferta = criar_oferta(quantidade='100', unidade='kg')

    def test_reserva_parcial_diminui_o_saldo(self):
        reserva = self.reservar(self.oferta, self.ong, Decimal('30'))
        self.assertEqual(reserva.situacao, 'ativa')
        self.assertEqual(self.saldo(self.oferta), Decimal('70'))

    def test_duas_ongs_dividem_a_oferta(self):
        self.reservar(self.oferta, self.ong, Decimal('60'))
        self.reservar(self.oferta, criar_ong(), Decimal('40'))
        self.assertEqual(self.saldo(self.oferta), 0)

    def test_nao_reserva_acima_do_saldo(self):  # RN-03
        self.reservar(self.oferta, self.ong, Decimal('80'))
        with self.assertRaises(ValidationError):
            self.reservar(self.oferta, criar_ong(), Decimal('30'))
        self.assertEqual(self.saldo(self.oferta), Decimal('20'))

    def test_quantidade_precisa_ser_positiva(self):
        with self.assertRaises(ValidationError):
            self.reservar(self.oferta, self.ong, Decimal('0'))

    def test_kg_com_uma_casa_decimal(self):  # RN-16, E-01
        self.reservar(self.oferta, self.ong, Decimal('12.5'))
        self.assertEqual(self.saldo(self.oferta), Decimal('87.5'))

    def test_unidade_nao_aceita_fracao(self):  # RN-16
        oferta = criar_oferta(quantidade='40', unidade='un')
        with self.assertRaises(ValidationError):
            self.reservar(oferta, self.ong, Decimal('2.5'))

    def test_ong_pendente_nao_reserva(self):  # RN-01
        with self.assertRaises(ValidationError):
            self.reservar(self.oferta, criar_ong(situacao='pendente'), Decimal('10'))

    def test_reserva_cancelada_nao_conta_no_saldo(self):
        reserva = self.reservar(self.oferta, self.ong, Decimal('30'))
        reserva.situacao = 'cancelada'
        reserva.save()
        self.assertEqual(self.saldo(self.oferta), Decimal('100'))
