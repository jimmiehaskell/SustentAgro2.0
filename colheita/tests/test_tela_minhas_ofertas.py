"""BL-21 (Pedro): Tela 13 · Minhas ofertas do agricultor em mock. RF-25, RF-27."""
from django.test import TestCase
from django.urls import reverse


class TelaMinhasOfertasTest(TestCase):
    def setUp(self):
        self.resposta = self.client.get(reverse('colheita:minhas_ofertas'))

    def test_mostra_ofertas_com_saldo_e_situacao(self):  # RF-25
        self.assertContains(self.resposta, 'Alface crespa')
        self.assertContains(self.resposta, 'Aberta · urgente')
        self.assertContains(self.resposta, 'Só para Sol Nascente')
        self.assertContains(self.resposta, 'Vencida em 10/10')
        self.assertNotContains(self.resposta, 'Tela em construção')

    def test_reserva_mostra_o_contato_da_ong(self):  # RF-27
        self.assertContains(self.resposta, 'Reserva ativa · 15 un')
        self.assertContains(self.resposta, '(61) 3371-0045')
        self.assertContains(self.resposta, 'contato@solnascente.org.br')
        self.assertContains(self.resposta, 'Nenhuma reserva ainda.')
