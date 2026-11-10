"""BL-33 (Gabriel): lista de ofertas real. RF-19, RF-28, RN-04, RN-05, RN-15, RN-18, RN-22, P-03, E-08."""
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from colheita.choices import SituacaoOferta, SituacaoReserva
from colheita.models import Reserva
from colheita.services import ofertas_da_lista
from core.tests import fabricas


def produtos(ofertas):
    return [oferta.produto for oferta in ofertas]


class VisibilidadeTest(TestCase):
    def setUp(self):
        self.ong = fabricas.criar_ong()
        self.outra_ong = fabricas.criar_ong(localidade='Gama')

    def test_oferta_sem_destino_aparece_para_ong_e_visitante(self):  # RN-05, RF-28
        fabricas.criar_oferta(produto='Alface')
        self.assertEqual(produtos(ofertas_da_lista(ong=self.ong)), ['Alface'])
        self.assertEqual(produtos(ofertas_da_lista()), ['Alface'])

    def test_oferta_direcionada_so_aparece_para_a_ong_de_destino(self):  # RN-04
        fabricas.criar_oferta(produto='Couve', ong_destino=self.ong)
        self.assertEqual(produtos(ofertas_da_lista(ong=self.ong)), ['Couve'])
        self.assertEqual(ofertas_da_lista(ong=self.outra_ong), [])
        self.assertEqual(ofertas_da_lista(), [])

    def test_oferta_cancelada_fica_fora(self):
        fabricas.criar_oferta(situacao=SituacaoOferta.CANCELADA)
        self.assertEqual(ofertas_da_lista(ong=self.ong), [])

    def test_visitante_nao_recebe_distancia(self):  # RF-28
        fabricas.criar_oferta()
        self.assertFalse(hasattr(ofertas_da_lista()[0], 'distancia_km'))


class VencimentoESaldoTest(TestCase):
    def setUp(self):
        self.ong = fabricas.criar_ong()

    def test_oferta_vencida_sai_da_lista(self):  # P-03
        fabricas.criar_oferta(produto='Ontem', colher_ate=date.today() - timedelta(days=1))
        fabricas.criar_oferta(produto='Hoje', colher_ate=date.today())
        self.assertEqual(produtos(ofertas_da_lista(ong=self.ong)), ['Hoje'])
        self.assertEqual(produtos(ofertas_da_lista()), ['Hoje'])

    def test_reserva_nao_recebida_continua_valida_quando_a_oferta_vence(self):  # RN-18
        oferta = fabricas.criar_oferta(quantidade='100', colher_ate=date.today() - timedelta(days=1))
        reserva = Reserva.objects.create(oferta=oferta, ong=self.ong, quantidade=Decimal('40'))
        self.assertEqual(ofertas_da_lista(ong=self.ong), [])
        reserva.refresh_from_db()
        self.assertEqual(reserva.situacao, SituacaoReserva.ATIVA)

    def test_oferta_sem_saldo_sai_da_lista(self):
        oferta = fabricas.criar_oferta(produto='Esgotada', quantidade='100')
        fabricas.criar_oferta(produto='Com saldo', quantidade='100')
        Reserva.objects.create(oferta=oferta, ong=self.ong, quantidade=Decimal('100'))
        self.assertEqual(produtos(ofertas_da_lista(ong=self.ong)), ['Com saldo'])
        self.assertEqual(produtos(ofertas_da_lista()), ['Com saldo'])

    def test_reserva_parcial_mantem_a_oferta_com_o_saldo_restante(self):
        oferta = fabricas.criar_oferta(quantidade='100')
        Reserva.objects.create(oferta=oferta, ong=self.ong, quantidade=Decimal('60'))
        self.assertEqual(ofertas_da_lista(ong=self.ong)[0].saldo, Decimal('40'))


class DistanciaEFiltrosTest(TestCase):
    def setUp(self):
        self.ong = fabricas.criar_ong(localidade='Ceilândia')
        fabricas.criar_oferta(produto='Planaltina', localidade='Planaltina')
        fabricas.criar_oferta(produto='Brazlândia', localidade='Brazlândia')
        fabricas.criar_oferta(produto='Ceilândia', localidade='Ceilândia')

    def test_distancia_em_linha_reta_e_ordem_do_mais_perto(self):  # RN-15
        ofertas = ofertas_da_lista(ong=self.ong)
        self.assertEqual(produtos(ofertas), ['Ceilândia', 'Brazlândia', 'Planaltina'])
        self.assertEqual([o.distancia_km for o in ofertas], [0, 18.8, 53.9])

    def test_ate_30_km(self):  # RF-19
        self.assertEqual(produtos(ofertas_da_lista(ong=self.ong, limite_km=30)), ['Ceilândia', 'Brazlândia'])

    def test_ate_60_km(self):
        self.assertEqual(len(ofertas_da_lista(ong=self.ong, limite_km=60)), 3)

    def test_todas_sem_limite(self):
        self.assertEqual(len(ofertas_da_lista(ong=self.ong, limite_km=None)), 3)


class TelaOfertasTest(TestCase):
    def setUp(self):
        self.ong = fabricas.criar_ong(localidade='Ceilândia')
        fabricas.criar_oferta(produto='Alface crespa', localidade='Brazlândia')
        fabricas.criar_oferta(produto='Tomate', localidade='Planaltina', destino='vender', preco_unitario='2.50')
        fabricas.criar_oferta(produto='Couve secreta', ong_destino=fabricas.criar_ong(localidade='Gama'))
        fabricas.criar_oferta(produto='Banana vencida', colher_ate=date.today() - timedelta(days=1))

    def abrir(self, **params):
        return self.client.get(reverse('colheita:ofertas'), params)

    def test_visitante_ve_so_o_nome_da_localidade(self):  # RF-28, RN-22, E-08
        resposta = self.abrir()
        self.assertContains(resposta, 'Alface crespa')
        self.assertContains(resposta, 'Brazlândia')
        self.assertContains(resposta, 'Cadastrar')
        for escondido in ('Retirada:', ' km', 'Reservar', 'Chácara 12'):
            self.assertNotContains(resposta, escondido)
        self.assertFalse(resposta.context['versao_ong'])

    def test_visitante_nao_ve_direcionada_nem_vencida(self):  # RN-04, P-03
        resposta = self.abrir()
        self.assertNotContains(resposta, 'Couve secreta')
        self.assertNotContains(resposta, 'Banana vencida')

    def test_doador_ve_a_mesma_versao_do_visitante(self):  # RF-28
        self.client.force_login(fabricas.criar_doador().usuario)
        resposta = self.abrir()
        self.assertFalse(resposta.context['versao_ong'])
        self.assertNotContains(resposta, 'Reservar')

    def test_ong_ativa_ve_distancia_retirada_e_reserva(self):  # RF-19, RN-22
        self.client.force_login(self.ong.usuario)
        resposta = self.abrir()
        self.assertTrue(resposta.context['versao_ong'])
        self.assertContains(resposta, 'a partir de Ceilândia')
        self.assertContains(resposta, '18,8 km')
        self.assertContains(resposta, 'Retirada: Chácara 12')
        self.assertContains(resposta, 'Venda · R$ 2,50/kg')
        self.assertContains(resposta, 'A ONG busca')
        self.assertContains(resposta, 'Reservar')
        self.assertNotContains(resposta, 'Couve secreta')
        self.assertNotContains(resposta, 'Banana vencida')

    def test_filtros_de_km_da_ong(self):  # RF-19
        self.client.force_login(self.ong.usuario)
        ate_30 = self.abrir(dist='30')
        self.assertContains(ate_30, 'Alface crespa')
        self.assertNotContains(ate_30, 'Tomate')
        self.assertContains(self.abrir(dist='60'), 'Tomate')
        self.assertContains(self.abrir(dist='todas'), 'Tomate')
        self.assertContains(self.abrir(dist='qualquer'), 'Tomate')

    def test_ong_de_destino_ve_a_oferta_direcionada(self):  # RN-04
        gama = fabricas.criar_ong(localidade='Gama')
        fabricas.criar_oferta(produto='Couve da Gama', ong_destino=gama)
        self.client.force_login(gama.usuario)
        self.assertContains(self.abrir(), 'Couve da Gama')

    def test_ong_pendente_nao_ve_ofertas(self):  # E-06
        pendente = fabricas.criar_ong(situacao='pendente')
        self.client.force_login(pendente.usuario)
        resposta = self.abrir()
        self.assertContains(resposta, 'As ofertas aparecem depois da aprovação')
        self.assertNotContains(resposta, 'Alface crespa')
