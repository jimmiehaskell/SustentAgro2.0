"""BL-46 (Gabriel): oferta direcionada e selo urgente. RF-21, RF-22, RN-04, RN-05, RN-06, P-05."""
from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from colheita.models import Reserva
from colheita.services import ofertas_da_lista, reservar_oferta
from core.tests import fabricas


def produtos(ofertas):
    return [oferta.produto for oferta in ofertas]


def ha(horas):
    return timezone.now() - timedelta(hours=horas)


class VisibilidadeDaDirecionadaTest(TestCase):  # RN-04
    def setUp(self):
        self.destino = fabricas.criar_ong()
        self.outra = fabricas.criar_ong(localidade='Gama')

    def test_nas_primeiras_48h_so_a_ong_de_destino_ve(self):
        fabricas.criar_oferta(produto='Couve', ong_destino=self.destino, aberta_a_todas_em=ha(-1))
        self.assertEqual(produtos(ofertas_da_lista(ong=self.destino)), ['Couve'])
        self.assertEqual(ofertas_da_lista(ong=self.outra), [])
        self.assertEqual(ofertas_da_lista(), [])

    def test_depois_de_48h_todos_veem(self):
        fabricas.criar_oferta(produto='Couve', ong_destino=self.destino, aberta_a_todas_em=ha(1))
        for ong in (self.destino, self.outra, None):
            with self.subTest(ong=ong):
                self.assertEqual(produtos(ofertas_da_lista(ong=ong)), ['Couve'])

    def test_oferta_publicada_com_destino_abre_a_todas_48h_depois(self):
        oferta = fabricas.criar_oferta(ong_destino=self.destino)
        self.assertAlmostEqual(oferta.aberta_a_todas_em, timezone.now() + timedelta(hours=48),
                               delta=timedelta(minutes=1))
        self.assertTrue(oferta.so_da_ong_destino)

    def test_sem_destino_aparece_desde_a_publicacao(self):  # RN-05
        fabricas.criar_oferta(produto='Alface')
        for ong in (self.destino, self.outra, None):
            with self.subTest(ong=ong):
                self.assertEqual(produtos(ofertas_da_lista(ong=ong)), ['Alface'])


class UrgenteTest(TestCase):  # RN-06, RF-22, P-05
    def setUp(self):
        self.ong = fabricas.criar_ong()

    def test_aberta_a_todas_ha_mais_de_48h_com_saldo_e_urgente(self):
        antiga = fabricas.criar_oferta(aberta_a_todas_em=ha(49))
        recente = fabricas.criar_oferta(aberta_a_todas_em=ha(47))
        self.assertTrue(antiga.urgente)
        self.assertFalse(recente.urgente)

    def test_sem_saldo_nao_e_urgente(self):
        oferta = fabricas.criar_oferta(quantidade='10', aberta_a_todas_em=ha(49))
        Reserva.objects.create(oferta=oferta, ong=self.ong, quantidade=Decimal('10'))
        self.assertFalse(oferta.urgente)

    def test_com_saldo_parcial_continua_urgente(self):
        oferta = fabricas.criar_oferta(quantidade='10', aberta_a_todas_em=ha(49))
        Reserva.objects.create(oferta=oferta, ong=self.ong, quantidade=Decimal('4'))
        self.assertTrue(oferta.urgente)

    def test_direcionada_conta_as_48h_da_abertura_a_todas(self):  # P-05
        outra = fabricas.criar_ong(localidade='Gama')
        publicada_ha_49h = fabricas.criar_oferta(ong_destino=outra, aberta_a_todas_em=ha(1))
        publicada_ha_97h = fabricas.criar_oferta(ong_destino=outra, aberta_a_todas_em=ha(49))
        self.assertFalse(publicada_ha_49h.urgente)
        self.assertTrue(publicada_ha_97h.urgente)

    def test_direcionada_ainda_exclusiva_nao_e_urgente(self):
        self.assertFalse(fabricas.criar_oferta(ong_destino=self.ong).urgente)


class OrdemDaListaTest(TestCase):  # RF-22
    def test_exclusivas_da_ong_depois_urgentes_depois_por_distancia(self):
        ong = fabricas.criar_ong(localidade='Ceilândia')
        fabricas.criar_oferta(produto='Perto', localidade='Ceilândia')
        fabricas.criar_oferta(produto='Urgente longe', localidade='Planaltina', aberta_a_todas_em=ha(49))
        fabricas.criar_oferta(produto='Urgente perto', localidade='Brazlândia', aberta_a_todas_em=ha(49))
        fabricas.criar_oferta(produto='Para mim', localidade='Planaltina', ong_destino=ong)
        fabricas.criar_oferta(produto='Meio', localidade='Brazlândia')
        self.assertEqual(produtos(ofertas_da_lista(ong=ong)),
                         ['Para mim', 'Urgente perto', 'Urgente longe', 'Perto', 'Meio'])

    def test_direcionada_depois_das_48h_entra_na_ordem_comum(self):
        ong = fabricas.criar_ong(localidade='Ceilândia')
        fabricas.criar_oferta(produto='Perto', localidade='Ceilândia')
        fabricas.criar_oferta(produto='Aberta', localidade='Planaltina', ong_destino=ong, aberta_a_todas_em=ha(1))
        self.assertEqual(produtos(ofertas_da_lista(ong=ong)), ['Perto', 'Aberta'])


class TelaDaListaTest(TestCase):
    def setUp(self):
        self.ong = fabricas.criar_ong()
        self.url = reverse('colheita:ofertas')

    def test_selo_para_a_sua_ong_so_na_janela_de_48h(self):
        fabricas.criar_oferta(produto='Couve exclusiva', ong_destino=self.ong)
        fabricas.criar_oferta(produto='Couve aberta', ong_destino=self.ong, aberta_a_todas_em=ha(1))
        self.client.force_login(self.ong.usuario)
        html = self.client.get(self.url).content.decode()
        self.assertEqual(html.count('Para a sua ONG'), 1)
        self.assertNotIn('abre a todas em 0', html)
        self.assertIn('Couve aberta', html)

    def test_selo_urgente_so_para_ong_e_so_com_mais_de_48h(self):
        fabricas.criar_oferta(produto='Alface velha', aberta_a_todas_em=ha(49))
        fabricas.criar_oferta(produto='Alface nova')
        self.client.force_login(self.ong.usuario)
        html = self.client.get(self.url).content.decode()
        self.assertEqual(html.count('>Urgente<'), 1)
        self.client.logout()
        self.assertNotIn('Urgente', self.client.get(self.url).content.decode())

    def test_visitante_ve_a_direcionada_depois_das_48h(self):
        fabricas.criar_oferta(produto='Couve aberta', ong_destino=self.ong, aberta_a_todas_em=ha(1))
        fabricas.criar_oferta(produto='Couve exclusiva', ong_destino=self.ong)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, 'Couve aberta')
        self.assertNotContains(resposta, 'Couve exclusiva')


class ReservaDaDirecionadaTest(TestCase):
    def setUp(self):
        self.destino = fabricas.criar_ong()
        self.outra = fabricas.criar_ong(localidade='Gama')

    def reservar_pela_tela(self, oferta, ong):
        self.client.force_login(ong.usuario)
        url = reverse('colheita:reservar', kwargs={'pk': oferta.pk})
        return self.client.post(url, {'quantidade': '5'})

    def test_outra_ong_nao_reserva_nas_primeiras_48h(self):  # RN-04
        oferta = fabricas.criar_oferta(ong_destino=self.destino)
        self.assertEqual(self.reservar_pela_tela(oferta, self.outra).status_code, 404)
        with self.assertRaisesMessage(ValidationError, 'primeiras 48 h'):
            reservar_oferta(oferta, self.outra, Decimal('5'))
        self.assertEqual(Reserva.objects.count(), 0)

    def test_ong_de_destino_reserva_nas_primeiras_48h(self):
        oferta = fabricas.criar_oferta(ong_destino=self.destino)
        self.assertEqual(self.reservar_pela_tela(oferta, self.destino).status_code, 302)
        self.assertEqual(Reserva.objects.filter(ong=self.destino).count(), 1)

    def test_outra_ong_reserva_depois_das_48h(self):
        oferta = fabricas.criar_oferta(ong_destino=self.destino, aberta_a_todas_em=ha(1))
        self.assertEqual(self.reservar_pela_tela(oferta, self.outra).status_code, 302)
        self.assertEqual(Reserva.objects.filter(ong=self.outra).count(), 1)
