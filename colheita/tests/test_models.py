"""BL-26 (Gabriel, com Jimmie): models Oferta e Reserva, saldo (RN-03), RN-04, RN-13, RN-16, RF-22."""
from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from core.tests.fabricas import criar_ong, criar_oferta


def _reservar(oferta, quantidade, situacao='ativa', **campos):
    from colheita.models import Reserva
    return Reserva.objects.create(oferta=oferta, ong=campos.pop('ong', None) or criar_ong(),
                                  quantidade=Decimal(quantidade), situacao=situacao, **campos)


class SaldoTest(TestCase):
    def test_oferta_sem_reservas_tem_saldo_igual_a_quantidade(self):
        self.assertEqual(criar_oferta(quantidade='100').saldo, Decimal('100'))

    def test_reservas_ativas_e_recebidas_descontam(self):  # RN-03
        oferta = criar_oferta(quantidade='100')
        _reservar(oferta, '30')
        _reservar(oferta, '20', situacao='recebida', quantidade_recebida=Decimal('15'))
        self.assertEqual(oferta.saldo, Decimal('50'))  # a recebida conta pelo reservado

    def test_canceladas_e_nao_recebidas_nao_contam(self):
        oferta = criar_oferta(quantidade='100')
        _reservar(oferta, '30', situacao='cancelada', cancelada_por='ong')
        _reservar(oferta, '20', situacao='nao_recebida', quantidade_recebida=Decimal('0'))
        self.assertEqual(oferta.saldo, Decimal('100'))

    def test_saldo_nunca_fica_negativo(self):
        oferta = criar_oferta(quantidade='10')
        _reservar(oferta, '10')
        _reservar(oferta, '5')  # gravada direto, sem o reservar_oferta (BL-34) para barrar
        self.assertEqual(oferta.saldo, Decimal('0'))


class OfertaTest(TestCase):
    # A fábrica já preenche aberta_a_todas_em; aqui ele é apagado para o save() calcular
    def test_sem_ong_de_destino_abre_a_todas_ao_publicar(self):  # RN-05
        oferta = criar_oferta()
        oferta.aberta_a_todas_em = None
        antes = timezone.now()
        oferta.save()
        self.assertLess(oferta.aberta_a_todas_em - antes, timedelta(minutes=1))

    def test_com_ong_de_destino_abre_a_todas_48h_depois(self):  # RN-04
        oferta = criar_oferta(ong_destino=criar_ong())
        oferta.aberta_a_todas_em = None
        antes = timezone.now()
        oferta.save()
        self.assertGreaterEqual(oferta.aberta_a_todas_em - antes, timedelta(hours=48))

    def test_vencida_depois_do_colher_ate(self):
        oferta = criar_oferta(colher_ate=date.today() - timedelta(days=1))
        self.assertTrue(oferta.vencida)
        self.assertFalse(criar_oferta(colher_ate=date.today()).vencida)

    def test_urgente_aberta_a_todas_ha_mais_de_48h_com_saldo(self):  # RF-22
        oferta = criar_oferta(quantidade='10')
        oferta.aberta_a_todas_em = timezone.now() - timedelta(hours=49)
        self.assertTrue(oferta.urgente)
        _reservar(oferta, '10')
        self.assertFalse(oferta.urgente)  # sem saldo deixa de ser urgente

    def test_recente_nao_e_urgente(self):
        self.assertFalse(criar_oferta().urgente)

    def test_clean_recusa_venda_sem_preco(self):  # RN-13
        oferta = criar_oferta()
        oferta.destino = 'vender'
        with self.assertRaises(ValidationError) as ctx:
            oferta.full_clean()
        self.assertIn('preco_unitario', ctx.exception.message_dict)

    def test_clean_recusa_unidade_fracionada(self):  # RN-16
        oferta = criar_oferta(unidade='un', quantidade='30')
        oferta.quantidade = Decimal('12.5')
        with self.assertRaises(ValidationError):
            oferta.full_clean()

    def test_oferta_antiga_continua_editavel(self):
        oferta = criar_oferta(colher_ate=date.today() - timedelta(days=10))
        oferta.produto = 'Alface americana'
        oferta.full_clean()  # a data no passado só é recusada ao publicar


class ReservaTest(TestCase):
    def test_reserva_em_unidades_nao_aceita_fracao(self):  # RN-16, E-01
        reserva = _reservar(criar_oferta(unidade='un', quantidade='30'), '5')
        reserva.quantidade = Decimal('2.5')
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_reserva_em_kg_aceita_uma_casa(self):
        _reservar(criar_oferta(quantidade='100'), '12.5').full_clean()

    def test_recebida_acima_da_reservada_e_recusada(self):  # E-02
        reserva = _reservar(criar_oferta(), '10')
        reserva.quantidade_recebida = Decimal('11')
        with self.assertRaises(ValidationError) as ctx:
            reserva.full_clean()
        self.assertIn('quantidade_recebida', ctx.exception.message_dict)

    def test_quantidade_zero_e_recusada(self):
        reserva = _reservar(criar_oferta(), '10')
        reserva.quantidade = Decimal('0')
        with self.assertRaises(ValidationError):
            reserva.full_clean()
