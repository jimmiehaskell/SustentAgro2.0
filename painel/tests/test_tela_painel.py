"""BL-20 (Pedro): Tela 8 · Painel de impacto em mock. RF-29, RF-30, RF-31."""
from django.test import TestCase
from django.urls import reverse


class TelaPainelTest(TestCase):
    def test_mostra_indicadores_grafico_e_ods(self):
        resposta = self.client.get(reverse('painel:painel'))
        self.assertContains(resposta, '4.380 kg')              # RF-29, no formato brasileiro
        self.assertContains(resposta, 'R$ 3.912,50')
        self.assertContains(resposta, 'id="dados-kg-por-mes"')  # RF-30
        self.assertContains(resposta, 'chart.umd.min.js')
        self.assertContains(resposta, 'das ações confirmadas')  # RF-31
        self.assertNotContains(resposta, 'Tela em construção')

    def test_estado_vazio(self):
        resposta = self.client.get(reverse('painel:painel'), {'vazio': '1'})
        self.assertContains(resposta, 'Ainda não há colheitas recebidas')
        self.assertContains(resposta, 'Sem ações confirmadas ainda.')
        self.assertContains(resposta, 'R$ 0,00')
        self.assertNotContains(resposta, 'chart.umd.min.js')
