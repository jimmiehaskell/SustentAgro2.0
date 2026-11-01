"""BL-29 (Júlia): RN-14, RN-19, RN-20, E-05. Remova o @skip ao implementar (depende de BL-25 e BL-26)."""
from unittest import skip

from django.test import TestCase

from core.tests.fabricas import criar_oferta, criar_ong


class SituacaoOngTest(TestCase):
    def test_aprovar_deixa_a_ong_ativa_e_registra_a_data(self):
        from ongs.services import aprovar_ong
        ong = criar_ong(situacao='pendente')
        aprovar_ong(ong)
        ong.refresh_from_db()
        self.assertEqual(ong.situacao, 'ativa')
        self.assertIsNotNone(ong.aprovada_em)

    def test_reprovar_guarda_o_motivo(self):
        from ongs.services import reprovar_ong
        ong = criar_ong(situacao='pendente')
        reprovar_ong(ong, 'CNPJ de empresa com fins lucrativos.')
        ong.refresh_from_db()
        self.assertEqual(ong.situacao, 'reprovada')
        self.assertIn('CNPJ', ong.motivo_reprovacao)

    def test_desativar_cancela_reservas_ativas_e_devolve_o_saldo(self):
        from colheita.models import Reserva
        from colheita.services import saldo
        from ongs.services import desativar_ong
        ong = criar_ong()
        oferta = criar_oferta(quantidade='100')
        reserva = Reserva.objects.create(oferta=oferta, ong=ong, quantidade=40)
        desativar_ong(ong)
        reserva.refresh_from_db()
        self.assertEqual(reserva.situacao, 'cancelada')
        self.assertEqual(reserva.cancelada_por, 'sistema')
        self.assertEqual(saldo(oferta), 100)
